from __future__ import annotations

from copy import deepcopy
from typing import Any


STRATEGY_BLUEPRINT: dict[str, Any] = {
    "title": "Strategy Blueprint",
    "revision": "2.7.0",
    "revision_date": "2026-04-30",
    "summary": (
        "Broker Bot is a paper-trading research system with two competing bots: an ML ensemble bot and an LLM decision-network bot. "
        "Both bots use separate brokerage paper accounts, shared risk controls, broker-side protection where possible, and post-trade learning reports."
    ),
    "models": [
        {
            "name": "ML Bot",
            "role": "Quantitative champion",
            "description": (
                "The ML Bot starts with a supervised return model and then applies bounded research overlays before portfolio construction."
            ),
            "strategies": [
                "Predicts short-horizon returns from momentum, volatility, liquidity, and market-context features.",
                "Uses an ensemble-style model stack with tree models, boosting, and a linear challenger.",
                "Adds bounded overlays from brokerage-service snapshots, mover/activity screens, recent news, symbol memory, and optional LLM review.",
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
    ],
    "shared_layers": [
        "Separate brokerage paper credentials allow ML and LLM bot equity curves to be compared cleanly.",
        "Rebalance runs can submit paper orders, while snapshot and caretaker runs update dashboard data and protection status.",
        "Caretaker runs can attach broker-side trailing stops to compatible whole-share positions and can enforce an optional daily drawdown kill switch.",
        "Learning reports evaluate mature decisions, calculate signed returns, compare against SPY, and update bounded learned-policy weights.",
        "Champion/Challenger reports compare the current live policy against stricter shadow policies before changing strategy behavior.",
        "Options reports are currently planning-only scaffolds for defined-risk vertical spread ideas; they are not live options execution.",
    ],
    "current_safety_posture": [
        "Paper trading only.",
        "LLM outputs are sanitized and bounded before they affect sizing or decisions.",
        "The LLM Skeptic can block trades before execution when evidence quality or upside/downside is poor.",
        "Confidence gates, sector caps, correlation caps, volatility targeting, drawdown controls, and broker-side exit protection reduce runaway behavior.",
        "Champion/challenger evaluation is shadow-only until enough evidence supports promotion.",
    ],
    "changelog": [
        {
            "revision": "2.7.0",
            "date": "2026-04-30",
            "title": "Navigation and readability pass",
            "changes": [
                "Added left-side dashboard navigation for major cockpit, report, and history sections.",
                "Grouped dashboard controls and status details so the active bot, data freshness, and revision are visible while scrolling.",
                "Tightened the dashboard layout to reduce visual noise and make long reports easier to browse.",
                "Continued replacing vendor-facing dashboard language with generic brokerage-service wording.",
            ],
        },
        {
            "revision": "2.6.0",
            "date": "2026-04-30",
            "title": "Strategy Blueprint and historical explainability",
            "changes": [
                "Added this Strategy Blueprint panel with revision history and model explanations.",
                "Made the dashboard default to a 14-day graph window.",
                "Added historical Champion/Challenger dashboard browsing.",
                "Made LLM Coach feedback more ticker-specific and less generic.",
            ],
        },
        {
            "revision": "2.5.0",
            "date": "2026-04-30",
            "title": "Skeptic and strategy evaluation layer",
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
            "changes": [
                "Added lightweight caretaker commands and workflow.",
                "Added broker-side trailing-stop protection checks.",
                "Added optional same-day drawdown kill switch.",
            ],
        },
        {
            "revision": "2.3.0",
            "date": "2026-04-28",
            "title": "Dashboard cockpit",
            "changes": [
                "Added multi-bot dashboard trend comparisons.",
                "Added indexed vs actual holding value graph mode.",
                "Added holdings ring chart, decision explorer, and protection summaries.",
            ],
        },
        {
            "revision": "2.2.0",
            "date": "2026-04-24",
            "title": "Second paper account and LLM bot",
            "changes": [
                "Separated ML and LLM bots into distinct brokerage paper accounts.",
                "Added LLM Stock Selector, Analyst, Trader, and Coach reports.",
                "Added separate LLM equity, positions, trades, decisions, and reports in the dashboard.",
            ],
        },
        {
            "revision": "2.1.0",
            "date": "2026-04-23",
            "title": "Learning and research reports",
            "changes": [
                "Added richer strategy, watchlist, and learning reports.",
                "Added deep research notes for current watchlist names.",
                "Added decision outcome logging for later learning.",
            ],
        },
        {
            "revision": "2.0.0",
            "date": "2026-04-22",
            "title": "Cloud paper-trading baseline",
            "changes": [
                "Added GitHub Actions cloud runs.",
                "Added dashboard snapshot generation for Streamlit.",
                "Added model training, rebalance, snapshot, advisor, and strategy report automation.",
            ],
        },
    ],
}


def get_strategy_blueprint() -> dict[str, Any]:
    return deepcopy(STRATEGY_BLUEPRINT)
