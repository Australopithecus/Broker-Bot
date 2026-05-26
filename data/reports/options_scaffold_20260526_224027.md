# Options Scaffold Report

Generated at: 2026-05-26T22:40:27.197825+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.25% and final score 0.80%
- Underlying spot: $308.33
- Expiry: 2026-06-12
- Long leg: `AAPL260612C00310000` at strike $310.00 using recent close $6.40
- Short leg: `AAPL260612C00325000` at strike $325.00 using recent close $1.50
- Estimated net debit: $4.90
- Max loss: $4.90
- Max profit: $10.10
- Breakeven at expiry: $314.90
- Reward/risk estimate: 2.06x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0052

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.11% and final score 0.31%
- Underlying spot: $265.27
- Expiry: 2026-06-12
- Long leg: `AMZN260612C00265000` at strike $265.00 using recent close $8.80
- Short leg: `AMZN260612C00280000` at strike $280.00 using recent close $2.57
- Estimated net debit: $6.23
- Max loss: $6.23
- Max profit: $8.77
- Breakeven at expiry: $271.23
- Reward/risk estimate: 1.41x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0022

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.14% and final score 0.26%
- Underlying spot: $376.99
- Expiry: 2026-07-02
- Long leg: `UNH260702C00375000` at strike $375.00 using recent close $17.25
- Short leg: `UNH260702C00395000` at strike $395.00 using recent close $10.70
- Estimated net debit: $6.55
- Max loss: $6.55
- Max profit: $13.45
- Breakeven at expiry: $381.55
- Reward/risk estimate: 2.05x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0013

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## JPM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.12% and final score 0.17%
- Underlying spot: $306.82
- Expiry: 2026-06-12
- Long leg: `JPM260612C00305000` at strike $305.00 using recent close $8.23
- Short leg: `JPM260612C00320000` at strike $320.00 using recent close $2.14
- Estimated net debit: $6.09
- Max loss: $6.09
- Max profit: $8.91
- Breakeven at expiry: $311.09
- Reward/risk estimate: 1.46x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: No additional rationale captured.

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
