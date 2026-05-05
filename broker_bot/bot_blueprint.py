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
    "title": "Strategy Blueprint",
    "revision": CURRENT_BEHAVIOR_REVISION,
    "revision_date": CURRENT_BEHAVIOR_REVISION_DATE,
    "summary": (
        "Broker Bot is a paper-trading research system with three competing models: an ML ensemble model, an LLM decision-network model, and a statistical arbitrage model. "
        "Each model can use separate brokerage paper accounts, shared risk controls, broker-side protection where possible, and post-trade learning reports."
    ),
    "models": [
        {
            "name": "ML Bot R2",
            "role": "Quantitative champion",
            "description": (
                "The ML Bot R2 starts with a supervised return model and then applies bounded, learned research overlays before portfolio construction."
            ),
            "strategies": [
                "Predicts short-horizon returns from momentum, volatility, liquidity, and market-context features.",
                "Uses an ensemble-style model stack with tree models, boosting, and a linear challenger.",
                "Adds bounded overlays from brokerage-service snapshots, mover/activity screens, recent news, symbol memory, and optional LLM review.",
                "Uses learned component reliability scales from mature decision outcomes to avoid over-weighting weaker signal families.",
                "Applies a minimum absolute signal score gate so weak selected signals become HOLD before sizing.",
                "Uses inverse-volatility target weighting, SPY regime leverage, sector caps, correlation caps, and drawdown controls.",
            ],
        },
        {
            "name": "LLM Bot",
            "role": "Narrative/reasoning challenger",
            "description": (
                "The LLM Bot uses multiple LLM roles to turn the same market universe into explicit watchlist, analyst, trader, skeptic, and coach outputs."
            ),
            "strategies": [
                "Stock Selector chooses a concentrated watchlist from ranked candidates.",
                "Analyst writes stock-specific daily reports with catalysts, current events, contrary evidence, risks, and confidence.",
                "Trader converts those reports into structured LONG/SHORT/HOLD decisions with conviction and expected upside/downside.",
                "Skeptic challenges each Trader decision, can reduce conviction, and can veto weakly supported ideas.",
                "Coach reviews mature outcomes and feeds concrete ticker-specific lessons back into the next Trader prompt.",
            ],
        },
        {
            "name": "Stat Arb Bot R1",
            "role": "Relationship-trading challenger",
            "description": (
                "The Stat Arb Bot searches for highly correlated stock pairs whose hedge-ratio spread is unusually stretched, then trades mean reversion."
            ),
            "strategies": [
                "Filters the universe for liquid stocks with enough price history.",
                "Builds same-sector or fallback cross-sector pair candidates and requires a minimum return correlation.",
                "Estimates a hedge ratio from log prices, converts the pair spread into a z-score, and enters only when the spread is stretched.",
                "Trades long the relatively cheap leg and short the relatively rich leg, aiming for relationship normalization rather than directional market prediction.",
                "Writes pair-candidate reports and logs z-score/correlation components for later outcome review.",
            ],
        },
    ],
    "shared_layers": [
        "Separate brokerage paper credentials allow ML, LLM, and Stat Arb bot equity curves to be compared cleanly.",
        "Rebalance runs can submit paper orders, while snapshot and caretaker runs update dashboard data and protection status.",
        "Caretaker runs can attach broker-side trailing stops to compatible whole-share positions and can enforce an optional daily drawdown kill switch.",
        "Learning reports evaluate mature decisions, calculate signed returns, compare against SPY, and update bounded learned-policy weights.",
        "Model evaluation reports score walk-forward out-of-sample folds before a model revision is trusted on the dashboard.",
        "Champion/Challenger reports compare the current live policy against stricter shadow policies and can write bounded threshold adjustments when enough evaluated evidence supports the change.",
        "Options reports are currently planning-only scaffolds for defined-risk vertical spread ideas; they are not live options execution.",
    ],
    "current_safety_posture": [
        "Paper trading only.",
        "LLM outputs are sanitized and bounded before they affect sizing or decisions.",
        "The LLM Skeptic can block trades before execution when evidence quality or upside/downside is poor.",
        "Confidence gates, sector caps, correlation caps, volatility targeting, drawdown controls, and broker-side exit protection reduce runaway behavior.",
        "Champion/challenger threshold promotion stays bounded and requires enough evaluated evidence before future runs use a changed gate.",
    ],
    "changelog": behavior_revision_history(),
}


def get_strategy_blueprint() -> dict[str, Any]:
    validate_behavior_revisions()
    return deepcopy(STRATEGY_BLUEPRINT)
