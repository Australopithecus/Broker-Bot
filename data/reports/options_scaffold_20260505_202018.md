# Options Scaffold Report

Generated at: 2026-05-05T20:20:18.981386+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.32% and final score 0.73%
- Underlying spot: $388.41
- Expiry: 2026-05-22
- Long leg: `GOOGL260522C00387500` at strike $387.50 using recent close $8.90
- Short leg: `GOOGL260522C00407500` at strike $407.50 using recent close $3.28
- Estimated net debit: $5.62
- Max loss: $5.62
- Max profit: $14.38
- Breakeven at expiry: $393.12
- Reward/risk estimate: 2.56x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0033; memory +0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.02% and final score 0.55%
- Underlying spot: $273.56
- Expiry: 2026-05-22
- Long leg: `AMZN260522C00272500` at strike $272.50 using recent close $6.90
- Short leg: `AMZN260522C00285000` at strike $285.00 using recent close $2.66
- Estimated net debit: $4.24
- Max loss: $4.24
- Max profit: $8.26
- Breakeven at expiry: $276.74
- Reward/risk estimate: 1.95x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0046; memory +0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.15% and final score 0.48%
- Underlying spot: $284.18
- Expiry: 2026-05-22
- Long leg: `AAPL260522C00285000` at strike $285.00 using recent close $2.69
- Short leg: `AAPL260522C00300000` at strike $300.00 using recent close $0.45
- Estimated net debit: $2.24
- Max loss: $2.24
- Max profit: $12.76
- Breakeven at expiry: $287.24
- Reward/risk estimate: 5.70x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0024; snapshot +0.0008

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## XOM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.60% and final score 0.42%
- Underlying spot: $154.88
- Expiry: 2026-05-22
- Long leg: `XOM260522C00155000` at strike $155.00 using recent close $3.40
- Short leg: `XOM260522C00162500` at strike $162.50 using recent close $1.26
- Estimated net debit: $2.14
- Max loss: $2.14
- Max profit: $5.36
- Breakeven at expiry: $157.14
- Reward/risk estimate: 2.50x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech -0.0024

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.16% and final score 0.37%
- Underlying spot: $363.83
- Expiry: 2026-05-22
- Long leg: `UNH260522C00365000` at strike $365.00 using recent close $11.87
- Short leg: `UNH260522C00382500` at strike $382.50 using recent close $3.33
- Estimated net debit: $8.54
- Max loss: $8.54
- Max profit: $8.96
- Breakeven at expiry: $373.54
- Reward/risk estimate: 1.05x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0020

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.01% and final score -0.29%
- Underlying spot: $604.92
- Expiry: 2026-05-22
- Long leg: `META260522P00605000` at strike $605.00 using recent close $12.98
- Short leg: `META260522P00575000` at strike $575.00 using recent close $4.25
- Estimated net debit: $8.73
- Max loss: $8.73
- Max profit: $21.27
- Breakeven at expiry: $596.27
- Reward/risk estimate: 2.44x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0024; memory -0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
