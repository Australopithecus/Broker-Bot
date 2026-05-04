# Options Scaffold Report

Generated at: 2026-05-04T22:15:59.560528+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.54% and final score 0.83%
- Underlying spot: $383.21
- Expiry: 2026-05-22
- Long leg: `GOOGL260522C00385000` at strike $385.00 using recent close $12.12
- Short leg: `GOOGL260522C00405000` at strike $405.00 using recent close $4.55
- Estimated net debit: $7.57
- Max loss: $7.57
- Max profit: $12.43
- Breakeven at expiry: $392.57
- Reward/risk estimate: 1.64x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0026

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.35% and final score 0.82%
- Underlying spot: $370.70
- Expiry: 2026-05-22
- Long leg: `UNH260522C00370000` at strike $370.00 using recent close $9.50
- Short leg: `UNH260522C00390000` at strike $390.00 using recent close $2.73
- Estimated net debit: $6.77
- Max loss: $6.77
- Max profit: $13.23
- Breakeven at expiry: $376.77
- Reward/risk estimate: 1.95x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0036; snapshot +0.0006; memory +0.0006

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.29% and final score -0.58%
- Underlying spot: $610.30
- Expiry: 2026-05-22
- Long leg: `META260522P00610000` at strike $610.00 using recent close $17.90
- Short leg: `META260522P00580000` at strike $580.00 using recent close $6.72
- Estimated net debit: $11.18
- Max loss: $11.18
- Max profit: $18.82
- Breakeven at expiry: $598.82
- Reward/risk estimate: 1.68x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0023; memory -0.0007

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.02% and final score 0.43%
- Underlying spot: $272.10
- Expiry: 2026-05-22
- Long leg: `AMZN260522C00270000` at strike $270.00 using recent close $6.70
- Short leg: `AMZN260522C00285000` at strike $285.00 using recent close $1.92
- Estimated net debit: $4.78
- Max loss: $4.78
- Max profit: $10.22
- Breakeven at expiry: $274.78
- Reward/risk estimate: 2.14x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0035; snapshot +0.0004

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
