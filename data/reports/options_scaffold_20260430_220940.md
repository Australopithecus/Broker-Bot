# Options Scaffold Report

Generated at: 2026-04-30T22:09:40.817145+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.65% and final score 1.24%
- Underlying spot: $384.99
- Expiry: 2026-05-15
- Long leg: `GOOGL260515C00385000` at strike $385.00 using recent close $2.67
- Short leg: `GOOGL260515C00405000` at strike $405.00 using recent close $0.98
- Estimated net debit: $1.69
- Max loss: $1.69
- Max profit: $18.31
- Breakeven at expiry: $386.69
- Reward/risk estimate: 10.83x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0032; snapshot +0.0026

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.26% and final score 0.74%
- Underlying spot: $370.58
- Expiry: 2026-05-15
- Long leg: `UNH260515C00370000` at strike $370.00 using recent close $9.25
- Short leg: `UNH260515C00390000` at strike $390.00 using recent close $2.33
- Estimated net debit: $6.92
- Max loss: $6.92
- Max profit: $13.08
- Breakeven at expiry: $376.92
- Reward/risk estimate: 1.89x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0035; memory +0.0010

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.02% and final score 0.35%
- Underlying spot: $265.04
- Expiry: 2026-05-15
- Long leg: `AMZN260515C00265000` at strike $265.00 using recent close $11.00
- Short leg: `AMZN260515C00277500` at strike $277.50 using recent close $5.86
- Estimated net debit: $5.14
- Max loss: $5.14
- Max profit: $7.36
- Breakeven at expiry: $270.14
- Reward/risk estimate: 1.43x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0027

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.17% and final score -0.34%
- Underlying spot: $612.16
- Expiry: 2026-05-15
- Long leg: `META260515P00610000` at strike $610.00 using recent close $8.20
- Short leg: `META260515P00580000` at strike $580.00 using recent close $3.60
- Estimated net debit: $4.60
- Max loss: $4.60
- Max profit: $25.40
- Breakeven at expiry: $605.40
- Reward/risk estimate: 5.52x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0029; snapshot -0.0022

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## JPM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.21% and final score 0.27%
- Underlying spot: $313.30
- Expiry: 2026-05-15
- Long leg: `JPM260515C00312500` at strike $312.50 using recent close $4.75
- Short leg: `JPM260515C00327500` at strike $327.50 using recent close $0.80
- Estimated net debit: $3.95
- Max loss: $3.95
- Max profit: $11.05
- Breakeven at expiry: $316.45
- Reward/risk estimate: 2.80x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: snapshot +0.0008

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## PG — Bull Call Debit Spread

- Signal: LONG idea with base score 0.17% and final score 0.16%
- Underlying spot: $147.18
- Expiry: 2026-05-15
- Long leg: `PG260515C00147000` at strike $147.00 using recent close $2.42
- Short leg: `PG260515C00155000` at strike $155.00 using recent close $0.33
- Estimated net debit: $2.09
- Max loss: $2.09
- Max profit: $5.91
- Breakeven at expiry: $149.09
- Reward/risk estimate: 2.83x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech -0.0013; snapshot +0.0005; memory +0.0007

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
