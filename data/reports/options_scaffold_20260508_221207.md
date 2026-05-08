# Options Scaffold Report

Generated at: 2026-05-08T22:12:07.047101+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.46% and final score 0.90%
- Underlying spot: $379.79
- Expiry: 2026-05-22
- Long leg: `UNH260522C00380000` at strike $380.00 using recent close $3.24
- Short leg: `UNH260522C00400000` at strike $400.00 using recent close $0.89
- Estimated net debit: $2.35
- Max loss: $2.35
- Max profit: $17.65
- Breakeven at expiry: $382.35
- Reward/risk estimate: 7.51x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0038; snapshot +0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.19% and final score 0.69%
- Underlying spot: $400.67
- Expiry: 2026-05-22
- Long leg: `GOOGL260522C00400000` at strike $400.00 using recent close $9.58
- Short leg: `GOOGL260522C00420000` at strike $420.00 using recent close $3.20
- Estimated net debit: $6.38
- Max loss: $6.38
- Max profit: $13.62
- Breakeven at expiry: $406.38
- Reward/risk estimate: 2.13x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0045; memory +0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bull Call Debit Spread

- Signal: LONG idea with base score 0.34% and final score 0.66%
- Underlying spot: $215.21
- Expiry: 2026-05-22
- Long leg: `NVDA260522C00215000` at strike $215.00 using recent close $7.62
- Short leg: `NVDA260522C00225000` at strike $225.00 using recent close $4.14
- Estimated net debit: $3.48
- Max loss: $3.48
- Max profit: $6.52
- Breakeven at expiry: $218.48
- Reward/risk estimate: 1.87x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0023; screener +0.0011; memory -0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.15% and final score 0.53%
- Underlying spot: $272.54
- Expiry: 2026-05-22
- Long leg: `AMZN260522C00272500` at strike $272.50 using recent close $5.70
- Short leg: `AMZN260522C00285000` at strike $285.00 using recent close $1.67
- Estimated net debit: $4.03
- Max loss: $4.03
- Max profit: $8.47
- Breakeven at expiry: $276.53
- Reward/risk estimate: 2.10x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0034

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.10% and final score 0.35%
- Underlying spot: $293.15
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

- Signal: SHORT idea with base score 0.23% and final score -0.23%
- Underlying spot: $144.38
- Expiry: 2026-05-22
- Long leg: `XOM260522P00144000` at strike $144.00 using recent close $2.73
- Short leg: `XOM260522P00137000` at strike $137.00 using recent close $0.82
- Estimated net debit: $1.91
- Max loss: $1.91
- Max profit: $5.09
- Breakeven at expiry: $142.09
- Reward/risk estimate: 2.66x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0045

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
