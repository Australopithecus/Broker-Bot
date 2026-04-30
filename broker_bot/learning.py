from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from .bots import LLM_BOT_NAME, ML_BOT_NAME, bot_label, normalize_bot_name
from .config import Config, load_config
from .data import fetch_daily_bars
from .llm_utils import call_json_llm
from .logging_db import (
    log_decision_outcomes,
    log_strategy_report,
    read_latest_decision_run,
    read_pending_decision_logs,
    read_recent_decision_logs,
    read_recent_evaluated_decisions,
    read_recent_selected_decisions,
)


COMPONENT_TO_WEIGHT = {
    "technical_adjustment": "technical_weight",
    "snapshot_adjustment": "snapshot_weight",
    "screener_adjustment": "screener_weight",
    "news_adjustment": "news_weight",
    "memory_adjustment": "memory_weight",
    "llm_adjustment": "llm_weight",
}


@dataclass
class LearningReport:
    ts: str
    headline: str
    summary: str
    metrics: dict[str, float]
    weight_updates: dict[str, float]
    report_path: str | None = None


@dataclass
class StrategyReport:
    ts: str
    headline: str
    summary: str
    report_path: str


def _clip(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _load_components(components_json: str | None) -> dict[str, float]:
    if not components_json:
        return {}
    try:
        payload = json.loads(components_json)
    except Exception:
        return {}
    if not isinstance(payload, dict):
        return {}

    clean: dict[str, float] = {}
    for key, value in payload.items():
        try:
            clean[key] = float(value)
        except Exception:
            continue
    return clean


def _load_json_object(payload: str | None) -> dict:
    if not payload:
        return {}
    try:
        parsed = json.loads(payload)
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _component_summary(components: dict[str, float], limit: int = 4) -> str:
    if not components:
        return "No component breakdown recorded."
    ranked = sorted(components.items(), key=lambda item: abs(float(item[1])), reverse=True)
    parts = [
        f"{name.replace('_adjustment', '')}={float(value):+.4f}"
        for name, value in ranked
        if abs(float(value)) >= 0.0001
    ]
    return ", ".join(parts[:limit]) if parts else "No component breakdown recorded."


def _outcome_breakdown(recent_rows: list[tuple[str, str, str, float, float, float | None, float | None, str | None]]) -> dict[str, dict[str, float]]:
    by_side: dict[str, list[tuple[float, float | None]]] = {}
    for _, side, _, _, signed_return, _, beat_spy, _ in recent_rows:
        by_side.setdefault(side, []).append((float(signed_return), beat_spy if beat_spy is None else float(beat_spy)))

    breakdown: dict[str, dict[str, float]] = {}
    for side, values in by_side.items():
        signed = [item[0] for item in values]
        alpha = [item[1] for item in values if item[1] is not None]
        breakdown[side] = {
            "samples": float(len(values)),
            "hit_rate": sum(1 for value in signed if value > 0) / len(signed) if signed else 0.0,
            "avg_signed_return": sum(signed) / len(signed) if signed else 0.0,
            "avg_beat_spy": sum(alpha) / len(alpha) if alpha else 0.0,
        }
    return breakdown


def _component_attribution_lines(component_metrics: dict[str, dict[str, float]]) -> list[str]:
    if not component_metrics:
        return ["- Not enough evaluated decisions for component attribution yet."]
    lines: list[str] = []
    for component_name, stats in sorted(
        component_metrics.items(),
        key=lambda item: float(item[1].get("edge", 0.0)),
        reverse=True,
    ):
        readable = component_name.replace("_adjustment", "").replace("_", " ")
        edge = float(stats.get("edge", 0.0))
        hit_rate = float(stats.get("hit_rate", 0.0))
        samples = int(float(stats.get("samples", 0.0)))
        verdict = "helping" if edge > 0.001 else ("hurting" if edge < -0.001 else "mixed")
        lines.append(f"- {readable}: {verdict}; edge={edge:+.2%}, hit rate={hit_rate:.1%}, samples={samples}.")
    return lines


def _counterfactual_hold_scan(config: Config, cutoff_ts: str, bot_name: str) -> tuple[dict[str, float], list[str]]:
    hold_rows = [
        row
        for row in read_recent_decision_logs(config.db_path, limit=300, bot_name=bot_name)
        if row[3] == 0 and row[2] == "HOLD" and row[0] <= cutoff_ts
    ]
    if not hold_rows:
        return {"hold_sample_count": 0.0}, ["- No mature HOLD candidates were available for counterfactual review."]

    sample = sorted(hold_rows, key=lambda row: abs(float(row[5])), reverse=True)[:40]
    now = datetime.now(timezone.utc)
    oldest_ts = min(datetime.fromisoformat(row[0]) for row in sample)
    symbols = sorted({row[1] for row in sample})
    try:
        bars = fetch_daily_bars(config, symbols + ["SPY"], oldest_ts - timedelta(days=10), now, bot_name=bot_name).bars
    except Exception:
        return {"hold_sample_count": float(len(sample))}, ["- Counterfactual HOLD scan skipped because market data was unavailable."]

    prices = bars.pivot_table(index="timestamp", columns="Symbol", values="close").sort_index()
    outcomes: list[dict[str, float | str]] = []
    for ts, symbol, _, _, _, final_score, _, _ in sample:
        if symbol not in prices.columns:
            continue
        decision_dt = pd.Timestamp(ts)
        symbol_series = prices[symbol].dropna()
        future_symbol = symbol_series[symbol_series.index >= decision_dt]
        if len(future_symbol) <= config.prediction_horizon_days:
            continue

        entry_price = float(future_symbol.iloc[0])
        exit_price = float(future_symbol.iloc[config.prediction_horizon_days])
        raw_return = (exit_price / entry_price) - 1.0 if entry_price > 0 else 0.0
        would_be_side = "LONG" if float(final_score) >= 0 else "SHORT"
        signed_return = raw_return if would_be_side == "LONG" else -raw_return
        spy_return = 0.0
        if "SPY" in prices.columns:
            spy_series = prices["SPY"].dropna()
            future_spy = spy_series[spy_series.index >= decision_dt]
            if len(future_spy) > config.prediction_horizon_days:
                spy_entry = float(future_spy.iloc[0])
                spy_exit = float(future_spy.iloc[config.prediction_horizon_days])
                spy_return = (spy_exit / spy_entry) - 1.0 if spy_entry > 0 else 0.0
        outcomes.append(
            {
                "symbol": symbol,
                "side": would_be_side,
                "score": float(final_score),
                "signed_return": signed_return,
                "beat_spy": signed_return - spy_return,
            }
        )

    if not outcomes:
        return {"hold_sample_count": float(len(sample))}, ["- HOLD scan found no candidates with enough future price data yet."]

    missed = [row for row in outcomes if float(row["signed_return"]) > 0.005]
    avoided = [row for row in outcomes if float(row["signed_return"]) < -0.005]
    metrics = {
        "hold_sample_count": float(len(outcomes)),
        "hold_avg_signed_return": sum(float(row["signed_return"]) for row in outcomes) / len(outcomes),
        "hold_avg_beat_spy": sum(float(row["beat_spy"]) for row in outcomes) / len(outcomes),
        "missed_opportunity_rate": len(missed) / len(outcomes),
        "avoided_loss_rate": len(avoided) / len(outcomes),
    }
    top_missed = sorted(missed, key=lambda row: float(row["signed_return"]), reverse=True)[:5]
    top_avoided = sorted(avoided, key=lambda row: float(row["signed_return"]))[:5]
    lines = [
        (
            f"- Reviewed {len(outcomes)} mature HOLD candidates: average would-be signed return "
            f"{metrics['hold_avg_signed_return']:.2%}, average alpha {metrics['hold_avg_beat_spy']:.2%}."
        ),
        f"- Missed-opportunity rate: {metrics['missed_opportunity_rate']:.1%}; avoided-loss rate: {metrics['avoided_loss_rate']:.1%}.",
    ]
    if top_missed:
        lines.append(
            "- Best skipped setups: "
            + "; ".join(
                f"{row['symbol']} {row['side']} would have returned {float(row['signed_return']):.2%}"
                for row in top_missed
            )
            + "."
        )
    if top_avoided:
        lines.append(
            "- Worst skipped setups avoided: "
            + "; ".join(
                f"{row['symbol']} {row['side']} would have returned {float(row['signed_return']):.2%}"
                for row in top_avoided
            )
            + "."
        )
    return metrics, lines


def _cross_bot_agreement_lines(config: Config, bot_name: str) -> tuple[dict[str, float], list[str]]:
    normalized = normalize_bot_name(bot_name)
    other_bot = LLM_BOT_NAME if normalized == ML_BOT_NAME else ML_BOT_NAME
    own_rows = read_recent_selected_decisions(config.db_path, limit=80, bot_name=normalized)
    other_rows = read_recent_selected_decisions(config.db_path, limit=80, bot_name=other_bot)
    if not own_rows or not other_rows:
        return {"cross_bot_overlap": 0.0}, [f"- No recent {bot_label(other_bot)} selected decisions were available for comparison."]

    own_latest: dict[str, tuple[str, float]] = {}
    for row in own_rows:
        own_latest.setdefault(row[1], (row[2], float(row[4])))
    other_latest: dict[str, tuple[str, float]] = {}
    for row in other_rows:
        other_latest.setdefault(row[1], (row[2], float(row[4])))

    overlap = sorted(set(own_latest) & set(other_latest))
    agreements = [symbol for symbol in overlap if own_latest[symbol][0] == other_latest[symbol][0]]
    disagreements = [symbol for symbol in overlap if own_latest[symbol][0] != other_latest[symbol][0]]
    metrics = {
        "cross_bot_overlap": float(len(overlap)),
        "cross_bot_agreement_count": float(len(agreements)),
        "cross_bot_disagreement_count": float(len(disagreements)),
        "cross_bot_agreement_rate": len(agreements) / len(overlap) if overlap else 0.0,
    }
    lines = [
        f"- Compared recent selected decisions against {bot_label(other_bot)}: {len(overlap)} overlapping symbols, {len(agreements)} agreements, {len(disagreements)} disagreements.",
    ]
    if agreements:
        lines.append("- Agreement names: " + ", ".join(f"{symbol} {own_latest[symbol][0]}" for symbol in agreements[:8]) + ".")
    if disagreements:
        lines.append(
            "- Disagreement names: "
            + ", ".join(
                f"{symbol} {normalized.upper()}={own_latest[symbol][0]} vs {other_bot.upper()}={other_latest[symbol][0]}"
                for symbol in disagreements[:8]
            )
            + "."
        )
    return metrics, lines


def _thesis_bullets(
    symbol: str,
    side: str,
    base_score: float,
    final_score: float,
    rationale: str,
    components: dict[str, float],
    research: dict,
) -> list[str]:
    bullets = [
        f"Signal moved from {base_score:.2%} to {final_score:.2%} after ensemble overlays.",
        f"Component mix: {_component_summary(components)}",
    ]
    if rationale:
        bullets.append(rationale)

    headlines = ((research.get("news_headlines") or {}).get(symbol) or [])[:3]
    if headlines:
        bullets.append("Recent headlines: " + " | ".join(headlines))

    llm_rationale = ((research.get("llm_rationales") or {}).get(symbol) or "").strip()
    if llm_rationale:
        bullets.append(f"LLM view: {llm_rationale}")

    snapshot_score = (research.get("snapshot_scores") or {}).get(symbol)
    if snapshot_score is not None:
        bullets.append(f"Snapshot pressure score: {float(snapshot_score):+.2f}")

    memory_count_note = "long" if side == "LONG" else "short"
    bullets.append(f"Bot is currently treating this as a {memory_count_note} idea with explainable bounded sizing.")
    return bullets


def _deep_research_notes(config: Config, watchlist_rows: list[dict], research: dict) -> list[dict]:
    if not watchlist_rows:
        return []

    base_notes = []
    for row in watchlist_rows:
        bullets = _thesis_bullets(
            symbol=row["symbol"],
            side=row["side"],
            base_score=row["base_score"],
            final_score=row["final_score"],
            rationale=row["rationale"],
            components=row["components"],
            research=research,
        )
        base_notes.append(
            {
                "symbol": row["symbol"],
                "side": row["side"],
                "summary": bullets[0],
                "thesis": bullets[:3],
                "risks": bullets[3:5] or ["Crowded move risk and model overfitting risk remain."],
                "watch_for": bullets[5:] or ["Monitor next report for changes in component mix and relative performance."],
            }
        )

    if not config.llm_enabled:
        return base_notes

    payload = {
        "objective": "Write concise but informative watchlist research notes for a paper-trading bot.",
        "symbols": [
            {
                "symbol": row["symbol"],
                "side": row["side"],
                "base_score": round(row["base_score"], 6),
                "final_score": round(row["final_score"], 6),
                "components": row["components"],
                "rationale": row["rationale"],
                "headlines": ((research.get("news_headlines") or {}).get(row["symbol"]) or [])[:3],
                "llm_rationale": ((research.get("llm_rationales") or {}).get(row["symbol"]) or ""),
            }
            for row in watchlist_rows[:6]
        ],
        "output_format": {
            "notes": [
                {
                    "symbol": "ticker",
                    "summary": "one-paragraph summary",
                    "thesis": ["bullet", "bullet"],
                    "risks": ["bullet", "bullet"],
                    "watch_for": ["bullet", "bullet"],
                }
            ]
        },
    }
    response = call_json_llm(
        config,
        system_prompt=(
            "You are writing an internal watchlist memo for a paper-trading system. "
            "Return JSON only with a notes array. "
            "Keep each note concrete, balanced, and limited to the supplied evidence."
        ),
        payload=payload,
        max_output_tokens=1200,
    )
    if not response:
        return base_notes

    notes = response.get("notes")
    if not isinstance(notes, list):
        return base_notes

    structured: list[dict] = []
    side_map = {row["symbol"]: row["side"] for row in watchlist_rows}
    for note in notes:
        if not isinstance(note, dict):
            continue
        symbol = str(note.get("symbol", "")).strip().upper()
        if not symbol or symbol not in side_map:
            continue
        structured.append(
            {
                "symbol": symbol,
                "side": side_map[symbol],
                "summary": str(note.get("summary", "")).strip() or "No summary provided.",
                "thesis": [str(item).strip() for item in note.get("thesis", []) if str(item).strip()][:4],
                "risks": [str(item).strip() for item in note.get("risks", []) if str(item).strip()][:4],
                "watch_for": [str(item).strip() for item in note.get("watch_for", []) if str(item).strip()][:4],
            }
        )
    return structured or base_notes


def build_symbol_memory(db_path: str, limit: int = 300, bot_name: str = "ml") -> dict[str, float]:
    rows = read_recent_evaluated_decisions(db_path, limit=limit, bot_name=bot_name)
    by_symbol: dict[str, list[float]] = {}
    for symbol, _, _, _, signed_return, _, _, _ in rows:
        by_symbol.setdefault(symbol, []).append(float(signed_return))

    memory: dict[str, float] = {}
    for symbol, returns in by_symbol.items():
        if not returns:
            continue
        avg_signed = sum(returns) / len(returns)
        hit_rate = sum(1 for value in returns if value > 0) / len(returns)
        confidence = min(1.0, len(returns) / 6.0)
        score = ((avg_signed / 0.02) * 0.6) + (((hit_rate - 0.5) * 2.0) * 0.4)
        memory[symbol] = _clip(score, -1.0, 1.0) * confidence
    return memory


def _evaluate_pending_decisions(
    config: Config,
    pending_rows: list[tuple[int, str, str, str, float, str | None]],
    bot_name: str = "ml",
) -> list[tuple[int, str, int, float, float, float | None, float | None, str]]:
    if not pending_rows:
        return []

    now = datetime.now(timezone.utc)
    oldest_ts = min(datetime.fromisoformat(row[1]) for row in pending_rows)
    start = oldest_ts - timedelta(days=10)
    symbols = sorted({row[2] for row in pending_rows})
    bars = fetch_daily_bars(config, symbols + ["SPY"], start, now, bot_name=bot_name).bars
    prices = bars.pivot_table(index="timestamp", columns="Symbol", values="close").sort_index()

    evaluated_rows: list[tuple[int, str, int, float, float, float | None, float | None, str]] = []
    for decision_id, ts, symbol, side, _, _ in pending_rows:
        if symbol not in prices.columns:
            continue

        decision_dt = pd.Timestamp(ts)
        symbol_series = prices[symbol].dropna()
        future_symbol = symbol_series[symbol_series.index >= decision_dt]
        if len(future_symbol) <= config.prediction_horizon_days:
            continue

        entry_price = float(future_symbol.iloc[0])
        exit_price = float(future_symbol.iloc[config.prediction_horizon_days])
        raw_return = (exit_price / entry_price) - 1.0 if entry_price > 0 else 0.0
        signed_return = raw_return if side == "LONG" else -raw_return

        spy_return = None
        beat_spy = None
        if "SPY" in prices.columns:
            spy_series = prices["SPY"].dropna()
            future_spy = spy_series[spy_series.index >= decision_dt]
            if len(future_spy) > config.prediction_horizon_days:
                spy_entry = float(future_spy.iloc[0])
                spy_exit = float(future_spy.iloc[config.prediction_horizon_days])
                if spy_entry > 0:
                    spy_return = (spy_exit / spy_entry) - 1.0
                    beat_spy = signed_return - spy_return

        if signed_return > 0.002:
            outcome_label = "win"
        elif signed_return < -0.002:
            outcome_label = "loss"
        else:
            outcome_label = "flat"

        evaluated_rows.append(
            (
                decision_id,
                now.isoformat(),
                config.prediction_horizon_days,
                raw_return,
                signed_return,
                spy_return,
                beat_spy,
                outcome_label,
            )
        )

    return evaluated_rows


def _component_metrics(db_path: str, limit: int = 300, bot_name: str = "ml") -> dict[str, dict[str, float]]:
    rows = read_recent_evaluated_decisions(db_path, limit=limit, bot_name=bot_name)
    metrics: dict[str, dict[str, float]] = {}

    for _, _, _, _, signed_return, _, _, components_json in rows:
        components = _load_components(components_json)
        for component_name in COMPONENT_TO_WEIGHT:
            component_value = float(components.get(component_name, 0.0))
            if abs(component_value) < 1e-9:
                continue
            bucket = metrics.setdefault(component_name, {"samples": 0.0, "edge": 0.0, "hits": 0.0})
            bucket["samples"] += 1.0
            directional_edge = signed_return if component_value > 0 else -signed_return
            bucket["edge"] += directional_edge
            if directional_edge > 0:
                bucket["hits"] += 1.0

    for component_name, bucket in metrics.items():
        samples = bucket["samples"]
        if samples > 0:
            bucket["edge"] /= samples
            bucket["hit_rate"] = bucket["hits"] / samples
        else:
            bucket["hit_rate"] = 0.0
        del bucket["hits"]
    return metrics


def _write_report_file(config: Config, prefix: str, body: str) -> str:
    reports_dir = Path(config.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"{prefix}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(body, encoding="utf-8")
    return str(report_path)


def _signed_return_metrics(values: list[float], alphas: list[float]) -> dict[str, float]:
    return {
        "samples": float(len(values)),
        "hit_rate": sum(1 for value in values if value > 0) / len(values) if values else 0.0,
        "avg_signed_return": sum(values) / len(values) if values else 0.0,
        "avg_beat_spy": sum(alphas) / len(alphas) if alphas else 0.0,
    }


def generate_attribution_report(config: Config, bot_name: str = "ml") -> StrategyReport:
    normalized_bot = normalize_bot_name(bot_name)
    recent_rows = read_recent_evaluated_decisions(config.db_path, limit=400, bot_name=normalized_bot)
    component_metrics = _component_metrics(config.db_path, limit=400, bot_name=normalized_bot)
    signed_returns = [float(row[4]) for row in recent_rows]
    alphas = [float(row[6]) for row in recent_rows if row[6] is not None]
    metrics = _signed_return_metrics(signed_returns, alphas)
    metrics["component_count"] = float(len(component_metrics))

    by_side = _outcome_breakdown(recent_rows)
    winners = sorted(recent_rows, key=lambda row: float(row[4]), reverse=True)[:5]
    losers = sorted(recent_rows, key=lambda row: float(row[4]))[:5]
    helpful = sorted(component_metrics.items(), key=lambda item: float(item[1].get("edge", 0.0)), reverse=True)[:5]
    harmful = sorted(component_metrics.items(), key=lambda item: float(item[1].get("edge", 0.0)))[:5]
    helpful_lines = [
        f"- {name.replace('_adjustment', '').replace('_', ' ')}: edge={stats.get('edge', 0.0):+.2%}, "
        f"hit rate={stats.get('hit_rate', 0.0):.1%}, samples={int(stats.get('samples', 0.0))}"
        for name, stats in helpful
    ] or ["- Not enough component data yet."]
    harmful_lines = [
        f"- {name.replace('_adjustment', '').replace('_', ' ')}: edge={stats.get('edge', 0.0):+.2%}, "
        f"hit rate={stats.get('hit_rate', 0.0):.1%}, samples={int(stats.get('samples', 0.0))}"
        for name, stats in harmful
    ] or ["- Not enough component data yet."]
    winner_lines = [
        f"- {symbol} {side} evaluated {evaluated_ts}: signed={signed_return:.2%}, raw={realized_return:.2%}"
        for symbol, side, evaluated_ts, realized_return, signed_return, _, _, _ in winners
    ] or ["- No evaluated winners yet."]
    loser_lines = [
        f"- {symbol} {side} evaluated {evaluated_ts}: signed={signed_return:.2%}, raw={realized_return:.2%}"
        for symbol, side, evaluated_ts, realized_return, signed_return, _, _, _ in losers
    ] or ["- No evaluated losses yet."]

    body = "\n".join(
        [
            f"# {bot_label(normalized_bot)} Post-Trade Attribution",
            "",
            f"Generated at {datetime.now(timezone.utc).isoformat()}",
            "",
            "This report asks a simple question: which ingredients in the bot's decisions have actually been associated with profitable outcomes so far?",
            "",
            "## Overall outcome attribution",
            f"- Evaluated decisions: {len(recent_rows)}",
            f"- Hit rate: {metrics['hit_rate']:.1%}",
            f"- Average signed return: {metrics['avg_signed_return']:.2%}",
            f"- Average alpha versus SPY: {metrics['avg_beat_spy']:.2%}",
            "",
            "## Side breakdown",
            json.dumps(by_side or {"status": "not enough outcomes yet"}, indent=2, sort_keys=True),
            "",
            "## Components most associated with better outcomes",
            *helpful_lines,
            "",
            "## Components most associated with worse outcomes",
            *harmful_lines,
            "",
            "## Best recent decisions",
            *winner_lines,
            "",
            "## Worst recent decisions",
            *loser_lines,
        ]
    )
    ts = datetime.now(timezone.utc).isoformat()
    report_path = _write_report_file(config, f"attribution_{normalized_bot}", body)
    headline = f"{bot_label(normalized_bot)} Post-Trade Attribution"
    summary = (
        f"Reviewed {len(recent_rows)} evaluated decisions; hit rate {metrics['hit_rate']:.1%}, "
        f"average signed return {metrics['avg_signed_return']:.2%}."
    )
    log_strategy_report(
        config.db_path,
        ts,
        "attribution",
        headline,
        summary,
        body,
        json.dumps(metrics, sort_keys=True),
        json.dumps({}, sort_keys=True),
        bot_name=normalized_bot,
    )
    return StrategyReport(ts=ts, headline=headline, summary=summary, report_path=report_path)


def _selected_rows_metrics(rows: list[tuple]) -> dict[str, float]:
    signed_returns = [float(row[10]) for row in rows if row[10] is not None]
    alphas = [float(row[11]) for row in rows if row[11] is not None]
    return _signed_return_metrics(signed_returns, alphas)


def generate_champion_challenger_report(config: Config, bot_name: str = "ml") -> StrategyReport:
    normalized_bot = normalize_bot_name(bot_name)
    rows = read_recent_selected_decisions(config.db_path, limit=500, bot_name=normalized_bot)
    evaluated = [row for row in rows if row[10] is not None]
    if normalized_bot == LLM_BOT_NAME:
        threshold = max(float(config.llm_min_conviction), 0.0)
        threshold_label = "LLM minimum conviction"
        champion_description = (
            "Champion: the current LLM network, including Stock Selector, Analyst, Trader, "
            "Skeptic review, conviction gate, and normal execution/risk controls."
        )
        challenger_description = (
            "Challenger: a stricter shadow version of the LLM policy that counts only selected "
            f"decisions with absolute conviction/final score at or above {threshold:.4f}."
        )
        implemented_changes = [
            f"LLM conviction gate is active at {threshold:.4f}.",
            "LLM Skeptic review can caution, reduce conviction, or veto weakly supported trades before execution.",
            "Champion/challenger remains a shadow evaluation; it does not automatically promote a new policy.",
        ]
    else:
        threshold = max(float(config.min_signal_abs_score), 0.0)
        threshold_label = "minimum absolute signal score"
        champion_description = (
            "Champion: the current ML ensemble policy using the trained return model, research overlays, "
            "symbol memory, confidence gate, and normal execution/risk controls."
        )
        challenger_description = (
            "Challenger: a stricter shadow version of the ML policy that counts only selected "
            f"decisions with absolute final score at or above {threshold:.4f}."
        )
        implemented_changes = [
            f"ML confidence gate is active at {threshold:.4f}; weaker selected signals are converted to HOLD before sizing.",
            "Post-trade attribution now tracks which signal components are associated with wins or losses.",
            "Champion/challenger remains a shadow evaluation; it does not automatically promote a new policy.",
        ]

    challenger = [row for row in evaluated if abs(float(row[4])) >= threshold]
    excluded = [row for row in evaluated if abs(float(row[4])) < threshold]
    champion_metrics = _selected_rows_metrics(evaluated)
    challenger_metrics = _selected_rows_metrics(challenger)
    excluded_metrics = _selected_rows_metrics(excluded)

    sample_note = ""
    if int(challenger_metrics["samples"]) < 10:
        verdict = "Too early to promote the challenger because it has fewer than 10 evaluated samples."
        sample_note = "The dashboard should treat this as directional evidence, not proof."
    elif challenger_metrics["avg_signed_return"] > champion_metrics["avg_signed_return"] + 0.001:
        verdict = "The challenger is outperforming the current champion on recent evaluated decisions."
    else:
        verdict = "The challenger has not yet shown enough improvement over the current champion."

    body = "\n".join(
        [
            f"# {bot_label(normalized_bot)} Champion / Challenger",
            "",
            f"Generated at {datetime.now(timezone.utc).isoformat()}",
            "",
            "Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current confidence threshold.",
            "",
            f"Threshold used: {threshold_label} = {threshold:.4f}",
            "",
            "## Models being tested",
            f"- {champion_description}",
            f"- {challenger_description}",
            "",
            "## Verdict",
            verdict,
            sample_note,
            "",
            "## Champion metrics",
            json.dumps(champion_metrics, indent=2, sort_keys=True),
            "",
            "## Challenger metrics",
            json.dumps(challenger_metrics, indent=2, sort_keys=True),
            "",
            "## Trades excluded by the challenger",
            json.dumps(excluded_metrics, indent=2, sort_keys=True),
            "",
            "## Changes implemented",
            *[f"- {item}" for item in implemented_changes],
            "",
            "## Interpretation",
            "- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.",
            "- If excluded trades perform well, the gate may be too strict and should be relaxed.",
            "- This is shadow evaluation only; it reports what would have happened without automatically changing the strategy.",
        ]
    )
    ts = datetime.now(timezone.utc).isoformat()
    metrics = {
        "threshold": threshold,
        "champion_samples": champion_metrics["samples"],
        "champion_hit_rate": champion_metrics["hit_rate"],
        "champion_avg_signed_return": champion_metrics["avg_signed_return"],
        "challenger_samples": challenger_metrics["samples"],
        "challenger_hit_rate": challenger_metrics["hit_rate"],
        "challenger_avg_signed_return": challenger_metrics["avg_signed_return"],
        "excluded_samples": excluded_metrics["samples"],
        "excluded_avg_signed_return": excluded_metrics["avg_signed_return"],
    }
    changes = {
        "verdict": verdict,
        "champion_description": champion_description,
        "challenger_description": challenger_description,
        "implemented_changes": implemented_changes,
        "threshold_label": threshold_label,
    }
    report_path = _write_report_file(config, f"champion_challenger_{normalized_bot}", body)
    headline = f"{bot_label(normalized_bot)} Champion / Challenger"
    summary = (
        f"Compared current policy with a stricter confidence-gated challenger. "
        f"Champion avg {champion_metrics['avg_signed_return']:.2%}; "
        f"challenger avg {challenger_metrics['avg_signed_return']:.2%}."
    )
    log_strategy_report(
        config.db_path,
        ts,
        "champion_challenger",
        headline,
        summary,
        body,
        json.dumps(metrics, sort_keys=True),
        json.dumps(changes, sort_keys=True),
        bot_name=normalized_bot,
    )
    return StrategyReport(ts=ts, headline=headline, summary=summary, report_path=report_path)


def _propose_weight_updates(
    config: Config,
    component_metrics: dict[str, dict[str, float]],
) -> tuple[dict[str, float], dict[str, float]]:
    current_weights = {
        "technical_weight": config.technical_weight,
        "snapshot_weight": config.snapshot_weight,
        "screener_weight": config.screener_weight,
        "news_weight": config.news_weight,
        "memory_weight": config.memory_weight,
        "llm_weight": config.llm_weight,
    }
    updated_weights = dict(current_weights)
    changed_weights: dict[str, float] = {}

    for component_name, weight_name in COMPONENT_TO_WEIGHT.items():
        stats = component_metrics.get(component_name)
        if not stats:
            continue
        if stats.get("samples", 0.0) < 8:
            continue

        edge = float(stats.get("edge", 0.0))
        step = 0.0
        if edge > 0.0015:
            step = 0.1
        elif edge < -0.0015:
            step = -0.1
        if step == 0.0:
            continue

        proposed = round(_clip(updated_weights[weight_name] + step, 0.25, 2.0), 3)
        if abs(proposed - updated_weights[weight_name]) < 1e-9:
            continue
        updated_weights[weight_name] = proposed
        changed_weights[weight_name] = proposed

    return updated_weights, changed_weights


def _write_learned_policy(
    config: Config,
    weights: dict[str, float],
    component_metrics: dict[str, dict[str, float]],
    summary: str,
) -> None:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "weights": weights,
        "component_metrics": component_metrics,
    }
    out_path = Path(config.learned_policy_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def review_and_learn(config: Config, bot_name: str = "ml") -> LearningReport:
    normalized_bot = normalize_bot_name(bot_name)
    cutoff_ts = (datetime.now(timezone.utc) - timedelta(days=max(config.prediction_horizon_days, 1) + 1)).isoformat()
    pending_rows = read_pending_decision_logs(config.db_path, cutoff_ts=cutoff_ts, limit=1200, bot_name=normalized_bot)
    evaluated_rows = _evaluate_pending_decisions(config, pending_rows, bot_name=normalized_bot) if pending_rows else []
    if evaluated_rows:
        log_decision_outcomes(config.db_path, evaluated_rows)

    recent_rows = read_recent_evaluated_decisions(config.db_path, limit=200, bot_name=normalized_bot)
    signed_returns = [float(row[4]) for row in recent_rows]
    hit_rate = (sum(1 for value in signed_returns if value > 0) / len(signed_returns)) if signed_returns else 0.0
    avg_signed_return = (sum(signed_returns) / len(signed_returns)) if signed_returns else 0.0
    avg_beat_spy = (
        sum(float(row[6]) for row in recent_rows if row[6] is not None) / max(1, sum(1 for row in recent_rows if row[6] is not None))
    ) if recent_rows else 0.0

    component_metrics = _component_metrics(config.db_path, limit=300, bot_name=normalized_bot)
    updated_weights, changed_weights = _propose_weight_updates(config, component_metrics)
    outcome_breakdown = _outcome_breakdown(recent_rows)
    hold_metrics, hold_lines = _counterfactual_hold_scan(config, cutoff_ts, normalized_bot)

    summary = (
        f"Evaluated {len(evaluated_rows)} mature decisions this run; "
        f"recent hit rate {hit_rate:.1%}, average signed return {avg_signed_return:.2%}."
    )
    _write_learned_policy(config, updated_weights, component_metrics, summary)

    ts = datetime.now(timezone.utc).isoformat()
    headline = f"{bot_label(normalized_bot)} Learning Update"
    metrics = {
        "newly_evaluated": float(len(evaluated_rows)),
        "recent_hit_rate": hit_rate,
        "recent_avg_signed_return": avg_signed_return,
        "recent_avg_beat_spy": avg_beat_spy,
    }
    metrics.update(hold_metrics)
    body = "\n".join(
        [
            f"# {bot_label(normalized_bot)} Learning Update",
            "",
            summary,
            "",
            "## Decision quality diagnostics",
            json.dumps(outcome_breakdown or {"status": "not enough outcomes yet"}, indent=2, sort_keys=True),
            "",
            "## Component attribution",
            *_component_attribution_lines(component_metrics),
            "",
            "## Counterfactual HOLD scan",
            *hold_lines,
            "",
            "## Weight changes",
            json.dumps(changed_weights or {"status": "no bounded weight changes this run"}, indent=2, sort_keys=True),
            "",
            "## Component metrics",
            json.dumps(component_metrics, indent=2, sort_keys=True),
        ]
    )

    reports_dir = Path(config.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"learning_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(body, encoding="utf-8")

    log_strategy_report(
        config.db_path,
        ts,
        "learning",
        headline,
        summary,
        body,
        json.dumps(metrics, sort_keys=True),
        json.dumps(changed_weights, sort_keys=True),
        bot_name=normalized_bot,
    )

    return LearningReport(
        ts=ts,
        headline=headline,
        summary=summary,
        metrics=metrics,
        weight_updates=changed_weights,
        report_path=str(report_path),
    )


def generate_strategy_report(config: Config, bot_name: str = "ml") -> StrategyReport:
    normalized_bot = normalize_bot_name(bot_name)
    learning_report = review_and_learn(config, bot_name=normalized_bot)
    current_config = load_config()
    latest_run = read_latest_decision_run(config.db_path, bot_name=normalized_bot)
    latest_run_context = _load_json_object(latest_run[3]) if latest_run else {}
    research = latest_run_context.get("research") if isinstance(latest_run_context.get("research"), dict) else {}

    advisor_headline = "Advisor unavailable"
    advisor_summary = "Advisor report could not be generated."
    advisor_suggestions: list[str] = []
    advisor_overrides: dict[str, float] = {}
    try:
        from .advisor import generate_advisor_report

        advisor = generate_advisor_report(current_config)
        advisor_headline = advisor.headline
        advisor_summary = advisor.summary
        advisor_suggestions = advisor.suggestions[:8]
        advisor_overrides = advisor.overrides
    except Exception:
        pass

    recent_decisions = read_recent_decision_logs(config.db_path, limit=30, bot_name=normalized_bot)
    recent_outcomes = read_recent_evaluated_decisions(config.db_path, limit=20, bot_name=normalized_bot)
    cross_bot_metrics, cross_bot_lines = _cross_bot_agreement_lines(current_config, normalized_bot)
    market_regime = latest_run_context.get("market_regime", {}) if isinstance(latest_run_context.get("market_regime"), dict) else {}
    regime_notes = market_regime.get("notes", [])
    if not isinstance(regime_notes, list):
        regime_notes = []
    portfolio_risk = latest_run_context.get("portfolio_risk", {}) if isinstance(latest_run_context.get("portfolio_risk"), dict) else {}

    watchlist_rows: list[dict] = []
    for ts, symbol, side, selected, base_score, final_score, components_json, rationale in recent_decisions:
        if not selected or side == "HOLD":
            continue
        watchlist_rows.append(
            {
                "ts": ts,
                "symbol": symbol,
                "side": side,
                "base_score": float(base_score),
                "final_score": float(final_score),
                "components": _load_components(components_json),
                "rationale": rationale or "",
            }
        )
    watchlist_rows = sorted(watchlist_rows, key=lambda row: abs(row["final_score"]), reverse=True)
    deep_notes = _deep_research_notes(current_config, watchlist_rows[:6], research)

    decision_lines = []
    for ts, symbol, side, _, base_score, final_score, _, rationale in recent_decisions[:12]:
        if side == "HOLD":
            continue
        note = rationale or "No extra rationale recorded."
        decision_lines.append(
            f"- {ts}: {symbol} {side} base={base_score:.4f} final={final_score:.4f}. {note}"
        )

    outcome_lines = []
    for symbol, side, evaluated_ts, realized_return, signed_return, spy_return, beat_spy, _ in recent_outcomes[:10]:
        spy_note = f", SPY={spy_return:.2%}" if spy_return is not None else ""
        beat_note = f", alpha={beat_spy:.2%}" if beat_spy is not None else ""
        outcome_lines.append(
            f"- {evaluated_ts}: {symbol} {side} raw={realized_return:.2%}, signed={signed_return:.2%}{spy_note}{beat_note}"
        )

    current_weights = {
        "technical_weight": current_config.technical_weight,
        "snapshot_weight": current_config.snapshot_weight,
        "screener_weight": current_config.screener_weight,
        "news_weight": current_config.news_weight,
        "memory_weight": current_config.memory_weight,
        "llm_weight": current_config.llm_weight,
    }

    watchlist_lines = []
    for row in watchlist_rows[:10]:
        headlines = ((research.get("news_headlines") or {}).get(row["symbol"]) or [])[:2]
        headline_text = f" Headlines: {' | '.join(headlines)}" if headlines else ""
        watchlist_lines.append(
            f"- {row['symbol']} {row['side']} base={row['base_score']:.2%} final={row['final_score']:.2%}. "
            f"{row['rationale'] or 'No extra rationale recorded.'}{headline_text}"
        )

    research_sections = []
    for note in deep_notes:
        research_sections.extend(
            [
                f"### {note['symbol']} ({note['side']})",
                note["summary"],
                "",
                "Thesis:",
                *[f"- {item}" for item in note.get("thesis", [])],
                "",
                "Risks:",
                *[f"- {item}" for item in note.get("risks", [])],
                "",
                "What to monitor next:",
                *[f"- {item}" for item in note.get("watch_for", [])],
                "",
            ]
        )

    body = "\n".join(
        [
            f"# {bot_label(normalized_bot)} Strategy Report",
            "",
            f"Generated at {datetime.now(timezone.utc).isoformat()}",
            "",
            "## Executive summary",
            (
                f"Latest decision run reviewed {latest_run_context.get('candidate_count', 0)} candidates, "
                f"selected {latest_run_context.get('selected_long_count', 0)} longs and "
                f"{latest_run_context.get('selected_short_count', 0)} shorts."
                if latest_run_context
                else "No recent decision-run context was available."
            ),
            "",
            "## Current learned weights",
            json.dumps(current_weights, indent=2, sort_keys=True),
            "",
            "## Market regime and risk controls",
            f"Regime: {market_regime.get('label', 'unknown')}",
            *(f"- {note}" for note in regime_notes if isinstance(note, str)),
            "",
            "Portfolio risk summary:",
            json.dumps(portfolio_risk or {"status": "no portfolio risk summary captured"}, indent=2, sort_keys=True),
            "",
            "## Cross-bot agreement",
            *cross_bot_lines,
            "",
            "## Current watchlist",
            *(watchlist_lines or ["- No current watchlist entries were available."]),
            "",
            "## Deep research notes",
            *(research_sections or ["No deep research notes were available for the latest watchlist."]),
            "",
            "## What the bot recently decided",
            *(decision_lines or ["- No recent LONG/SHORT decisions logged yet."]),
            "",
            "## What the bot recently learned",
            *(outcome_lines or ["- No mature decisions have been evaluated yet."]),
            "",
            "## Learning summary",
            learning_report.summary,
            "",
            "## Advisor summary",
            f"{advisor_headline}: {advisor_summary}",
            *(f"- {suggestion}" for suggestion in advisor_suggestions),
            "",
            "## Advisor overrides under consideration",
            json.dumps(advisor_overrides, indent=2, sort_keys=True),
        ]
    )

    ts = datetime.now(timezone.utc).isoformat()
    reports_dir = Path(config.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"strategy_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(body, encoding="utf-8")

    metrics = dict(learning_report.metrics)
    metrics["recent_decision_count"] = float(len(recent_decisions))
    metrics["recent_outcome_count"] = float(len(recent_outcomes))
    metrics["watchlist_count"] = float(len(watchlist_rows))
    metrics["deep_research_count"] = float(len(deep_notes))
    metrics.update(cross_bot_metrics)
    summary = (
        f"{learning_report.summary} Advisor says: {advisor_summary}"
        if advisor_summary
        else learning_report.summary
    )

    log_strategy_report(
        config.db_path,
        ts,
        "strategy",
        f"{bot_label(normalized_bot)} Strategy Report",
        summary,
        body,
        json.dumps(metrics, sort_keys=True),
        json.dumps(
            {
                "learning_weight_updates": learning_report.weight_updates,
                "advisor_overrides": advisor_overrides,
            },
            sort_keys=True,
        ),
        bot_name=normalized_bot,
    )

    watchlist_body = "\n".join(
        [
            "# Broker Bot Watchlist",
            "",
            f"Generated at {datetime.now(timezone.utc).isoformat()}",
            "",
            "## Ranked ideas",
            *(watchlist_lines or ["- No current watchlist entries were available."]),
            "",
            "## Research notes",
            *(research_sections or ["No deep research notes were available for the latest watchlist."]),
        ]
    )
    log_strategy_report(
        config.db_path,
        ts,
        "watchlist",
        "Watchlist Report",
        f"Prepared {len(watchlist_rows[:10])} watchlist ideas with {len(deep_notes)} deeper research notes.",
        watchlist_body,
        json.dumps(
            {
                "watchlist_count": len(watchlist_rows),
                "deep_research_count": len(deep_notes),
            },
            sort_keys=True,
        ),
        json.dumps({}, sort_keys=True),
        bot_name=normalized_bot,
    )

    return StrategyReport(
        ts=ts,
        headline=f"{bot_label(normalized_bot)} Strategy Report",
        summary=summary,
        report_path=str(report_path),
    )
