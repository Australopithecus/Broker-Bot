# Options Scaffold Report

Generated at: 2026-05-25T22:17:59.274127+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.19% and final score 0.73%
- Underlying spot: $308.81
- Expiry: 2026-06-12
- Long leg: `AAPL260612C00310000` at strike $310.00 using recent close $6.40
- Short leg: `AAPL260612C00325000` at strike $325.00 using recent close $1.50
- Estimated net debit: $4.90
- Max loss: $4.90
- Max profit: $10.10
- Breakeven at expiry: $314.90
- Reward/risk estimate: 2.06x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0051

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.09% and final score 0.31%
- Underlying spot: $388.55
- Expiry: 2026-06-12
- Long leg: `UNH260612C00390000` at strike $390.00 using recent close $9.20
- Short leg: `UNH260612C00410000` at strike $410.00 using recent close $2.63
- Estimated net debit: $6.57
- Max loss: $6.57
- Max profit: $13.43
- Breakeven at expiry: $396.57
- Reward/risk estimate: 2.04x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0019

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.31% and final score -0.28%
- Underlying spot: $215.34
- Expiry: 2026-06-12
- Long leg: `NVDA260612P00215000` at strike $215.00 using recent close $7.34
- Short leg: `NVDA260612P00205000` at strike $205.00 using recent close $3.49
- Estimated net debit: $3.85
- Max loss: $3.85
- Max profit: $6.15
- Breakeven at expiry: $211.15
- Reward/risk estimate: 1.60x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0010; screener +0.0013

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## JPM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.22% and final score 0.26%
- Underlying spot: $306.34
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

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.22% and final score -0.10%
- Underlying spot: $610.42
- Expiry: 2026-06-12
- Long leg: `META260612P00610000` at strike $610.00 using recent close $16.20
- Short leg: `META260612P00580000` at strike $580.00 using recent close $5.52
- Estimated net debit: $10.68
- Max loss: $10.68
- Max profit: $19.32
- Breakeven at expiry: $599.32
- Reward/risk estimate: 1.81x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0031

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.04% and final score 0.10%
- Underlying spot: $266.27
- Expiry: 2026-06-12
- Long leg: `AMZN260612C00265000` at strike $265.00 using recent close $8.80
- Short leg: `AMZN260612C00280000` at strike $280.00 using recent close $2.57
- Estimated net debit: $6.23
- Max loss: $6.23
- Max profit: $8.77
- Breakeven at expiry: $271.23
- Reward/risk estimate: 1.41x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0008

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
