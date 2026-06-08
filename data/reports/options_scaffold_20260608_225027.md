# Options Scaffold Report

Generated at: 2026-06-08T22:50:27.859155+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.30% and final score -0.54%
- Underlying spot: $585.25
- Expiry: 2026-06-26
- Long leg: `META260626P00585000` at strike $585.00 using recent close $16.26
- Short leg: `META260626P00555000` at strike $555.00 using recent close $7.10
- Estimated net debit: $9.16
- Max loss: $9.16
- Max profit: $20.84
- Breakeven at expiry: $575.84
- Reward/risk estimate: 2.28x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0019; memory -0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.32% and final score -0.45%
- Underlying spot: $208.66
- Expiry: 2026-06-26
- Long leg: `NVDA260626P00210000` at strike $210.00 using recent close $10.67
- Short leg: `NVDA260626P00200000` at strike $200.00 using recent close $5.60
- Estimated net debit: $5.07
- Max loss: $5.07
- Max profit: $4.93
- Breakeven at expiry: $204.93
- Reward/risk estimate: 0.97x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0020; snapshot +0.0006

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.06% and final score -0.36%
- Underlying spot: $245.21
- Expiry: 2026-06-26
- Long leg: `AMZN260626P00245000` at strike $245.00 using recent close $6.94
- Short leg: `AMZN260626P00235000` at strike $235.00 using recent close $3.35
- Estimated net debit: $3.59
- Max loss: $3.59
- Max profit: $6.41
- Breakeven at expiry: $241.41
- Reward/risk estimate: 1.79x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0028

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## XOM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.00% and final score 0.31%
- Underlying spot: $151.85
- Expiry: 2026-06-26
- Long leg: `XOM260626C00150000` at strike $150.00 using recent close $4.85
- Short leg: `XOM260626C00160000` at strike $160.00 using recent close $1.46
- Estimated net debit: $3.39
- Max loss: $3.39
- Max profit: $6.61
- Breakeven at expiry: $153.39
- Reward/risk estimate: 1.95x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0027; snapshot +0.0006

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.03% and final score -0.28%
- Underlying spot: $363.44
- Expiry: 2026-06-26
- Long leg: `GOOGL260626P00365000` at strike $365.00 using recent close $10.50
- Short leg: `GOOGL260626P00345000` at strike $345.00 using recent close $3.43
- Estimated net debit: $7.07
- Max loss: $7.07
- Max profit: $12.93
- Breakeven at expiry: $357.93
- Reward/risk estimate: 1.83x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0023

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## JPM — Bull Call Debit Spread

- Signal: LONG idea with base score -0.06% and final score 0.28%
- Underlying spot: $311.11
- Expiry: 2026-06-26
- Long leg: `JPM260626C00310000` at strike $310.00 using recent close $9.75
- Short leg: `JPM260626C00325000` at strike $325.00 using recent close $3.18
- Estimated net debit: $6.57
- Max loss: $6.57
- Max profit: $8.43
- Breakeven at expiry: $316.57
- Reward/risk estimate: 1.28x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0031

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
