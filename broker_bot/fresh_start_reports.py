from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any


FRESH_START_REPORT_TYPES = {"summary", "supervisor", "model_eval", "learning", "attribution", "strategy"}
FRESH_START_REPORT_CUTOFF = datetime(2026, 8, 13, tzinfo=timezone.utc)
FRESH_START_REPORT_CUTOFF_ISO = FRESH_START_REPORT_CUTOFF.isoformat()
REPORT_ARCHIVE_MESSAGE = (
    "Pre-fresh-start model evaluations and strategy reports remain archived in storage, "
    "but are hidden from dashboard and snapshot outputs."
)

_RETIRED_REPORT_MARKERS = [
    "All-Model",
    "all-model",
    "LLM Bot",
    "AI Lab Bot",
    "Stat Arb Bot",
    "Champion/Challenger",
    "champion/challenger",
    "ML/LLM",
]

_REPORT_REPLACEMENTS = [
    ("ML Bot R2", "Broker Bot"),
    ("ML Bot R1", "Broker Bot"),
    ("ML Bot", "Broker Bot"),
    ("without llm", "without review overlay"),
    ("without_llm", "without_review_overlay"),
    ("llm_adjustment", "review_adjustment"),
    ("LLM", "review overlay"),
]


def _report_text(report: dict[str, Any]) -> str:
    return "\n".join(str(report.get(key) or "") for key in ["headline", "summary", "body"])


def _parse_report_ts(raw_ts: Any) -> datetime | None:
    if not raw_ts:
        return None
    try:
        parsed = datetime.fromisoformat(str(raw_ts).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _is_fresh_start_report(report: dict[str, Any]) -> bool:
    parsed = _parse_report_ts(report.get("ts"))
    return parsed is not None and parsed >= FRESH_START_REPORT_CUTOFF


def _replace_text(value: Any) -> Any:
    if isinstance(value, str):
        updated = value
        for old, new in _REPORT_REPLACEMENTS:
            updated = updated.replace(old, new)
        return updated
    if isinstance(value, list):
        return [_replace_text(item) for item in value]
    if isinstance(value, dict):
        return {_replace_text(key): _replace_text(item) for key, item in value.items()}
    return value


def _fmt_pct(value: Any) -> str:
    try:
        return f"{float(value):+.2%}"
    except Exception:
        return "n/a"


def _fmt_num(value: Any) -> str:
    try:
        return f"{float(value):,.0f}"
    except Exception:
        return "n/a"


def _compact_report(report: dict[str, Any]) -> dict[str, Any]:
    report_type = report.get("report_type")
    if report_type not in {"model_eval", "learning"}:
        return report

    metrics = report.get("metrics") if isinstance(report.get("metrics"), dict) else {}
    if report_type == "model_eval":
        report["metrics"] = {
            "oos_symbol_days": metrics.get("oos_symbol_days"),
            "base_directional_accuracy": metrics.get("base_directional_accuracy"),
            "base_model_portfolio_total_return": metrics.get("base_model_portfolio_total_return"),
            "learned_overlays_portfolio_total_return": metrics.get("learned_overlays_portfolio_total_return"),
            "base_model_selected_count": metrics.get("base_model_selected_count"),
        }
        report["changes"] = {}
        report["body"] = "\n".join(
            [
                "# Broker Bot Model Evaluation",
                "",
                str(report.get("summary") or "Latest out-of-sample model evaluation."),
                "",
                "## Key Metrics",
                f"- Out-of-sample symbol-days: {_fmt_num(metrics.get('oos_symbol_days'))}.",
                f"- Directional accuracy: {_fmt_pct(metrics.get('base_directional_accuracy'))}.",
                f"- Base model total return: {_fmt_pct(metrics.get('base_model_portfolio_total_return'))}.",
                f"- Overlay stack total return: {_fmt_pct(metrics.get('learned_overlays_portfolio_total_return'))}.",
                f"- Selected observations: {_fmt_num(metrics.get('base_model_selected_count'))}.",
            ]
        )
    elif report_type == "learning":
        report["metrics"] = {
            "newly_evaluated": metrics.get("newly_evaluated"),
            "recent_hit_rate": metrics.get("recent_hit_rate"),
            "recent_avg_signed_return": metrics.get("recent_avg_signed_return"),
            "recent_avg_beat_spy": metrics.get("recent_avg_beat_spy"),
        }
        report["changes"] = {}
        report["body"] = "\n".join(
            [
                "# Broker Bot Learning Update",
                "",
                str(report.get("summary") or "Latest learning update."),
                "",
                "## Current Posture",
                "- Detailed component weights are kept out of the fresh-start dashboard until enough new outcomes accumulate.",
            ]
        )
    return report


def fresh_start_report_archive_note() -> dict[str, str]:
    return {
        "status": "archived",
        "cutoff": FRESH_START_REPORT_CUTOFF_ISO,
        "message": REPORT_ARCHIVE_MESSAGE,
    }


def fresh_start_strategy_reports(reports: list[dict[str, Any]] | None, limit: int | None = None) -> list[dict[str, Any]]:
    visible: list[dict[str, Any]] = []
    seen_types: set[str] = set()
    for report in reports or []:
        if not isinstance(report, dict):
            continue
        report_type = str(report.get("report_type") or "")
        if report_type not in FRESH_START_REPORT_TYPES:
            continue
        if report_type in seen_types:
            continue
        if not _is_fresh_start_report(report):
            continue
        text = _report_text(report)
        if any(marker in text for marker in _RETIRED_REPORT_MARKERS):
            continue
        visible.append(_compact_report(_replace_text(deepcopy(report))))
        seen_types.add(report_type)
        if limit is not None and len(visible) >= limit:
            break
    return visible
