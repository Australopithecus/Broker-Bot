from __future__ import annotations

from typing import Any

from .behavior_revisions import CURRENT_BEHAVIOR_REVISION
from .bots import LLM_BOT_NAME, ML_BOT_NAME, STAT_ARB_BOT_NAME, bot_label, normalize_bot_name


def _latest_report(reports: list[dict[str, Any]], report_type: str) -> dict[str, Any] | None:
    for report in reports:
        if report.get("report_type") == report_type:
            return report
    return None


def model_revision(
    bot_name: str | None,
    reports: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    normalized = normalize_bot_name(bot_name)
    reports = reports or []
    base_label = bot_label(normalized)

    if normalized == ML_BOT_NAME:
        model_eval = _latest_report(reports, "model_eval")
        metrics = model_eval.get("metrics", {}) if model_eval else {}
        return {
            "id": "ml-r2-learned-overlays",
            "label": "R2",
            "display_label": "ML Bot R2",
            "name": "Learned Overlays",
            "status": "active",
            "introduced_at": "2026-05-01",
            "behavior_revision": CURRENT_BEHAVIOR_REVISION,
            "summary": (
                model_eval.get("summary")
                if model_eval
                else "Out-of-sample model evaluation plus learned component reliability scales."
            ),
            "base_label": base_label,
            "report_ts": model_eval.get("ts") if model_eval else None,
            "metrics": {
                "base_directional_accuracy": metrics.get("base_directional_accuracy"),
                "base_total_return": metrics.get("base_model_portfolio_total_return"),
                "learned_overlay_total_return": metrics.get("learned_overlays_portfolio_total_return"),
                "learned_overlay_selected_count": metrics.get("learned_overlays_selected_count"),
            },
        }

    if normalized == STAT_ARB_BOT_NAME:
        stat_report = _latest_report(reports, "stat_arb_daily")
        metrics = stat_report.get("metrics", {}) if stat_report else {}
        return {
            "id": "stat-arb-r1-pairs-mean-reversion",
            "label": "R1",
            "display_label": "Stat Arb Bot R1",
            "name": "Pairs Mean Reversion",
            "status": "active",
            "introduced_at": "2026-05-04",
            "behavior_revision": CURRENT_BEHAVIOR_REVISION,
            "summary": (
                stat_report.get("summary")
                if stat_report
                else "Explicit statistical pairs strategy using correlation, hedge-ratio spreads, and z-score mean reversion."
            ),
            "base_label": base_label,
            "report_ts": stat_report.get("ts") if stat_report else None,
            "metrics": {
                "candidate_pair_count": metrics.get("candidate_pair_count"),
                "selected_pair_count": metrics.get("selected_pair_count"),
                "entry_z": metrics.get("entry_z"),
                "min_correlation": metrics.get("min_correlation"),
            },
        }

    return {
        "id": "llm-r1-multi-role",
        "label": "R1",
        "display_label": f"{base_label} R1",
        "name": "Multi-role LLM",
        "status": "active",
        "introduced_at": None,
        "behavior_revision": CURRENT_BEHAVIOR_REVISION,
        "summary": "Multi-role LLM selection, analysis, trading, and coaching workflow.",
        "base_label": base_label,
        "report_ts": None,
        "metrics": {},
    }


def apply_model_revision(bot_name: str | None, payload: dict[str, Any]) -> dict[str, Any]:
    revised = dict(payload)
    reports = revised.get("strategy_reports")
    if not isinstance(reports, list):
        reports = []
    revision = model_revision(bot_name, reports)
    revised["base_label"] = revised.get("base_label") or revision["base_label"]
    revised["revision"] = revision
    revised["label"] = revision["display_label"]
    return revised
