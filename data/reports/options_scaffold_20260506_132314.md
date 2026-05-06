# Options Scaffold Report

Generated at: 2026-05-06T13:23:14.172244+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.23% and final score 0.74%
- Underlying spot: $388.41
- Expiry: 2026-05-20
- Long leg: `GOOGL260520C00390000` at strike $390.00 using recent close $9.00
- Short leg: `GOOGL260520C00410000` at strike $410.00 using recent close $2.63
- Estimated net debit: $6.37
- Max loss: $6.37
- Max profit: $13.63
- Breakeven at expiry: $396.37
- Reward/risk estimate: 2.14x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0038; snapshot +0.0008; memory +0.0006

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.01% and final score 0.64%
- Underlying spot: $273.56
- Expiry: 2026-05-20
- Long leg: `AMZN260520C00275000` at strike $275.00 using recent close $6.00
- Short leg: `AMZN260520C00290000` at strike $290.00 using recent close $1.44
- Estimated net debit: $4.56
- Max loss: $4.56
- Max profit: $10.44
- Breakeven at expiry: $279.56
- Reward/risk estimate: 2.29x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0053; memory +0.0007

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.31% and final score 0.52%
- Underlying spot: $363.83
- Expiry: 2026-05-22
- Long leg: `UNH260522C00365000` at strike $365.00 using recent close $7.58
- Short leg: `UNH260522C00382500` at strike $382.50 using recent close $2.42
- Estimated net debit: $5.16
- Max loss: $5.16
- Max profit: $12.34
- Breakeven at expiry: $370.16
- Reward/risk estimate: 2.39x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0023; snapshot -0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.19% and final score 0.52%
- Underlying spot: $284.18
- Expiry: 2026-05-20
- Long leg: `AAPL260520C00285000` at strike $285.00 using recent close $4.99
- Short leg: `AAPL260520C00300000` at strike $300.00 using recent close $1.02
- Estimated net debit: $3.97
- Max loss: $3.97
- Max profit: $11.03
- Breakeven at expiry: $288.97
- Reward/risk estimate: 2.78x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0028

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.02% and final score -0.33%
- Underlying spot: $604.92
- Expiry: 2026-05-20
- Long leg: `META260520P00605000` at strike $605.00 using recent close $15.42
- Short leg: `META260520P00575000` at strike $575.00 using recent close $4.59
- Estimated net debit: $10.83
- Max loss: $10.83
- Max profit: $19.17
- Breakeven at expiry: $594.17
- Reward/risk estimate: 1.77x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0028; memory -0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## JPM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.19% and final score 0.19%
- Underlying spot: $309.36
- Expiry: 2026-05-22
- Long leg: `JPM260522C00310000` at strike $310.00 using recent close $6.50
- Short leg: `JPM260522C00325000` at strike $325.00 using recent close $1.33
- Estimated net debit: $5.17
- Max loss: $5.17
- Max profit: $9.83
- Breakeven at expiry: $315.17
- Reward/risk estimate: 1.90x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech -0.0006; snapshot +0.0005

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
