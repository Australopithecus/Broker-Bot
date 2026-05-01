from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd
from alpaca.data.enums import MarketType, MostActivesBy
from alpaca.data.historical import NewsClient, ScreenerClient, StockHistoricalDataClient
from alpaca.data.requests import MarketMoversRequest, MostActivesRequest, NewsRequest, StockSnapshotRequest

from .config import Config, get_bot_account_config
from .llm_utils import call_json_llm
from .overlay_learning import apply_component_scales, load_component_scales


POSITIVE_NEWS_WORDS = {
    "beat",
    "beats",
    "bullish",
    "buyback",
    "growth",
    "profit",
    "profits",
    "strong",
    "stronger",
    "surge",
    "surges",
    "record",
    "approval",
    "approved",
    "upgrade",
    "outperform",
    "partnership",
    "raises",
    "raised",
}

NEGATIVE_NEWS_WORDS = {
    "cuts",
    "cut",
    "decline",
    "declines",
    "delay",
    "delays",
    "downgrade",
    "downgraded",
    "fraud",
    "lawsuit",
    "miss",
    "misses",
    "probe",
    "recall",
    "warning",
    "weak",
    "weaker",
    "missed",
}

TECHNICAL_MAX_ADJ = 0.0025
SNAPSHOT_MAX_ADJ = 0.0016
SCREENER_MAX_ADJ = 0.0016
NEWS_MAX_ADJ = 0.0022
MEMORY_MAX_ADJ = 0.0018
LLM_MAX_ADJ = 0.0025


@dataclass
class ResearchContext:
    candidate_symbols: list[str] = field(default_factory=list)
    movers_up: list[str] = field(default_factory=list)
    movers_down: list[str] = field(default_factory=list)
    most_active: list[str] = field(default_factory=list)
    snapshot_scores: dict[str, float] = field(default_factory=dict)
    news_scores: dict[str, float] = field(default_factory=dict)
    news_headlines: dict[str, list[str]] = field(default_factory=dict)
    llm_scores: dict[str, float] = field(default_factory=dict)
    llm_rationales: dict[str, str] = field(default_factory=dict)
    component_scales: dict[str, float] = field(default_factory=dict)
    llm_summary: str = ""
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_symbols": self.candidate_symbols,
            "movers_up": self.movers_up,
            "movers_down": self.movers_down,
            "most_active": self.most_active,
            "snapshot_scores": self.snapshot_scores,
            "news_scores": self.news_scores,
            "news_headlines": self.news_headlines,
            "llm_scores": self.llm_scores,
            "llm_rationales": self.llm_rationales,
            "component_scales": self.component_scales,
            "llm_summary": self.llm_summary,
            "notes": self.notes,
        }


def _clip(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _rank_signal(series: pd.Series, ascending: bool = True) -> pd.Series:
    if series.empty:
        return pd.Series(dtype=float)
    filled = series.astype(float).replace([float("inf"), float("-inf")], pd.NA)
    median = float(filled.dropna().median()) if not filled.dropna().empty else 0.0
    filled = filled.fillna(median)
    ranked = filled.rank(pct=True, ascending=ascending)
    return (ranked * 2.0) - 1.0


def _candidate_symbols(latest: pd.DataFrame, limit: int) -> list[str]:
    if latest.empty:
        return []
    half = max(limit // 2, 1)
    longs = latest.sort_values("pred_return", ascending=False)["Symbol"].head(half).tolist()
    shorts = latest.sort_values("pred_return", ascending=True)["Symbol"].head(half).tolist()
    ordered = []
    for symbol in longs + shorts:
        if symbol not in ordered:
            ordered.append(symbol)
    return ordered[:limit]


def _score_headlines(headlines: list[str]) -> float:
    if not headlines:
        return 0.0
    score = 0.0
    for headline in headlines:
        lower = headline.lower()
        score += sum(1 for word in POSITIVE_NEWS_WORDS if word in lower)
        score -= sum(1 for word in NEGATIVE_NEWS_WORDS if word in lower)
    scale = max(len(headlines), 1) * 2.0
    return _clip(score / scale, -1.0, 1.0)


def _safe_bar_value(snapshot: Any, bar_name: str, field_name: str) -> float | None:
    bar = getattr(snapshot, bar_name, None)
    value = getattr(bar, field_name, None)
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _snapshot_signal(snapshot: Any) -> float:
    daily_close = _safe_bar_value(snapshot, "daily_bar", "close")
    prev_close = _safe_bar_value(snapshot, "previous_daily_bar", "close")
    minute_close = _safe_bar_value(snapshot, "minute_bar", "close")
    minute_volume = _safe_bar_value(snapshot, "minute_bar", "volume")
    daily_volume = _safe_bar_value(snapshot, "daily_bar", "volume")

    daily_move = 0.0
    if daily_close and prev_close and prev_close > 0:
        daily_move = (daily_close / prev_close) - 1.0

    minute_strength = 0.0
    if minute_close and daily_close and daily_close > 0:
        minute_strength = (minute_close / daily_close) - 1.0

    volume_signal = 0.0
    if minute_volume and daily_volume and daily_volume > 0:
        volume_signal = _clip((minute_volume / daily_volume) * 20.0, 0.0, 1.0)

    raw = (daily_move * 8.0) + (minute_strength * 12.0) + (volume_signal * 0.15)
    return _clip(raw, -1.0, 1.0)


def _fetch_screener_context(config: Config, context: ResearchContext, bot_name: str = "ml") -> None:
    account = get_bot_account_config(config, bot_name)
    try:
        client = ScreenerClient(account.api_key, account.secret_key)
        movers = client.get_market_movers(MarketMoversRequest(top=10, market_type=MarketType.STOCKS))
        actives = client.get_most_actives(MostActivesRequest(top=10, by=MostActivesBy.VOLUME))
    except Exception as exc:
        context.notes.append(f"Screener unavailable: {exc}")
        return

    context.movers_up = [item.symbol for item in getattr(movers, "gainers", []) or []]
    context.movers_down = [item.symbol for item in getattr(movers, "losers", []) or []]
    context.most_active = [item.symbol for item in getattr(actives, "most_actives", []) or []]


def _fetch_snapshot_context(config: Config, context: ResearchContext, bot_name: str = "ml") -> None:
    if not context.candidate_symbols:
        return
    account = get_bot_account_config(config, bot_name)
    try:
        client = StockHistoricalDataClient(account.api_key, account.secret_key)
        snapshots = client.get_stock_snapshot(
            StockSnapshotRequest(
                symbol_or_symbols=context.candidate_symbols,
                feed=account.data_feed,
            )
        )
    except Exception as exc:
        context.notes.append(f"Snapshots unavailable: {exc}")
        return

    if not isinstance(snapshots, dict):
        return
    for symbol, snapshot in snapshots.items():
        context.snapshot_scores[symbol] = _snapshot_signal(snapshot)


def _fetch_news_context(config: Config, context: ResearchContext, bot_name: str = "ml") -> None:
    if not context.candidate_symbols:
        return
    account = get_bot_account_config(config, bot_name)
    try:
        client = NewsClient(account.api_key, account.secret_key)
        request = NewsRequest(
            symbols=",".join(context.candidate_symbols),
            start=datetime.now(timezone.utc) - timedelta(days=config.news_lookback_days),
            end=datetime.now(timezone.utc),
            limit=50,
            include_content=False,
            exclude_contentless=True,
        )
        news = client.get_news(request)
    except Exception as exc:
        context.notes.append(f"News unavailable: {exc}")
        return

    for item in getattr(news, "data", []) or []:
        headline = (getattr(item, "headline", None) or "").strip()
        if not headline:
            continue
        for symbol in getattr(item, "symbols", []) or []:
            if symbol not in context.candidate_symbols:
                continue
            context.news_headlines.setdefault(symbol, []).append(headline)

    for symbol, headlines in context.news_headlines.items():
        context.news_headlines[symbol] = headlines[:3]
        context.news_scores[symbol] = _score_headlines(headlines[:3])


def _fetch_llm_overlay(
    config: Config,
    latest: pd.DataFrame,
    context: ResearchContext,
    symbol_memory: dict[str, float],
) -> None:
    if not config.llm_enabled or latest.empty or not context.candidate_symbols:
        return

    short_list = latest[latest["Symbol"].isin(context.candidate_symbols)].copy()
    if short_list.empty:
        return

    payload = {
        "objective": "Select paper-trading stocks to watch and provide modest return adjustments.",
        "constraints": {
            "max_adjustment_abs": LLM_MAX_ADJ,
            "only_symbols": context.candidate_symbols,
            "paper_trading": True,
            "style": "aggressive but explainable",
        },
        "market_context": {
            "movers_up": context.movers_up,
            "movers_down": context.movers_down,
            "most_active": context.most_active,
        },
        "candidates": [
            {
                "symbol": row["Symbol"],
                "pred_return": round(float(row["pred_return"]), 6),
                "mom_20d": round(float(row["mom_20d"]), 6),
                "return_5d": round(float(row["return_5d"]), 6),
                "vol_20d": round(float(row["vol_20d"]), 6),
                "memory_score": round(float(symbol_memory.get(row["Symbol"], 0.0)), 4),
                "news_headlines": context.news_headlines.get(row["Symbol"], [])[:2],
                "snapshot_score": round(float(context.snapshot_scores.get(row["Symbol"], 0.0)), 4),
            }
            for _, row in short_list.sort_values("pred_return", ascending=False).iterrows()
        ],
    }

    response = call_json_llm(
        config,
        system_prompt=(
            "You are an explainable stock-selection assistant for a paper-trading bot. "
            "Return only JSON with keys: summary (string), adjustments (array). "
            "Each adjustments item must include symbol, adjustment, and reason. "
            "Adjustment must be a small numeric return delta within the allowed bound."
        ),
        payload=payload,
        max_output_tokens=700,
    )
    if not response:
        return

    summary = response.get("summary")
    if isinstance(summary, str):
        context.llm_summary = summary.strip()

    adjustments = response.get("adjustments") or []
    if not isinstance(adjustments, list):
        return

    allowed = set(context.candidate_symbols)
    for item in adjustments:
        if not isinstance(item, dict):
            continue
        symbol = str(item.get("symbol", "")).strip().upper()
        if symbol not in allowed:
            continue
        try:
            raw_adjustment = float(item.get("adjustment", 0.0))
        except Exception:
            continue
        context.llm_scores[symbol] = _clip(raw_adjustment / max(LLM_MAX_ADJ, 1e-9), -1.0, 1.0)
        reason = item.get("reason")
        if isinstance(reason, str) and reason.strip():
            context.llm_rationales[symbol] = reason.strip()


def build_research_overlay(
    config: Config,
    latest: pd.DataFrame,
    symbol_memory: dict[str, float] | None = None,
    bot_name: str = "ml",
) -> tuple[pd.DataFrame, ResearchContext]:
    symbol_memory = symbol_memory or {}
    overlay = latest.copy()
    if overlay.empty:
        return overlay, ResearchContext()

    overlay["base_pred_return"] = overlay["pred_return"].astype(float)

    mom_signal = _rank_signal(overlay["mom_20d"], ascending=True)
    short_signal = _rank_signal(overlay["return_5d"], ascending=True)
    rank_signal = (overlay["rank_mom_20d"].astype(float) * 2.0) - 1.0
    vol_signal = -_rank_signal(overlay["vol_20d"], ascending=True)

    technical_raw = (0.40 * mom_signal) + (0.20 * short_signal) + (0.25 * rank_signal) + (0.15 * vol_signal)
    overlay["technical_adjustment"] = technical_raw * TECHNICAL_MAX_ADJ * config.technical_weight

    component_scales = load_component_scales(config.learned_policy_path)
    context = ResearchContext(
        candidate_symbols=_candidate_symbols(overlay, config.research_candidate_limit),
        component_scales=component_scales,
    )
    _fetch_screener_context(config, context, bot_name=bot_name)
    _fetch_snapshot_context(config, context, bot_name=bot_name)
    _fetch_news_context(config, context, bot_name=bot_name)
    _fetch_llm_overlay(config, overlay, context, symbol_memory)

    screener_raw: list[float] = []
    for symbol in overlay["Symbol"]:
        score = 0.0
        if symbol in context.movers_up:
            score += 1.0
        if symbol in context.movers_down:
            score -= 1.0
        if symbol in context.most_active:
            score += 0.35 if score >= 0 else -0.35
        screener_raw.append(_clip(score, -1.0, 1.0))

    overlay["snapshot_adjustment"] = (
        overlay["Symbol"].map(context.snapshot_scores).fillna(0.0).astype(float) * SNAPSHOT_MAX_ADJ * config.snapshot_weight
    )
    overlay["screener_adjustment"] = pd.Series(screener_raw, index=overlay.index) * SCREENER_MAX_ADJ * config.screener_weight
    overlay["news_adjustment"] = (
        overlay["Symbol"].map(context.news_scores).fillna(0.0).astype(float) * NEWS_MAX_ADJ * config.news_weight
    )
    overlay["memory_adjustment"] = (
        overlay["Symbol"].map(symbol_memory).fillna(0.0).astype(float) * MEMORY_MAX_ADJ * config.memory_weight
    )
    overlay["llm_adjustment"] = (
        overlay["Symbol"].map(context.llm_scores).fillna(0.0).astype(float) * LLM_MAX_ADJ * config.llm_weight
    )

    overlay = apply_component_scales(overlay, component_scales)

    rationales: list[str] = []
    for _, row in overlay.iterrows():
        parts: list[str] = []
        symbol = row["Symbol"]
        if abs(float(row["technical_adjustment"])) >= 0.0005:
            parts.append(f"tech {float(row['technical_adjustment']):+.4f}")
        if abs(float(row["snapshot_adjustment"])) >= 0.0004:
            parts.append(f"snapshot {float(row['snapshot_adjustment']):+.4f}")
        if abs(float(row["screener_adjustment"])) >= 0.0004:
            parts.append(f"screener {float(row['screener_adjustment']):+.4f}")
        if abs(float(row["news_adjustment"])) >= 0.0004:
            headline = context.news_headlines.get(symbol, [""])[0]
            if headline:
                parts.append(f"news {float(row['news_adjustment']):+.4f} ({headline[:70]})")
            else:
                parts.append(f"news {float(row['news_adjustment']):+.4f}")
        if abs(float(row["memory_adjustment"])) >= 0.0003:
            parts.append(f"memory {float(row['memory_adjustment']):+.4f}")
        if abs(float(row["llm_adjustment"])) >= 0.0004:
            llm_reason = context.llm_rationales.get(symbol)
            if llm_reason:
                parts.append(f"llm {float(row['llm_adjustment']):+.4f} ({llm_reason[:70]})")
            else:
                parts.append(f"llm {float(row['llm_adjustment']):+.4f}")
        rationales.append("; ".join(parts[:4]))

    overlay["rationale"] = rationales
    return overlay, context
