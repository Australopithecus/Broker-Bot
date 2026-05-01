# Options Scaffold Report

Generated at: 2026-05-01T22:06:43.580724+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.52% and final score 0.98%
- Underlying spot: $368.78
- Expiry: 2026-05-15
- Long leg: `UNH260515C00370000` at strike $370.00 using recent close $8.60
- Short leg: `UNH260515C00390000` at strike $390.00 using recent close $1.78
- Estimated net debit: $6.82
- Max loss: $6.82
- Max profit: $13.18
- Breakeven at expiry: $376.82
- Reward/risk estimate: 1.93x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0037; memory +0.0006

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.47% and final score 0.86%
- Underlying spot: $385.79
- Expiry: 2026-05-15
- Long leg: `GOOGL260515C00385000` at strike $385.00 using recent close $10.06
- Short leg: `GOOGL260515C00405000` at strike $405.00 using recent close $3.60
- Estimated net debit: $6.46
- Max loss: $6.46
- Max profit: $13.54
- Breakeven at expiry: $391.46
- Reward/risk estimate: 2.10x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0034; memory +0.0006

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.44% and final score -0.81%
- Underlying spot: $608.61
- Expiry: 2026-05-15
- Long leg: `META260515P00610000` at strike $610.00 using recent close $15.15
- Short leg: `META260515P00580000` at strike $580.00 using recent close $5.10
- Estimated net debit: $10.05
- Max loss: $10.05
- Max profit: $19.95
- Breakeven at expiry: $599.95
- Reward/risk estimate: 1.99x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0031; memory -0.0005

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.20% and final score 0.38%
- Underlying spot: $280.11
- Expiry: 2026-05-15
- Long leg: `AAPL260515C00280000` at strike $280.00 using recent close $3.85
- Short leg: `AAPL260515C00295000` at strike $295.00 using recent close $1.06
- Estimated net debit: $2.79
- Max loss: $2.79
- Max profit: $12.21
- Breakeven at expiry: $282.79
- Reward/risk estimate: 4.38x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0010; snapshot +0.0012; memory -0.0004

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## XOM — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.09% and final score -0.37%
- Underlying spot: $152.76
- Expiry: 2026-05-15
- Long leg: `XOM260515P00152500` at strike $152.50 using recent close $4.00
- Short leg: `XOM260515P00145000` at strike $145.00 using recent close $1.17
- Estimated net debit: $2.83
- Max loss: $2.83
- Max profit: $4.67
- Breakeven at expiry: $149.67
- Reward/risk estimate: 1.65x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0024

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.31% and final score -0.31%
- Underlying spot: $198.39
- Expiry: 2026-05-15
- Long leg: `NVDA260515P00197500` at strike $197.50 using recent close $4.92
- Short leg: `NVDA260515P00187500` at strike $187.50 using recent close $2.01
- Estimated net debit: $2.91
- Max loss: $2.91
- Max profit: $7.09
- Breakeven at expiry: $194.59
- Reward/risk estimate: 2.44x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: memory -0.0004

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
