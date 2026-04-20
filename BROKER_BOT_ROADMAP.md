# Broker Bot Roadmap

This project is now organized into four practical phases so the bot can improve without turning into an opaque science experiment.

## Phase 1: Working Ensemble Bot

Goal: Get a paper-trading bot that can act, explain itself, and learn from its own results.

- Train the baseline Random Forest model.
- Blend that model with bounded overlays from:
  - Alpaca market movers
  - Alpaca most-active symbols
  - Alpaca snapshots
  - Alpaca news headlines
  - symbol-level memory from past decisions
  - optional LLM candidate review
- Log every decision with rationale and component contributions.
- Evaluate mature decisions after the prediction horizon passes.
- Update learned ensemble weights in `data/learned_policy.json`.
- Generate learning and strategy reports in `data/reports/`.

Status: Implemented in the current codebase.

## Phase 2: Better Research Inputs

Goal: Improve idea quality before the bot places trades.

- Add richer universe selection beyond static S&P 500 membership.
- Add sector and industry metadata to memory and reporting.
- Ingest earnings dates, analyst changes, or fundamentals from an approved source.
- Add a structured watchlist pipeline that narrows the universe before scoring.

## Phase 3: Better Validation

Goal: Make sure changes are actually helping and not just sounding sophisticated.

- Backtest the ensemble overlays, not just the base Random Forest.
- Track performance by regime:
  - bull markets
  - bear markets
  - high-volatility periods
  - low-volatility periods
- Compare live paper-trading outcomes with backtest expectations.
- Add tests around decision logging, evaluation, and learned-policy updates.

## Phase 4: Smarter Automation

Goal: Make the system feel like a disciplined research assistant.

- Schedule `review-decisions`, `advisor-report`, and `strategy-report` automatically.
- Surface strategy reports in the dashboard UI.
- Add alerts for unusual behavior:
  - no trades placed
  - repeated rejected orders
  - falling hit rate
  - sudden drawdown spike
- Add guardrails before any future move from paper trading toward real trading.
