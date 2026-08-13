from __future__ import annotations

from copy import deepcopy
from typing import Any


CURRENT_BEHAVIOR_REVISION = "4.0.0"
CURRENT_BEHAVIOR_REVISION_DATE = "2026-08-13"

BEHAVIOR_REVISION_HISTORY: list[dict[str, Any]] = [
    {
        "revision": "4.0.0",
        "date": "2026-08-13",
        "title": "Fresh-start base model",
        "models": ["Broker Bot"],
        "changes": [
            "Reset the dashboard and visible model metadata around one fresh-start champion model.",
            "Expanded the trading universe to the current S&P 500 with sector mapping.",
            "Quarantined learned overlays after broad-universe out-of-sample validation showed the base model was stronger.",
            "Kept risk controls, evidence logging, model evaluation, Summary, and Supervisor reports as the operating guardrails.",
        ],
    },
]


def behavior_revision_history() -> list[dict[str, Any]]:
    return deepcopy(BEHAVIOR_REVISION_HISTORY)


def latest_behavior_revision() -> dict[str, Any]:
    return deepcopy(BEHAVIOR_REVISION_HISTORY[0])


def validate_behavior_revisions() -> None:
    if not BEHAVIOR_REVISION_HISTORY:
        raise ValueError("At least one bot behavior revision is required.")
    latest = BEHAVIOR_REVISION_HISTORY[0]
    if latest.get("revision") != CURRENT_BEHAVIOR_REVISION:
        raise ValueError("CURRENT_BEHAVIOR_REVISION must match the newest behavior revision entry.")
    if latest.get("date") != CURRENT_BEHAVIOR_REVISION_DATE:
        raise ValueError("CURRENT_BEHAVIOR_REVISION_DATE must match the newest behavior revision entry.")
    seen: set[str] = set()
    for entry in BEHAVIOR_REVISION_HISTORY:
        revision = str(entry.get("revision") or "")
        if not revision:
            raise ValueError("Every bot behavior revision needs a revision number.")
        if revision in seen:
            raise ValueError(f"Duplicate bot behavior revision: {revision}")
        seen.add(revision)
        for field in ("date", "title"):
            if not str(entry.get(field) or "").strip():
                raise ValueError(f"Revision {revision} is missing {field}.")
        if not entry.get("models"):
            raise ValueError(f"Revision {revision} must list which model behavior changed.")
        if not entry.get("changes"):
            raise ValueError(f"Revision {revision} must describe what changed.")
