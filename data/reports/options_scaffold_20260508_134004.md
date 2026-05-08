# Options Scaffold Report

Generated at: 2026-05-08T13:40:04.544422+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.62% and final score 1.18%
- Underlying spot: $397.20
- Expiry: 2026-05-22
- Long leg: `GOOGL260522C00397500` at strike $397.50 using recent close $10.80
- Short leg: `GOOGL260522C00417500` at strike $417.50 using recent close $3.57
- Estimated net debit: $7.23
- Max loss: $7.23
- Max profit: $12.77
- Breakeven at expiry: $404.73
- Reward/risk estimate: 1.77x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0046; memory +0.0008

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bull Call Debit Spread

- Signal: LONG idea with base score 0.57% and final score 0.85%
- Underlying spot: $215.76
- Expiry: 2026-05-22
- Long leg: `NVDA260522C00215000` at strike $215.00 using recent close $7.62
- Short leg: `NVDA260522C00225000` at strike $225.00 using recent close $4.14
- Estimated net debit: $3.48
- Max loss: $3.48
- Max profit: $6.52
- Breakeven at expiry: $218.48
- Reward/risk estimate: 1.87x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0031; snapshot +0.0007; memory -0.0011

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.27% and final score 0.74%
- Underlying spot: $374.42
- Expiry: 2026-05-22
- Long leg: `UNH260522C00375000` at strike $375.00 using recent close $5.00
- Short leg: `UNH260522C00392500` at strike $392.50 using recent close $1.18
- Estimated net debit: $3.82
- Max loss: $3.82
- Max profit: $13.68
- Breakeven at expiry: $378.82
- Reward/risk estimate: 3.58x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0038; snapshot +0.0006

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## XOM — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.04% and final score -0.49%
- Underlying spot: $144.81
- Expiry: 2026-05-22
- Long leg: `XOM260522P00145000` at strike $145.00 using recent close $3.40
- Short leg: `XOM260522P00138000` at strike $138.00 using recent close $0.95
- Estimated net debit: $2.45
- Max loss: $2.45
- Max profit: $4.55
- Breakeven at expiry: $142.55
- Reward/risk estimate: 1.86x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0046

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score -0.02% and final score 0.29%
- Underlying spot: $270.24
- Expiry: 2026-05-22
- Long leg: `AMZN260522C00270000` at strike $270.00 using recent close $6.87
- Short leg: `AMZN260522C00282500` at strike $282.50 using recent close $2.15
- Estimated net debit: $4.72
- Max loss: $4.72
- Max profit: $7.78
- Breakeven at expiry: $274.72
- Reward/risk estimate: 1.65x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0023; memory +0.0005

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score -0.02% and final score 0.27%
- Underlying spot: $292.77
- Expiry: 2026-05-22
- Long leg: `AAPL260522C00292500` at strike $292.50 using recent close $3.45
- Short leg: `AAPL260522C00307500` at strike $307.50 using recent close $0.58
- Estimated net debit: $2.87
- Max loss: $2.87
- Max profit: $12.13
- Breakeven at expiry: $295.37
- Reward/risk estimate: 4.23x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0021; snapshot +0.0007

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
