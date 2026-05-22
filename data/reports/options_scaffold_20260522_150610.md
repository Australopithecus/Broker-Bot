# Options Scaffold Report

Generated at: 2026-05-22T15:06:10.712827+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.26% and final score 0.79%
- Underlying spot: $310.58
- Expiry: 2026-06-05
- Long leg: `AAPL260605C00310000` at strike $310.00 using recent close $3.15
- Short leg: `AAPL260605C00325000` at strike $325.00 using recent close $0.40
- Estimated net debit: $2.75
- Max loss: $2.75
- Max profit: $12.25
- Breakeven at expiry: $312.75
- Reward/risk estimate: 4.45x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0050

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.16% and final score 0.38%
- Underlying spot: $388.63
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

- Signal: LONG idea with base score 0.20% and final score 0.22%
- Underlying spot: $305.85
- Expiry: 2026-06-05
- Long leg: `JPM260605C00305000` at strike $305.00 using recent close $5.30
- Short leg: `JPM260605C00320000` at strike $320.00 using recent close $0.87
- Estimated net debit: $4.43
- Max loss: $4.43
- Max profit: $10.57
- Breakeven at expiry: $309.43
- Reward/risk estimate: 2.39x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: No additional rationale captured.

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.13% and final score 0.22%
- Underlying spot: $268.47
- Expiry: 2026-06-05
- Long leg: `AMZN260605C00267500` at strike $267.50 using recent close $7.00
- Short leg: `AMZN260605C00280000` at strike $280.00 using recent close $2.15
- Estimated net debit: $4.85
- Max loss: $4.85
- Max profit: $7.65
- Breakeven at expiry: $272.35
- Reward/risk estimate: 1.58x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0010

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
