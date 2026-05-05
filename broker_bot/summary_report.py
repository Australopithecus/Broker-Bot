from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .bots import BOT_LABELS, LLM_BOT_NAME, ML_BOT_NAME, STAT_ARB_BOT_NAME, bot_label
from .config import Config, configured_bot_names
from .dashboard_metrics import WINDOW_OPTIONS, bot_performance_metrics, equity_frame, filter_frame_to_window, pct_change
from .llm_utils import call_json_llm
from .logging_db import (
    log_strategy_report,
    read_available_bot_names,
    read_latest_decision_run,
    read_latest_equity,
    read_latest_positions,
    read_latest_strategy_reports,
    read_latest_trades,
    read_recent_decision_logs,
    read_recent_selected_decisions,
)
from .model_revisions import apply_model_revision


SUMMARY_REPORT_TYPE = "summary"


@dataclass
class SummaryReport:
    ts: str
    headline: str
    summary: str
    report_path: str


def _to_float(value: Any, default: float | None = None) -> float | None:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except Exception:
        return default


def _fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:+.2%}"


def _fmt_money(value: float | None) -> str:
    return "n/a" if value is None else f"${value:,.2f}"


def _read_json(payload: str | None) -> dict:
    if not payload:
        return {}
    try:
        parsed = json.loads(payload)
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _market_frame(bots_payload: dict[str, dict]) -> pd.DataFrame:
    pieces = []
    for payload in bots_payload.values():
        df = equity_frame(payload.get("equity", []))
        if not df.empty and "spy" in df.columns:
            pieces.append(df[["spy"]].dropna())
    if not pieces:
        return pd.DataFrame()
    combined = pd.concat(pieces).sort_index()
    return combined[~combined.index.duplicated(keep="last")]


def _window_return(df: pd.DataFrame, column: str, window_key: str) -> float | None:
    if df.empty or column not in df.columns:
        return None
    filtered = filter_frame_to_window(df[[column]].dropna(), WINDOW_OPTIONS[window_key])
    if len(filtered) < 2:
        return None
    return pct_change(_to_float(filtered[column].iloc[-1]), _to_float(filtered[column].iloc[0]))


def _market_summary(bots_payload: dict[str, dict]) -> dict[str, Any]:
    frame = _market_frame(bots_payload)
    if frame.empty:
        return {
            "available": False,
            "summary": "Market benchmark data is not available in the current snapshots.",
            "returns": {},
            "vol_20d": None,
        }

    returns = {key: _window_return(frame, "spy", key) for key in ["24h", "7d", "28d", "90d"]}
    daily_returns = frame["spy"].pct_change().dropna().tail(20)
    vol_20d = float(daily_returns.std()) if len(daily_returns) >= 2 else None
    latest = _to_float(frame["spy"].iloc[-1])
    seven_day = returns.get("7d")
    if seven_day is None:
        tone = "Market benchmark direction is unclear from the available window."
    elif seven_day > 0.01:
        tone = "The market benchmark has been rising over the recent window."
    elif seven_day < -0.01:
        tone = "The market benchmark has been falling over the recent window."
    else:
        tone = "The market benchmark has been mostly range-bound over the recent window."

    return {
        "available": True,
        "latest_spy": latest,
        "returns": returns,
        "vol_20d": vol_20d,
        "summary": tone,
    }


def _decision_context(config: Config, bot_name: str) -> dict:
    row = read_latest_decision_run(config.db_path, bot_name=bot_name)
    return _read_json(row[3]) if row and row[3] else {}


def _recent_counts(config: Config, bot_name: str, days: int = 14) -> dict[str, int]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    decisions = read_recent_decision_logs(config.db_path, limit=500, bot_name=bot_name)
    selected = 0
    holds = 0
    total = 0
    for ts, _, side, is_selected, *_ in decisions:
        parsed = pd.to_datetime(ts, errors="coerce", utc=True)
        if pd.isna(parsed) or parsed.to_pydatetime() < cutoff:
            continue
        total += 1
        if int(is_selected):
            selected += 1
        if str(side).upper() == "HOLD":
            holds += 1

    trades = read_latest_trades(config.db_path, limit=500, bot_name=bot_name)
    recent_trades = 0
    for ts, *_ in trades:
        parsed = pd.to_datetime(ts, errors="coerce", utc=True)
        if not pd.isna(parsed) and parsed.to_pydatetime() >= cutoff:
            recent_trades += 1
    return {"total_decisions": total, "selected_decisions": selected, "holds": holds, "trades": recent_trades}


def _bot_payload(config: Config, bot_name: str) -> dict[str, Any]:
    equity_rows = list(reversed(read_latest_equity(config.db_path, limit=400, bot_name=bot_name)))
    position_rows = read_latest_positions(config.db_path, limit=500, bot_name=bot_name)
    trade_rows = list(reversed(read_latest_trades(config.db_path, limit=500, bot_name=bot_name)))
    decision_rows = read_recent_selected_decisions(config.db_path, limit=250, bot_name=bot_name)
    strategy_rows = read_latest_strategy_reports(config.db_path, limit=20, bot_name=bot_name)
    payload = {
        "label": bot_label(bot_name),
        "equity": [
            {"ts": row[0], "equity": row[1], "cash": row[2], "portfolio_value": row[3], "spy_value": row[4]}
            for row in equity_rows
        ],
        "positions": [
            {"symbol": row[0], "qty": row[1], "avg_entry_price": row[2], "market_value": row[3], "unrealized_pl": row[4]}
            for row in position_rows
        ],
        "trades": [
            {"ts": row[0], "symbol": row[1], "side": row[2], "qty": row[3], "price": row[4], "status": row[5]}
            for row in trade_rows
        ],
        "decisions": [
            {
                "ts": row[0],
                "symbol": row[1],
                "side": row[2],
                "base_score": row[3],
                "final_score": row[4],
                "components": _read_json(row[5]),
                "rationale": row[6],
                "evaluated_ts": row[7],
                "horizon_days": row[8],
                "realized_return": row[9],
                "signed_return": row[10],
                "beat_spy": row[11],
                "outcome_label": row[12],
            }
            for row in decision_rows
        ],
        "strategy_reports": [
            {
                "ts": row[0],
                "report_type": row[1],
                "headline": row[2],
                "summary": row[3],
                "body": row[4],
                "metrics": _read_json(row[5]),
                "changes": _read_json(row[6]),
            }
            for row in strategy_rows
        ],
    }
    return apply_model_revision(bot_name, payload)


def _diagnose_bot(
    config: Config,
    bot_name: str,
    payload: dict[str, Any],
    metrics: dict[str, Any],
    market: dict[str, Any],
) -> tuple[list[str], list[str], list[str]]:
    positives: list[str] = []
    issues: list[str] = []
    recommendations: list[str] = []
    label = payload.get("label") or bot_label(bot_name)
    counts = _recent_counts(config, bot_name)
    context = _decision_context(config, bot_name)
    market_7d = (market.get("returns") or {}).get("7d")
    window_return = metrics.get("window_return")
    window_alpha = metrics.get("window_alpha")
    win_rate = metrics.get("win_rate")
    avg_alpha = metrics.get("avg_trade_alpha")
    gross_exposure_pct = metrics.get("gross_exposure_pct")

    if window_return is not None and window_return > 0:
        positives.append(f"{label} produced a positive 7-day account return of {_fmt_pct(window_return)}.")
    if window_alpha is not None and window_alpha > 0:
        positives.append(f"{label} beat the benchmark over the 7-day window by {_fmt_pct(window_alpha)}.")
    if win_rate is not None and win_rate >= 0.55:
        positives.append(f"{label} has a recent evaluated-decision win rate of {_fmt_pct(win_rate)}.")

    if metrics.get("latest_equity") is None:
        issues.append(f"{label} has no equity snapshot yet, so performance cannot be evaluated.")
        recommendations.append(f"Run a snapshot/rebalance for {label} so the dashboard and summary report can score it.")
        return positives, issues, recommendations

    if window_alpha is not None and window_alpha < -0.01:
        issues.append(f"{label} lagged the benchmark by {_fmt_pct(window_alpha)} over the 7-day window.")
        recommendations.append(f"Review {label}'s latest selected decisions and consider tightening its active threshold if weak trades drove the lag.")

    if win_rate is not None and avg_alpha is not None and metrics.get("evaluated_decision_count", 0) >= 10:
        if win_rate < 0.4 and avg_alpha < -0.001:
            issues.append(f"{label} looks poorly calibrated: win rate {_fmt_pct(win_rate)} with average trade alpha {_fmt_pct(avg_alpha)}.")
            recommendations.append(f"Let champion/challenger tighten {label}'s threshold unless excluded trades are outperforming.")

    if gross_exposure_pct is not None and gross_exposure_pct < 0.02 and market_7d is not None and abs(market_7d) > 0.015:
        market_direction = "rising" if market_7d > 0 else "falling"
        issues.append(
            f"{label} was nearly uninvested while the benchmark was {market_direction} {_fmt_pct(market_7d)} over 7 days."
        )
        recommendations.append(f"Check whether {label}'s gate or risk overlay is too restrictive for the current market regime.")

    if counts["selected_decisions"] == 0 and counts["total_decisions"] >= 10 and market_7d is not None and abs(market_7d) > 0.015:
        issues.append(f"{label} generated no selected trades across {counts['total_decisions']} recent decisions despite a moving market.")
        recommendations.append(f"Review threshold calibration for {label}; persistent all-HOLD behavior can miss large benchmark moves.")

    if bot_name == LLM_BOT_NAME:
        gated = int(context.get("conviction_gated_count", 0) or 0)
        vetoed = 0
        skeptic_summary = context.get("skeptic_action_summary")
        if isinstance(skeptic_summary, dict):
            vetoed = int(skeptic_summary.get("vetoed_count", 0) or 0)
        if counts["selected_decisions"] == 0 and (gated or vetoed):
            issues.append(
                f"{label} appears over-constrained: {gated} conviction-gated and {vetoed} skeptic-vetoed decisions in the latest run."
            )
            recommendations.append(
                "Consider lowering `LLM_MIN_CONVICTION` slightly or disabling Skeptic veto authority temporarily if this persists through several moving-market sessions."
            )

    if bot_name == STAT_ARB_BOT_NAME:
        stat_context = context.get("stat_arb") if isinstance(context.get("stat_arb"), dict) else {}
        selected_pairs = int(context.get("selected_pair_count", 0) or 0)
        candidate_pairs = int(context.get("candidate_pair_count", 0) or 0)
        if candidate_pairs == 0:
            issues.append(f"{label} found no eligible pair candidates in the latest run.")
            recommendations.append("Check sector mapping, liquidity filters, and available price history for the Stat Arb universe.")
        elif selected_pairs == 0 and candidate_pairs > 20:
            issues.append(
                f"{label} screened {candidate_pairs} pairs but selected none; the z-score entry gate may be too strict for current dispersion."
            )
            recommendations.append(
                f"Let champion/challenger evaluate `STAT_ARB_ENTRY_Z` near {stat_context.get('entry_z', config.stat_arb_entry_z)} before relaxing it manually."
            )

    return positives, issues, recommendations


def _build_body(
    generated_at: str,
    market: dict[str, Any],
    rows: list[dict[str, Any]],
    positives: list[str],
    issues: list[str],
    recommendations: list[str],
    llm_narrative: dict[str, Any] | None,
) -> str:
    executive_summary = ""
    if llm_narrative:
        executive_summary = str(llm_narrative.get("executive_summary") or "").strip()
    if not executive_summary:
        issue_count = len(issues)
        if issue_count:
            executive_summary = f"The system has {issue_count} notable model or calibration issue(s) to monitor."
        else:
            executive_summary = "No major model-health issues were detected from the latest available snapshots."

    market_returns = market.get("returns") or {}
    lines = [
        "# All-Model Summary Report",
        "",
        f"Generated at {generated_at}",
        "",
        "## Executive Summary",
        executive_summary,
        "",
        "## Market Context",
        f"- {market.get('summary')}",
        f"- Benchmark latest value: {_fmt_money(market.get('latest_spy'))}.",
        f"- Benchmark returns: 24h {_fmt_pct(market_returns.get('24h'))}, 7d {_fmt_pct(market_returns.get('7d'))}, 28d {_fmt_pct(market_returns.get('28d'))}, 90d {_fmt_pct(market_returns.get('90d'))}.",
        f"- Recent benchmark volatility proxy: {_fmt_pct(market.get('vol_20d'))}.",
        "",
        "## Model Performance Table",
        "| Model | 7d return | 7d vs benchmark | Win rate | Avg trade alpha | Gross exposure | Recent trades |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {label} | {ret} | {alpha} | {win} | {trade_alpha} | {gross} | {trades} |".format(
                label=row["label"],
                ret=_fmt_pct(row.get("window_return")),
                alpha=_fmt_pct(row.get("window_alpha")),
                win=_fmt_pct(row.get("win_rate")),
                trade_alpha=_fmt_pct(row.get("avg_trade_alpha")),
                gross=_fmt_pct(row.get("gross_exposure_pct")),
                trades=int(row.get("recent_trades", 0)),
            )
        )
    lines.extend(["", "## What Went Well"])
    lines.extend([f"- {item}" for item in positives] or ["- No clear positive outlier was detected yet."])
    lines.extend(["", "## What Went Poorly Or Looks Abnormal"])
    lines.extend([f"- {item}" for item in issues] or ["- No major abnormal model behavior was detected."])
    lines.extend(["", "## Suggested Corrections"])
    lines.extend([f"- {item}" for item in recommendations] or ["- Keep collecting outcomes; no immediate threshold or authority change is indicated."])

    if llm_narrative:
        raw_notes = llm_narrative.get("additional_notes", [])
        if isinstance(raw_notes, str):
            raw_notes = [raw_notes]
        extra_notes = [str(item).strip() for item in raw_notes if str(item).strip()]
        if extra_notes:
            lines.extend(["", "## Narrative Notes"])
            lines.extend([f"- {item}" for item in extra_notes[:6]])
    return "\n".join(lines)


def generate_summary_report(config: Config) -> SummaryReport:
    discovered = set(BOT_LABELS) | set(configured_bot_names(config))
    try:
        discovered.update(read_available_bot_names(config.db_path))
    except Exception:
        pass
    bot_names = sorted(discovered)
    bots_payload = {bot_name: _bot_payload(config, bot_name) for bot_name in bot_names}
    market = _market_summary(bots_payload)

    rows: list[dict[str, Any]] = []
    positives: list[str] = []
    issues: list[str] = []
    recommendations: list[str] = []
    equity_frames = [equity_frame(payload.get("equity", [])) for payload in bots_payload.values()]
    anchor = max((frame.index.max() for frame in equity_frames if not frame.empty), default=None)
    for bot_name, payload in bots_payload.items():
        metrics = bot_performance_metrics(payload, WINDOW_OPTIONS["7d"], anchor)
        counts = _recent_counts(config, bot_name)
        bot_positives, bot_issues, bot_recs = _diagnose_bot(config, bot_name, payload, metrics, market)
        positives.extend(bot_positives)
        issues.extend(bot_issues)
        recommendations.extend(bot_recs)
        rows.append(
            {
                "bot_name": bot_name,
                "label": payload.get("label") or bot_label(bot_name),
                "recent_trades": counts["trades"],
                **metrics,
            }
        )

    rows.sort(key=lambda row: row.get("window_return") if row.get("window_return") is not None else -999, reverse=True)
    payload = {
        "market": market,
        "models": rows,
        "positives": positives[:12],
        "issues": issues[:12],
        "recommendations": recommendations[:12],
    }
    llm_narrative = call_json_llm(
        config,
        system_prompt=(
            "You are writing a concise all-model paper-trading summary report. "
            "Use only the supplied metrics. Diagnose abnormal model behavior concretely and avoid generic trading advice. "
            "Return JSON with executive_summary and additional_notes."
        ),
        payload=payload,
        max_output_tokens=1000,
    )

    ts = datetime.now(timezone.utc).isoformat()
    body = _build_body(ts, market, rows, positives[:12], issues[:12], recommendations[:12], llm_narrative)
    scored_rows = [row for row in rows if row.get("window_return") is not None]
    best = scored_rows[0]["label"] if scored_rows else "n/a"
    issue_count = len(issues)
    summary = f"Reviewed {len(rows)} model(s). Best 7-day model: {best}. Flagged {issue_count} issue(s)."
    reports_dir = Path(config.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"summary_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(body, encoding="utf-8")
    metrics = {
        "model_count": float(len(rows)),
        "issue_count": float(issue_count),
        "market_7d_return": (market.get("returns") or {}).get("7d"),
        "market_28d_return": (market.get("returns") or {}).get("28d"),
    }
    changes = {
        "recommendations": recommendations[:12],
        "issues": issues[:12],
        "schedule": "daily_after_market_close",
    }
    log_strategy_report(
        config.db_path,
        ts,
        SUMMARY_REPORT_TYPE,
        "All-Model Summary Report",
        summary,
        body,
        json.dumps(metrics, sort_keys=True),
        json.dumps(changes, sort_keys=True),
        bot_name=ML_BOT_NAME,
    )
    return SummaryReport(ts=ts, headline="All-Model Summary Report", summary=summary, report_path=str(report_path))
