from __future__ import annotations

from copy import deepcopy
from typing import Any

from .behavior_revisions import (
    CURRENT_BEHAVIOR_REVISION,
    CURRENT_BEHAVIOR_REVISION_DATE,
    behavior_revision_history,
    validate_behavior_revisions,
)


STRATEGY_BLUEPRINT: dict[str, Any] = {
    "title": "Fresh-Start Strategy",
    "revision": CURRENT_BEHAVIOR_REVISION,
    "revision_date": CURRENT_BEHAVIOR_REVISION_DATE,
    "summary": (
        "Broker Bot is now presented as one fresh-start paper-trading champion: a broad-universe base model with risk controls, evidence logging, and supervisor reports. "
        "Older model families and revision history are hidden from the operating dashboard."
    ),
    "models": [
        {
            "name": "Broker Bot",
            "role": "Fresh-start champion",
            "description": (
                "The current model ranks liquid S&P 500 stocks with a supervised one-day return model, then sizes the selected book through shared risk controls."
            ),
            "strategies": [
                "Trades only from the refreshed S&P 500 universe and sector map.",
                "Keeps learned overlays at zero weight until fresh evaluated outcomes justify reintroducing them.",
                "Uses inverse-volatility target weights with sector, correlation, drawdown, shortability, and broker-side protection checks.",
                "Logs decisions, reports, positions, equity, and outcomes so future changes are based on evidence.",
                "Requires out-of-sample model evaluation before trusting new policy changes.",
            ],
        },
    ],
    "shared_layers": [
        "Snapshots keep the dashboard fresh without placing trades.",
        "Rebalance commands remain paper-trading actions and pass through the same risk/execution layer.",
        "Caretaker runs can attach broker-side trailing stops to compatible whole-share positions and enforce an optional daily drawdown kill switch.",
        "Summary and Supervisor reports monitor calibration, data freshness, exposure, and abnormal behavior.",
    ],
    "current_safety_posture": [
        "Paper trading only.",
        "Broad universe and sector map are checked by the foundation audit.",
        "Overlay weights are quarantined at zero until fresh evidence supports reintroduction.",
        "Confidence gates, sector caps, correlation caps, volatility targeting, drawdown controls, and broker-side exit protection reduce runaway behavior.",
        "Supervisor policy changes require repeated report findings, cooldown periods, and an audit trail.",
    ],
    "changelog": behavior_revision_history(),
}


def get_strategy_blueprint() -> dict[str, Any]:
    validate_behavior_revisions()
    return deepcopy(STRATEGY_BLUEPRINT)
