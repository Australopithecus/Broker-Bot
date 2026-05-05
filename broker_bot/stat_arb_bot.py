from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from .bots import STAT_ARB_BOT_NAME, bot_label
from .config import Config
from .data import fetch_daily_bars
from .risk import classify_market_regime, load_sector_map
from .trader import OrderLogRow, Signal, execute_signals


@dataclass
class StatArbRunResult:
    ts: str
    orders: list[OrderLogRow]
    signals: list[Signal]
    decision_context: dict
    report: dict


def _liquid_symbols(bars: pd.DataFrame, config: Config) -> list[str]:
    df = bars[bars["Symbol"] != "SPY"].copy()
    if df.empty:
        return []
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df["volume"] = pd.to_numeric(df.get("volume", 0.0), errors="coerce").fillna(0.0)
    df["dollar_vol"] = df["close"] * df["volume"]
    ordered = df.sort_values("timestamp")
    latest = ordered.groupby("Symbol").tail(1).set_index("Symbol")
    recent = ordered.groupby("Symbol").tail(20)
    avg_dollar_vol = recent.groupby("Symbol")["dollar_vol"].mean()

    eligible = []
    for symbol, row in latest.iterrows():
        price = float(row.get("close") or 0.0)
        dollar_vol = float(avg_dollar_vol.get(symbol, 0.0) or 0.0)
        if config.min_price > 0 and price < config.min_price:
            continue
        if config.min_dollar_vol > 0 and dollar_vol < config.min_dollar_vol:
            continue
        eligible.append((symbol, dollar_vol))

    eligible.sort(key=lambda item: item[1], reverse=True)
    limit = max(int(config.stat_arb_symbol_limit), 2)
    return [symbol for symbol, _ in eligible[:limit]]


def _pair_grid(symbols: list[str], sector_map: dict[str, str]) -> list[tuple[str, str]]:
    if len(symbols) < 2:
        return []

    grouped: dict[str, list[str]] = {}
    for symbol in symbols:
        sector = sector_map.get(symbol, "Unknown") if sector_map else "All"
        grouped.setdefault(sector, []).append(symbol)

    pairs: list[tuple[str, str]] = []
    for group_symbols in grouped.values():
        ordered = sorted(group_symbols)
        if len(ordered) < 2:
            continue
        pairs.extend((ordered[i], ordered[j]) for i in range(len(ordered)) for j in range(i + 1, len(ordered)))

    if pairs:
        return pairs

    ordered = sorted(symbols)
    return [(ordered[i], ordered[j]) for i in range(len(ordered)) for j in range(i + 1, len(ordered))]


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        result = float(value)
    except Exception:
        return default
    return result if math.isfinite(result) else default


def _evaluate_pairs(
    closes: pd.DataFrame,
    symbols: list[str],
    sector_map: dict[str, str],
    config: Config,
) -> list[dict]:
    returns = closes.pct_change().dropna(how="all")
    log_prices = closes.apply(pd.to_numeric, errors="coerce").where(lambda frame: frame > 0).map(math.log)
    candidates: list[dict] = []
    min_obs = min(max(60, int(config.stat_arb_lookback_days * 0.4)), max(60, len(closes) // 2))

    for left, right in _pair_grid(symbols, sector_map):
        pair_returns = returns[[left, right]].dropna()
        pair_logs = log_prices[[left, right]].dropna()
        if len(pair_returns) < min_obs or len(pair_logs) < min_obs:
            continue

        corr = _safe_float(pair_returns[left].corr(pair_returns[right]))
        if corr < config.stat_arb_min_correlation:
            continue

        right_var = _safe_float(pair_logs[right].var())
        if right_var <= 0:
            continue
        hedge_beta = _safe_float(pair_logs[left].cov(pair_logs[right]) / right_var, 1.0)
        hedge_beta = max(0.25, min(hedge_beta, 4.0))
        spread = pair_logs[left] - hedge_beta * pair_logs[right]
        spread_std = _safe_float(spread.std())
        if spread_std <= 0:
            continue
        spread_mean = _safe_float(spread.mean())
        latest_spread = _safe_float(spread.iloc[-1])
        z_score = (latest_spread - spread_mean) / spread_std
        if not math.isfinite(z_score):
            continue

        candidates.append(
            {
                "left": left,
                "right": right,
                "sector": sector_map.get(left) if sector_map.get(left) == sector_map.get(right) else "Cross-sector",
                "correlation": corr,
                "hedge_beta": hedge_beta,
                "z_score": float(z_score),
                "abs_z": abs(float(z_score)),
                "spread_std": spread_std,
                "latest_spread": latest_spread,
                "mean_spread": spread_mean,
            }
        )

    candidates.sort(key=lambda row: (row["abs_z"], row["correlation"]), reverse=True)
    return candidates


def _signals_from_pairs(candidates: list[dict], closes: pd.DataFrame, config: Config) -> tuple[list[Signal], list[dict]]:
    vol = closes.pct_change().rolling(20).std().iloc[-1].to_dict()
    selected_pairs: list[dict] = []
    signals: list[Signal] = []
    used_symbols: set[str] = set()

    for pair in candidates:
        if len(selected_pairs) >= max(config.stat_arb_max_pairs, 0):
            break
        if pair["abs_z"] < config.stat_arb_entry_z:
            continue
        left = str(pair["left"])
        right = str(pair["right"])
        if left in used_symbols or right in used_symbols:
            continue

        z_score = float(pair["z_score"])
        expected_reversion = max((abs(z_score) - config.stat_arb_exit_z) * float(pair["spread_std"]), 0.0)
        expected_reversion = max(expected_reversion, config.min_signal_abs_score * 1.25)
        expected_reversion = min(expected_reversion, 0.12)
        if z_score > 0:
            rich_symbol, cheap_symbol = left, right
        else:
            rich_symbol, cheap_symbol = right, left

        pair_summary = dict(pair)
        pair_summary["rich_symbol"] = rich_symbol
        pair_summary["cheap_symbol"] = cheap_symbol
        selected_pairs.append(pair_summary)
        used_symbols.update({left, right})

        base_components = {
            "stat_arb_z_score": z_score,
            "stat_arb_abs_z": float(pair["abs_z"]),
            "stat_arb_correlation": float(pair["correlation"]),
            "stat_arb_hedge_beta": float(pair["hedge_beta"]),
            "stat_arb_expected_reversion": float(expected_reversion),
        }
        rationale = (
            f"Pair {left}/{right} spread z-score {z_score:+.2f} with correlation "
            f"{float(pair['correlation']):.2f}; trade expects mean reversion toward the historical spread."
        )
        signals.append(
            Signal(
                symbol=cheap_symbol,
                score=float(expected_reversion),
                side="LONG",
                vol=_safe_float(vol.get(cheap_symbol), 0.02),
                base_score=float(expected_reversion),
                selected=True,
                components=base_components,
                rationale=f"{rationale} Long the relatively cheap leg.",
            )
        )
        signals.append(
            Signal(
                symbol=rich_symbol,
                score=-float(expected_reversion),
                side="SHORT",
                vol=_safe_float(vol.get(rich_symbol), 0.02),
                base_score=-float(expected_reversion),
                selected=True,
                components=base_components,
                rationale=f"{rationale} Short the relatively rich leg.",
            )
        )

    return signals, selected_pairs


def _report_for_run(ts: str, candidates: list[dict], selected_pairs: list[dict], context: dict, config: Config) -> dict:
    headline = f"{bot_label(STAT_ARB_BOT_NAME)} Mean-Reversion Report"
    if selected_pairs:
        summary = (
            f"Selected {len(selected_pairs)} stretched pair(s) from {context.get('candidate_pair_count', 0)} "
            "eligible relationship candidates."
        )
    else:
        summary = (
            f"No pair spread exceeded the entry threshold of {config.stat_arb_entry_z:.2f} z-score; "
            "the bot should hold or flatten until a clearer dislocation appears."
        )

    selected_lines = [
        (
            f"- {row['left']}/{row['right']}: z={row['z_score']:+.2f}, corr={row['correlation']:.2f}, "
            f"long {row['cheap_symbol']} / short {row['rich_symbol']}."
        )
        for row in selected_pairs
    ]
    watch_lines = [
        f"- {row['left']}/{row['right']}: z={row['z_score']:+.2f}, corr={row['correlation']:.2f}."
        for row in candidates[:8]
    ]
    body = "\n".join(
        [
            f"# {headline}",
            "",
            summary,
            "",
            "## Selected dislocations",
            "\n".join(selected_lines) if selected_lines else "- None.",
            "",
            "## Closest relationship candidates",
            "\n".join(watch_lines) if watch_lines else "- Not enough correlated pairs passed liquidity/history filters.",
            "",
            "## Guardrails",
            f"- Entry threshold: {config.stat_arb_entry_z:.2f} z-score.",
            f"- Exit/neutral zone: {config.stat_arb_exit_z:.2f} z-score.",
            f"- Minimum return correlation: {config.stat_arb_min_correlation:.2f}.",
            f"- Maximum selected pairs: {config.stat_arb_max_pairs}.",
            "- This strategy is relationship-based and does not use supervised return prediction or LLM trade selection.",
        ]
    )
    reports_dir = Path(config.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"stat_arb_daily_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(body, encoding="utf-8")
    return {
        "ts": ts,
        "report_type": "stat_arb_daily",
        "headline": headline,
        "summary": summary,
        "body": body,
        "metrics": {
            "candidate_pair_count": float(context.get("candidate_pair_count", 0)),
            "selected_pair_count": float(len(selected_pairs)),
            "entry_z": float(config.stat_arb_entry_z),
            "min_correlation": float(config.stat_arb_min_correlation),
        },
        "changes": {},
        "report_path": str(report_path),
    }


def rebalance_stat_arb_bot(config: Config, symbols: list[str]) -> StatArbRunResult:
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=max(config.stat_arb_lookback_days, 90) + 20)
    universe = list(dict.fromkeys([symbol for symbol in symbols if symbol != "SPY"]))
    bars = fetch_daily_bars(config, universe + ["SPY"], start, end, bot_name=STAT_ARB_BOT_NAME).bars
    sector_map = load_sector_map(config.sector_map_path)
    liquid_symbols = _liquid_symbols(bars, config)
    if len(liquid_symbols) < 2:
        raise RuntimeError("Not enough liquid symbols to evaluate stat-arb pairs.")

    closes = (
        bars[bars["Symbol"].isin(liquid_symbols)]
        .pivot_table(index="timestamp", columns="Symbol", values="close")
        .sort_index()
        .tail(max(config.stat_arb_lookback_days, 90))
    )
    closes = closes.dropna(axis=1, thresh=max(60, int(len(closes) * 0.75))).ffill().dropna(axis=1)
    liquid_symbols = [symbol for symbol in liquid_symbols if symbol in closes.columns]
    candidates = _evaluate_pairs(closes, liquid_symbols, sector_map, config)
    signals, selected_pairs = _signals_from_pairs(candidates, closes, config)
    latest = (
        bars[bars["Symbol"].isin(liquid_symbols)]
        .sort_values("timestamp")
        .groupby("Symbol")
        .tail(1)[["Symbol", "close"]]
        .copy()
    )

    spy_df = bars[bars["Symbol"] == "SPY"]
    regime = classify_market_regime(
        spy_df,
        gross_leverage=config.gross_leverage,
        bear_leverage=config.bear_leverage,
        vol_target=config.vol_target,
        vol_window=config.vol_window,
    )
    stat_arb_gross = max(0.0, min(config.gross_leverage, config.stat_arb_pair_gross_pct * max(len(selected_pairs), 1)))
    context = {
        "strategy": "statistical_pairs_mean_reversion",
        "candidate_symbol_count": int(len(liquid_symbols)),
        "candidate_pair_count": int(len(candidates)),
        "selected_pair_count": int(len(selected_pairs)),
        "selected_pairs": selected_pairs,
        "top_pair_candidates": candidates[:12],
        "stat_arb": {
            "lookback_days": int(config.stat_arb_lookback_days),
            "min_correlation": float(config.stat_arb_min_correlation),
            "entry_z": float(config.stat_arb_entry_z),
            "exit_z": float(config.stat_arb_exit_z),
            "max_pairs": int(config.stat_arb_max_pairs),
            "pair_gross_pct": float(config.stat_arb_pair_gross_pct),
        },
        "market_regime": {"label": regime.label, "notes": regime.notes},
    }
    ts, orders, executed_signals, decision_context = execute_signals(
        config,
        latest,
        signals,
        min(regime.leverage, stat_arb_gross),
        regime.spy_vol,
        context,
        bot_name=STAT_ARB_BOT_NAME,
    )
    report = _report_for_run(ts, candidates, selected_pairs, decision_context, config)
    return StatArbRunResult(ts=ts, orders=orders, signals=executed_signals, decision_context=decision_context, report=report)
