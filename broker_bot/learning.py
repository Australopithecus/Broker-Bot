from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from .config import Config, load_config
from .data import fetch_daily_bars
from .logging_db import (
    log_decision_outcomes,
    log_strategy_report,
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


def build_symbol_memory(db_path: str, limit: int = 300) -> dict[str, float]:
    rows = read_recent_evaluated_decisions(db_path, limit=limit)
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
) -> list[tuple[int, str, int, float, float, float | None, float | None, str]]:
    if not pending_rows:
        return []

    now = datetime.now(timezone.utc)
    oldest_ts = min(datetime.fromisoformat(row[1]) for row in pending_rows)
    start = oldest_ts - timedelta(days=10)
    symbols = sorted({row[2] for row in pending_rows})
    bars = fetch_daily_bars(config, symbols + ["SPY"], start, now).bars
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


def _component_metrics(db_path: str, limit: int = 300) -> dict[str, dict[str, float]]:
    rows = read_recent_evaluated_decisions(db_path, limit=limit)
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


def review_and_learn(config: Config) -> LearningReport:
    cutoff_ts = (datetime.now(timezone.utc) - timedelta(days=max(config.prediction_horizon_days, 1) + 1)).isoformat()
    pending_rows = read_pending_decision_logs(config.db_path, cutoff_ts=cutoff_ts, limit=1200)
    evaluated_rows = _evaluate_pending_decisions(config, pending_rows) if pending_rows else []
    if evaluated_rows:
        log_decision_outcomes(config.db_path, evaluated_rows)

    recent_rows = read_recent_evaluated_decisions(config.db_path, limit=200)
    signed_returns = [float(row[4]) for row in recent_rows]
    hit_rate = (sum(1 for value in signed_returns if value > 0) / len(signed_returns)) if signed_returns else 0.0
    avg_signed_return = (sum(signed_returns) / len(signed_returns)) if signed_returns else 0.0
    avg_beat_spy = (
        sum(float(row[6]) for row in recent_rows if row[6] is not None) / max(1, sum(1 for row in recent_rows if row[6] is not None))
    ) if recent_rows else 0.0

    component_metrics = _component_metrics(config.db_path, limit=300)
    updated_weights, changed_weights = _propose_weight_updates(config, component_metrics)

    summary = (
        f"Evaluated {len(evaluated_rows)} mature decisions this run; "
        f"recent hit rate {hit_rate:.1%}, average signed return {avg_signed_return:.2%}."
    )
    _write_learned_policy(config, updated_weights, component_metrics, summary)

    ts = datetime.now(timezone.utc).isoformat()
    headline = "Learning Update"
    metrics = {
        "newly_evaluated": float(len(evaluated_rows)),
        "recent_hit_rate": hit_rate,
        "recent_avg_signed_return": avg_signed_return,
        "recent_avg_beat_spy": avg_beat_spy,
    }
    body = "\n".join(
        [
            "# Learning Update",
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
    )

    return LearningReport(
        ts=ts,
        headline=headline,
        summary=summary,
        metrics=metrics,
        weight_updates=changed_weights,
        report_path=str(report_path),
    )


def generate_strategy_report(config: Config) -> StrategyReport:
    learning_report = review_and_learn(config)
    current_config = load_config()

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

    recent_decisions = read_recent_decision_logs(config.db_path, limit=30)
    recent_outcomes = read_recent_evaluated_decisions(config.db_path, limit=20)

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

    body = "\n".join(
        [
            "# Broker Bot Strategy Report",
            "",
            f"Generated at {datetime.now(timezone.utc).isoformat()}",
            "",
            "## Current learned weights",
            json.dumps(current_weights, indent=2, sort_keys=True),
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
    summary = (
        f"{learning_report.summary} Advisor says: {advisor_summary}"
        if advisor_summary
        else learning_report.summary
    )

    log_strategy_report(
        config.db_path,
        ts,
        "strategy",
        "Strategy Report",
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
    )

    return StrategyReport(
        ts=ts,
        headline="Strategy Report",
        summary=summary,
        report_path=str(report_path),
    )
