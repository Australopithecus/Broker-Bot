# Options Scaffold Report

Generated at: 2026-05-22T22:17:15.835613+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.25% and final score 0.78%
- Underlying spot: $308.81
- Expiry: 2026-06-05
- Long leg: `AAPL260605C00310000` at strike $310.00 using recent close $3.15
- Short leg: `AAPL260605C00325000` at strike $325.00 using recent close $0.40
- Estimated net debit: $2.75
- Max loss: $2.75
- Max profit: $12.25
- Breakeven at expiry: $312.75
- Reward/risk estimate: 4.45x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0051

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.05% and final score 0.27%
- Underlying spot: $388.55
- Expiry: 2026-06-05
- Long leg: `UNH260605C00387500` at strike $387.50 using recent close $6.75
- Short leg: `UNH260605C00407500` at strike $407.50 using recent close $1.54
- Estimated net debit: $5.21
- Max loss: $5.21
- Max profit: $14.79
- Breakeven at expiry: $392.71
- Reward/risk estimate: 2.84x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0019

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## JPM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.20% and final score 0.23%
- Underlying spot: $306.34
- Expiry: 2026-06-05
- Long leg: `JPM260605C00307500` at strike $307.50 using recent close $3.99
- Short leg: `JPM260605C00322500` at strike $322.50 using recent close $0.64
- Estimated net debit: $3.35
- Max loss: $3.35
- Max profit: $11.65
- Breakeven at expiry: $310.85
- Reward/risk estimate: 3.48x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: No additional rationale captured.

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.25% and final score -0.21%
- Underlying spot: $215.34
- Expiry: 2026-06-05
- Long leg: `NVDA260605P00215000` at strike $215.00 using recent close $4.92
- Short leg: `NVDA260605P00205000` at strike $205.00 using recent close $1.98
- Estimated net debit: $2.94
- Max loss: $2.94
- Max profit: $7.06
- Breakeven at expiry: $212.06
- Reward/risk estimate: 2.40x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0010; screener +0.0013

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
