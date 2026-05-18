# Options Scaffold Report

Generated at: 2026-05-18T22:14:30.165989+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.25% and final score 0.64%
- Underlying spot: $391.04
- Expiry: 2026-06-05
- Long leg: `UNH260605C00390000` at strike $390.00 using recent close $11.40
- Short leg: `UNH260605C00410000` at strike $410.00 using recent close $4.72
- Estimated net debit: $6.68
- Max loss: $6.68
- Max profit: $13.32
- Breakeven at expiry: $396.68
- Reward/risk estimate: 1.99x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0037

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## XOM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.32% and final score 0.54%
- Underlying spot: $160.48
- Expiry: 2026-06-05
- Long leg: `XOM260605C00160000` at strike $160.00 using recent close $3.99
- Short leg: `XOM260605C00170000` at strike $170.00 using recent close $1.11
- Estimated net debit: $2.88
- Max loss: $2.88
- Max profit: $7.12
- Breakeven at expiry: $162.88
- Reward/risk estimate: 2.47x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0021

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.04% and final score 0.38%
- Underlying spot: $396.81
- Expiry: 2026-06-05
- Long leg: `GOOGL260605C00395000` at strike $395.00 using recent close $13.12
- Short leg: `GOOGL260605C00415000` at strike $415.00 using recent close $5.40
- Estimated net debit: $7.72
- Max loss: $7.72
- Max profit: $12.28
- Breakeven at expiry: $402.72
- Reward/risk estimate: 1.59x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0033

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.04% and final score -0.31%
- Underlying spot: $611.25
- Expiry: 2026-06-05
- Long leg: `META260605P00610000` at strike $610.00 using recent close $15.61
- Short leg: `META260605P00580000` at strike $580.00 using recent close $5.80
- Estimated net debit: $9.81
- Max loss: $9.81
- Max profit: $20.19
- Breakeven at expiry: $600.19
- Reward/risk estimate: 2.06x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0034

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## JPM — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.05% and final score -0.27%
- Underlying spot: $300.79
- Expiry: 2026-06-05
- Long leg: `JPM260605P00300000` at strike $300.00 using recent close $7.80
- Short leg: `JPM260605P00285000` at strike $285.00 using recent close $2.46
- Estimated net debit: $5.34
- Max loss: $5.34
- Max profit: $9.66
- Breakeven at expiry: $294.66
- Reward/risk estimate: 1.81x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0022

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## PG — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.03% and final score -0.19%
- Underlying spot: $142.38
- Expiry: 2026-06-05
- Long leg: `PG260605P00142000` at strike $142.00 using recent close $2.79
- Short leg: `PG260605P00135000` at strike $135.00 using recent close $0.56
- Estimated net debit: $2.23
- Max loss: $2.23
- Max profit: $4.77
- Breakeven at expiry: $139.77
- Reward/risk estimate: 2.14x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0018

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
