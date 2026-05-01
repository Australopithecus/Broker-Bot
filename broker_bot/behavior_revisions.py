from __future__ import annotations

from copy import deepcopy
from typing import Any


CURRENT_BEHAVIOR_REVISION = "2.7.0"
CURRENT_BEHAVIOR_REVISION_DATE = "2026-05-01"

BEHAVIOR_REVISION_HISTORY: list[dict[str, Any]] = [
    {
        "revision": "2.7.0",
        "date": "2026-05-01",
        "title": "ML Bot R2 learned overlays",
        "models": ["ML Bot"],
        "changes": [
            "Added walk-forward model evaluation for out-of-sample directional accuracy, return, and overlay impact.",
            "Promoted the ML model behavior to ML Bot R2 with learned component reliability scales for snapshot, technical, and memory signals.",
            "Added model revision metadata to dashboard comparison payloads, reports, and snapshot generation.",
        ],
    },
    {
        "revision": "2.6.0",
        "date": "2026-04-30",
        "title": "Ticker-specific LLM Coach feedback",
        "models": ["LLM Bot"],
        "changes": [
            "Changed the LLM Coach feedback style from generic advice to ticker-specific wins, mistakes, and next-action guidance.",
            "Fed more concrete Coach lessons back into the LLM Trader context so future decisions can adapt to prior outcomes.",
        ],
    },
    {
        "revision": "2.5.0",
        "date": "2026-04-30",
        "title": "Skeptic and strategy evaluation layer",
        "models": ["ML Bot", "LLM Bot"],
        "changes": [
            "Added LLM Skeptic review before LLM Trader decisions reach execution.",
            "Added ML confidence gating and LLM conviction gating.",
            "Added post-trade attribution reports.",
            "Added Champion/Challenger shadow evaluation reports.",
        ],
    },
    {
        "revision": "2.4.0",
        "date": "2026-04-29",
        "title": "Market-hours caretaker",
        "models": ["ML Bot", "LLM Bot"],
        "changes": [
            "Added lightweight caretaker commands and workflow.",
            "Added broker-side trailing-stop protection checks.",
            "Added optional same-day drawdown kill switch.",
        ],
    },
    {
        "revision": "2.2.0",
        "date": "2026-04-24",
        "title": "Second paper account and LLM bot",
        "models": ["LLM Bot"],
        "changes": [
            "Separated ML and LLM bots into distinct brokerage paper accounts.",
            "Added LLM Stock Selector, Analyst, Trader, and Coach reports.",
            "Enabled ML and LLM bots to generate independent decisions and outcomes for direct performance comparison.",
        ],
    },
    {
        "revision": "2.1.0",
        "date": "2026-04-23",
        "title": "Learning and research reports",
        "models": ["ML Bot"],
        "changes": [
            "Added richer strategy, watchlist, and learning reports.",
            "Added deep research notes for current watchlist names.",
            "Added decision outcome logging for later learning.",
        ],
    },
    {
        "revision": "2.0.0",
        "date": "2026-04-22",
        "title": "Paper-trading automation baseline",
        "models": ["ML Bot"],
        "changes": [
            "Added model training and rebalance commands for automated paper-trading decisions.",
            "Added advisor and strategy report automation to explain generated decisions.",
            "Added snapshot generation so model outcomes could feed later learning and review loops.",
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
