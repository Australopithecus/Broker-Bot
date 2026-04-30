# Options Scaffold Report

Generated at: 2026-04-30T17:51:30.060685+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.67% and final score 1.24%
- Underlying spot: $383.38
- Expiry: 2026-05-15
- Long leg: `GOOGL260515C00385000` at strike $385.00 using recent close $2.67
- Short leg: `GOOGL260515C00405000` at strike $405.00 using recent close $0.98
- Estimated net debit: $1.69
- Max loss: $1.69
- Max profit: $18.31
- Breakeven at expiry: $386.69
- Reward/risk estimate: 10.83x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0032; snapshot +0.0024

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.27% and final score 0.70%
- Underlying spot: $369.39
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

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.09% and final score -0.43%
- Underlying spot: $611.01
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

- Signal: LONG idea with base score 0.17% and final score 0.17%
- Underlying spot: $313.17
- Expiry: 2026-05-15
- Long leg: `JPM260515C00312500` at strike $312.50 using recent close $4.75
- Short leg: `JPM260515C00327500` at strike $327.50 using recent close $0.80
- Estimated net debit: $3.95
- Max loss: $3.95
- Max profit: $11.05
- Breakeven at expiry: $316.45
- Reward/risk estimate: 2.80x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: No additional rationale captured.

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
