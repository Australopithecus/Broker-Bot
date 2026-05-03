# Options Scaffold Report

Generated at: 2026-05-03T02:22:31.876282+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.52% and final score 0.97%
- Underlying spot: $368.78
- Expiry: 2026-05-22
- Long leg: `UNH260522C00370000` at strike $370.00 using recent close $9.50
- Short leg: `UNH260522C00390000` at strike $390.00 using recent close $2.73
- Estimated net debit: $6.77
- Max loss: $6.77
- Max profit: $13.23
- Breakeven at expiry: $376.77
- Reward/risk estimate: 1.95x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0037; memory +0.0005

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.47% and final score 0.86%
- Underlying spot: $385.79
- Expiry: 2026-05-22
- Long leg: `GOOGL260522C00385000` at strike $385.00 using recent close $12.12
- Short leg: `GOOGL260522C00405000` at strike $405.00 using recent close $4.55
- Estimated net debit: $7.57
- Max loss: $7.57
- Max profit: $12.43
- Breakeven at expiry: $392.57
- Reward/risk estimate: 1.64x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0033; memory +0.0006

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.44% and final score -0.80%
- Underlying spot: $608.61
- Expiry: 2026-05-22
- Long leg: `META260522P00610000` at strike $610.00 using recent close $17.90
- Short leg: `META260522P00580000` at strike $580.00 using recent close $6.72
- Estimated net debit: $11.18
- Max loss: $11.18
- Max profit: $18.82
- Breakeven at expiry: $598.82
- Reward/risk estimate: 1.68x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0030; memory -0.0005

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## XOM — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.09% and final score -0.38%
- Underlying spot: $152.76
- Expiry: 2026-05-22
- Long leg: `XOM260522P00155000` at strike $155.00 using recent close $5.70
- Short leg: `XOM260522P00145000` at strike $145.00 using recent close $1.74
- Estimated net debit: $3.96
- Max loss: $3.96
- Max profit: $6.04
- Breakeven at expiry: $151.04
- Reward/risk estimate: 1.53x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0023; memory -0.0003

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.20% and final score 0.35%
- Underlying spot: $280.11
- Expiry: 2026-05-22
- Long leg: `AAPL260522C00280000` at strike $280.00 using recent close $6.50
- Short leg: `AAPL260522C00295000` at strike $295.00 using recent close $1.52
- Estimated net debit: $4.98
- Max loss: $4.98
- Max profit: $10.02
- Breakeven at expiry: $284.98
- Reward/risk estimate: 2.01x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0010; snapshot +0.0011; memory -0.0006

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.31% and final score -0.31%
- Underlying spot: $198.39
- Expiry: 2026-05-22
- Long leg: `NVDA260522P00200000` at strike $200.00 using recent close $9.25
- Short leg: `NVDA260522P00190000` at strike $190.00 using recent close $5.15
- Estimated net debit: $4.10
- Max loss: $4.10
- Max profit: $5.90
- Breakeven at expiry: $195.90
- Reward/risk estimate: 1.44x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: No additional rationale captured.

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
