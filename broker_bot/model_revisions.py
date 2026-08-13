from __future__ import annotations

from typing import Any

from .behavior_revisions import CURRENT_BEHAVIOR_REVISION
from .bots import ML_BOT_NAME, normalize_bot_name


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

    if normalized == ML_BOT_NAME:
        model_eval = _latest_report(reports, "model_eval")
        metrics = model_eval.get("metrics", {}) if model_eval else {}
        return {
            "id": "fresh-start-base-model",
            "label": "Fresh Start",
            "display_label": "Broker Bot",
            "name": "Base Model",
            "status": "active",
            "introduced_at": "2026-08-13",
            "behavior_revision": CURRENT_BEHAVIOR_REVISION,
            "summary": (
                model_eval.get("summary")
                if model_eval
                else "Fresh-start broad-universe base model with learned overlays quarantined until evidence improves."
            ),
            "base_label": "Broker Bot",
            "report_ts": model_eval.get("ts") if model_eval else None,
            "metrics": {
                "base_directional_accuracy": metrics.get("base_directional_accuracy"),
                "base_total_return": metrics.get("base_model_portfolio_total_return"),
                "learned_overlay_total_return": metrics.get("learned_overlays_portfolio_total_return"),
                "learned_overlay_selected_count": metrics.get("learned_overlays_selected_count"),
            },
        }

    return {
        "id": "retired-dashboard-model",
        "label": "Retired",
        "display_label": "Retired Model",
        "name": "Retired Dashboard Model",
        "status": "retired",
        "introduced_at": None,
        "behavior_revision": CURRENT_BEHAVIOR_REVISION,
        "summary": "Legacy model metadata is retired from the fresh-start dashboard.",
        "base_label": "Retired Model",
        "report_ts": None,
        "metrics": {},
    }


def apply_model_revision(bot_name: str | None, payload: dict[str, Any]) -> dict[str, Any]:
    revised = dict(payload)
    reports = revised.get("strategy_reports")
    if not isinstance(reports, list):
        reports = []
    revision = model_revision(bot_name, reports)
    revised["base_label"] = revision["base_label"]
    revised["revision"] = revision
    revised["label"] = revision["display_label"]
    return revised
