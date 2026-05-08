# Options Scaffold Report

Generated at: 2026-05-08T16:43:54.169359+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## NVDA — Bull Call Debit Spread

- Signal: LONG idea with base score 0.53% and final score 0.85%
- Underlying spot: $215.82
- Expiry: 2026-05-22
- Long leg: `NVDA260522C00215000` at strike $215.00 using recent close $7.62
- Short leg: `NVDA260522C00225000` at strike $225.00 using recent close $4.14
- Estimated net debit: $3.48
- Max loss: $3.48
- Max profit: $6.52
- Breakeven at expiry: $218.48
- Reward/risk estimate: 1.87x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0031; screener +0.0007; memory -0.0010

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.27% and final score 0.80%
- Underlying spot: $398.25
- Expiry: 2026-05-22
- Long leg: `GOOGL260522C00397500` at strike $397.50 using recent close $10.80
- Short leg: `GOOGL260522C00417500` at strike $417.50 using recent close $3.57
- Estimated net debit: $7.23
- Max loss: $7.23
- Max profit: $12.77
- Breakeven at expiry: $404.73
- Reward/risk estimate: 1.77x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0045; memory +0.0008

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.26% and final score 0.65%
- Underlying spot: $372.44
- Expiry: 2026-05-22
- Long leg: `UNH260522C00372500` at strike $372.50 using recent close $6.36
- Short leg: `UNH260522C00390000` at strike $390.00 using recent close $1.38
- Estimated net debit: $4.98
- Max loss: $4.98
- Max profit: $12.52
- Breakeven at expiry: $377.48
- Reward/risk estimate: 2.51x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0035

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.06% and final score 0.39%
- Underlying spot: $272.45
- Expiry: 2026-05-22
- Long leg: `AMZN260522C00272500` at strike $272.50 using recent close $5.70
- Short leg: `AMZN260522C00285000` at strike $285.00 using recent close $1.67
- Estimated net debit: $4.03
- Max loss: $4.03
- Max profit: $8.47
- Breakeven at expiry: $276.53
- Reward/risk estimate: 2.10x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0028; memory +0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.06% and final score 0.31%
- Underlying spot: $292.10
- Expiry: 2026-05-22
- Long leg: `AAPL260522C00292500` at strike $292.50 using recent close $3.45
- Short leg: `AAPL260522C00307500` at strike $307.50 using recent close $0.58
- Estimated net debit: $2.87
- Max loss: $2.87
- Max profit: $12.13
- Breakeven at expiry: $295.37
- Reward/risk estimate: 4.23x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0021

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## XOM — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.19% and final score -0.29%
- Underlying spot: $144.97
- Expiry: 2026-05-22
- Long leg: `XOM260522P00145000` at strike $145.00 using recent close $3.40
- Short leg: `XOM260522P00138000` at strike $138.00 using recent close $0.95
- Estimated net debit: $2.45
- Max loss: $2.45
- Max profit: $4.55
- Breakeven at expiry: $142.55
- Reward/risk estimate: 1.86x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0045

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
