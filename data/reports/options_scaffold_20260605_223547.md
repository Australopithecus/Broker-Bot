# Options Scaffold Report

Generated at: 2026-06-05T22:35:47.618050+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.32% and final score -0.71%
- Underlying spot: $592.85
- Expiry: 2026-06-26
- Long leg: `META260626P00595000` at strike $595.00 using recent close $7.47
- Short leg: `META260626P00565000` at strike $565.00 using recent close $2.62
- Estimated net debit: $4.85
- Max loss: $4.85
- Max profit: $25.15
- Breakeven at expiry: $590.15
- Reward/risk estimate: 5.19x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0023; snapshot -0.0013; memory -0.0003

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## PG — Bull Call Debit Spread

- Signal: LONG idea with base score 0.41% and final score 0.68%
- Underlying spot: $146.49
- Expiry: 2026-06-26
- Long leg: `PG260626C00146000` at strike $146.00 using recent close $0.88
- Short leg: `PG260626C00152500` at strike $152.50 using recent close $0.30
- Estimated net debit: $0.58
- Max loss: $0.58
- Max profit: $5.92
- Breakeven at expiry: $146.58
- Reward/risk estimate: 10.21x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0013; snapshot +0.0014

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.24% and final score 0.68%
- Underlying spot: $399.59
- Expiry: 2026-06-26
- Long leg: `UNH260626C00400000` at strike $400.00 using recent close $9.40
- Short leg: `UNH260626C00420000` at strike $420.00 using recent close $3.35
- Estimated net debit: $6.05
- Max loss: $6.05
- Max profit: $13.95
- Breakeven at expiry: $406.05
- Reward/risk estimate: 2.31x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0042

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## JPM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.21% and final score 0.48%
- Underlying spot: $312.38
- Expiry: 2026-06-26
- Long leg: `JPM260626C00310000` at strike $310.00 using recent close $8.50
- Short leg: `JPM260626C00325000` at strike $325.00 using recent close $2.61
- Estimated net debit: $5.89
- Max loss: $5.89
- Max profit: $9.11
- Breakeven at expiry: $315.89
- Reward/risk estimate: 1.55x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0025

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.27% and final score -0.47%
- Underlying spot: $205.17
- Expiry: 2026-06-26
- Long leg: `NVDA260626P00205000` at strike $205.00 using recent close $2.82
- Short leg: `NVDA260626P00195000` at strike $195.00 using recent close $1.20
- Estimated net debit: $1.62
- Max loss: $1.62
- Max profit: $8.38
- Breakeven at expiry: $203.38
- Reward/risk estimate: 5.17x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0014; snapshot -0.0018; screener +0.0012

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.06% and final score -0.47%
- Underlying spot: $246.15
- Expiry: 2026-06-26
- Long leg: `AMZN260626P00245000` at strike $245.00 using recent close $3.65
- Short leg: `AMZN260626P00235000` at strike $235.00 using recent close $1.60
- Estimated net debit: $2.05
- Max loss: $2.05
- Max profit: $7.95
- Breakeven at expiry: $242.95
- Reward/risk estimate: 3.88x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0032; snapshot -0.0008

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
