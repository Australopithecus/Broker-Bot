# Options Scaffold Report

Generated at: 2026-06-09T22:50:33.426591+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.20% and final score 0.70%
- Underlying spot: $412.68
- Expiry: 2026-06-26
- Long leg: `UNH260626C00412500` at strike $412.50 using recent close $7.71
- Short leg: `UNH260626C00435000` at strike $435.00 using recent close $2.62
- Estimated net debit: $5.09
- Max loss: $5.09
- Max profit: $17.41
- Breakeven at expiry: $417.59
- Reward/risk estimate: 3.42x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0043; snapshot +0.0006

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.30% and final score -0.56%
- Underlying spot: $208.20
- Expiry: 2026-06-26
- Long leg: `NVDA260626P00207500` at strike $207.50 using recent close $6.64
- Short leg: `NVDA260626P00197500` at strike $197.50 using recent close $3.05
- Estimated net debit: $3.59
- Max loss: $3.59
- Max profit: $6.41
- Breakeven at expiry: $203.91
- Reward/risk estimate: 1.79x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0025

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.51% and final score -0.54%
- Underlying spot: $290.36
- Expiry: 2026-06-26
- Long leg: `AAPL260626P00290000` at strike $290.00 using recent close $2.67
- Short leg: `AAPL260626P00275000` at strike $275.00 using recent close $0.76
- Estimated net debit: $1.91
- Max loss: $1.91
- Max profit: $13.09
- Breakeven at expiry: $288.09
- Reward/risk estimate: 6.85x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech +0.0005; snapshot -0.0009

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## MSFT — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.25% and final score -0.46%
- Underlying spot: $403.11
- Expiry: 2026-06-26
- Long leg: `MSFT260626P00402500` at strike $402.50 using recent close $6.80
- Short leg: `MSFT260626P00380000` at strike $380.00 using recent close $1.87
- Estimated net debit: $4.93
- Max loss: $4.93
- Max profit: $17.57
- Breakeven at expiry: $397.57
- Reward/risk estimate: 3.56x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0014; snapshot -0.0005

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## JPM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.03% and final score 0.44%
- Underlying spot: $312.58
- Expiry: 2026-06-26
- Long leg: `JPM260626C00312500` at strike $312.50 using recent close $7.37
- Short leg: `JPM260626C00327500` at strike $327.50 using recent close $2.03
- Estimated net debit: $5.34
- Max loss: $5.34
- Max profit: $9.66
- Breakeven at expiry: $317.84
- Reward/risk estimate: 1.81x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0038; snapshot +0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.14% and final score -0.41%
- Underlying spot: $244.15
- Expiry: 2026-06-26
- Long leg: `AMZN260626P00245000` at strike $245.00 using recent close $6.72
- Short leg: `AMZN260626P00232500` at strike $232.50 using recent close $2.53
- Estimated net debit: $4.19
- Max loss: $4.19
- Max profit: $8.31
- Breakeven at expiry: $240.81
- Reward/risk estimate: 1.98x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0027

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
