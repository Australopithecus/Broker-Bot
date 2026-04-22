from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from .bots import bot_label, normalize_bot_name
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
    body = "\n".join(
        [
            f"# {bot_label(normalized_bot)} Learning Update",
            "",
            summary,
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
