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
        "Broker Bot is a paper-trading research system with three active competing models: an ML ensemble model, an LLM decision-network model, and an AI-designed adaptive model. "
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
                "Trader converts those reports into structured LONG/SHORT/HOLD decisions with conviction and expected upside/downside, targeting a small number of actionable paper trades when evidence is usable.",
                "Skeptic challenges each Trader decision, usually reducing conviction rather than blocking activity, and reserves hard vetoes for invalid, contradictory, or materially negative-edge setups.",
                "Coach reviews mature outcomes and feeds concrete ticker-specific lessons back into the next Trader prompt.",
            ],
        },
        {
            "name": "AI Lab Bot R1",
            "role": "Autonomous design challenger",
            "description": (
                "The AI Lab Bot is the open-ended experimental model: it uses an AI-designed adaptive sleeve ensemble and updates its own policy weights from outcomes."
            ),
            "strategies": [
                "Scores stocks with trend, short-term reversal, breakout, volume-confirmation, low-volatility, and market-regime alignment sleeves.",
                "Blends those sleeves into a composite long/short score using weights stored in `data/ai_lab_policy.json`.",
                "Updates sleeve weights and its minimum entry score from mature decision outcomes, with bounded changes and an audit trail.",
                "Uses a small controlled-exploration budget for near-threshold paper trades so the model can learn from borderline setups.",
                "Uses the same downstream execution, risk, sector/correlation, drawdown, and broker-side protection controls as the other bots.",
                "Reports the current policy, selected ideas, and self-updates after every rebalance.",
            ],
        },
    ],
    "shared_layers": [
        "Separate brokerage paper credentials allow ML, LLM, and AI Lab bot equity curves to be compared cleanly within the three-account paper limit.",
        "Rebalance runs can submit paper orders, while snapshot and caretaker runs update dashboard data and protection status.",
        "Caretaker runs can attach broker-side trailing stops to compatible whole-share positions and can enforce an optional daily drawdown kill switch.",
        "Learning reports evaluate mature decisions, calculate signed returns, compare against SPY, and update bounded learned-policy weights.",
        "Model evaluation reports score walk-forward out-of-sample folds before a model revision is trusted on the dashboard.",
        "Champion/Challenger reports compare the current live policy against stricter shadow policies and can write bounded threshold adjustments when enough evaluated evidence supports the change.",
        "Supervisor reports consolidate Summary, Coach, attribution, and Champion/Challenger evidence before applying any cross-model policy adaptation.",
        "AI Lab policy reports expose self-updated sleeve weights so the experimental model can evolve without changing source code.",
        "Options reports are currently planning-only scaffolds for defined-risk vertical spread ideas; they are not live options execution.",
    ],
    "current_safety_posture": [
        "Paper trading only.",
        "LLM outputs are sanitized and bounded before they affect sizing or decisions.",
        "The LLM Skeptic can reduce conviction before execution and can block trades only when evidence quality or upside/downside is clearly invalid.",
        "Confidence gates, sector caps, correlation caps, volatility targeting, drawdown controls, and broker-side exit protection reduce runaway behavior.",
        "Champion/challenger threshold promotion stays bounded and requires enough evaluated evidence before future runs use a changed gate.",
        "Supervisor policy changes require repeated Summary Report findings, cooldown periods, and an audit trail in the policy file.",
    ],
    "changelog": behavior_revision_history(),
}


def get_strategy_blueprint() -> dict[str, Any]:
    validate_behavior_revisions()
    return deepcopy(STRATEGY_BLUEPRINT)
