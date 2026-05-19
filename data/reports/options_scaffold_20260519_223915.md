# Options Scaffold Report

Generated at: 2026-05-19T22:39:15.016843+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## XOM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.42% and final score 0.60%
- Underlying spot: $162.61
- Expiry: 2026-06-05
- Long leg: `XOM260605C00162500` at strike $162.50 using recent close $3.85
- Short leg: `XOM260605C00170000` at strike $170.00 using recent close $1.54
- Estimated net debit: $2.31
- Max loss: $2.31
- Max profit: $5.19
- Breakeven at expiry: $164.81
- Reward/risk estimate: 2.25x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0018

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.18% and final score 0.55%
- Underlying spot: $299.14
- Expiry: 2026-06-05
- Long leg: `AAPL260605C00300000` at strike $300.00 using recent close $5.25
- Short leg: `AAPL260605C00315000` at strike $315.00 using recent close $1.10
- Estimated net debit: $4.15
- Max loss: $4.15
- Max profit: $10.85
- Breakeven at expiry: $304.15
- Reward/risk estimate: 2.61x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0035

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.20% and final score 0.53%
- Underlying spot: $389.45
- Expiry: 2026-06-05
- Long leg: `UNH260605C00390000` at strike $390.00 using recent close $9.51
- Short leg: `UNH260605C00410000` at strike $410.00 using recent close $3.19
- Estimated net debit: $6.32
- Max loss: $6.32
- Max profit: $13.68
- Breakeven at expiry: $396.32
- Reward/risk estimate: 2.16x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0031

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## JPM — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.03% and final score -0.30%
- Underlying spot: $295.84
- Expiry: 2026-06-05
- Long leg: `JPM260605P00295000` at strike $295.00 using recent close $4.35
- Short leg: `JPM260605P00280000` at strike $280.00 using recent close $1.18
- Estimated net debit: $3.17
- Max loss: $3.17
- Max profit: $11.83
- Breakeven at expiry: $291.83
- Reward/risk estimate: 3.73x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0026

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score -0.07% and final score 0.29%
- Underlying spot: $387.75
- Expiry: 2026-06-12
- Long leg: `GOOGL260612C00390000` at strike $390.00 using recent close $18.67
- Short leg: `GOOGL260612C00410000` at strike $410.00 using recent close $9.00
- Estimated net debit: $9.67
- Max loss: $9.67
- Max profit: $10.33
- Breakeven at expiry: $399.67
- Reward/risk estimate: 1.07x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0037

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.13% and final score -0.23%
- Underlying spot: $602.70
- Expiry: 2026-06-05
- Long leg: `META260605P00602500` at strike $602.50 using recent close $13.09
- Short leg: `META260605P00570000` at strike $570.00 using recent close $3.70
- Estimated net debit: $9.39
- Max loss: $9.39
- Max profit: $23.11
- Breakeven at expiry: $593.11
- Reward/risk estimate: 2.46x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0035

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
