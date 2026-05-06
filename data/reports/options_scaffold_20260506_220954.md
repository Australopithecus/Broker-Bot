# Options Scaffold Report

Generated at: 2026-05-06T22:09:54.225200+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.25% and final score 0.90%
- Underlying spot: $397.83
- Expiry: 2026-05-20
- Long leg: `GOOGL260520C00400000` at strike $400.00 using recent close $4.34
- Short leg: `GOOGL260520C00420000` at strike $420.00 using recent close $1.35
- Estimated net debit: $2.99
- Max loss: $2.99
- Max profit: $17.01
- Breakeven at expiry: $402.99
- Reward/risk estimate: 5.69x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0052; snapshot +0.0006; memory +0.0007

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.29% and final score 0.84%
- Underlying spot: $274.98
- Expiry: 2026-05-20
- Long leg: `AMZN260520C00275000` at strike $275.00 using recent close $6.00
- Short leg: `AMZN260520C00290000` at strike $290.00 using recent close $1.44
- Estimated net debit: $4.56
- Max loss: $4.56
- Max profit: $10.44
- Breakeven at expiry: $279.56
- Reward/risk estimate: 2.29x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0046; memory +0.0009

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bull Call Debit Spread

- Signal: LONG idea with base score 0.33% and final score 0.45%
- Underlying spot: $207.67
- Expiry: 2026-05-22
- Long leg: `NVDA260522C00207500` at strike $207.50 using recent close $4.08
- Short leg: `NVDA260522C00217500` at strike $217.50 using recent close $1.91
- Estimated net debit: $2.17
- Max loss: $2.17
- Max profit: $7.83
- Breakeven at expiry: $209.67
- Reward/risk estimate: 3.61x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0010; snapshot +0.0013; memory -0.0011

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.08% and final score 0.35%
- Underlying spot: $367.04
- Expiry: 2026-05-22
- Long leg: `UNH260522C00367500` at strike $367.50 using recent close $6.90
- Short leg: `UNH260522C00385000` at strike $385.00 using recent close $1.87
- Estimated net debit: $5.03
- Max loss: $5.03
- Max profit: $12.47
- Breakeven at expiry: $372.53
- Reward/risk estimate: 2.48x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0022

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## JPM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.25% and final score 0.35%
- Underlying spot: $314.87
- Expiry: 2026-05-22
- Long leg: `JPM260522C00315000` at strike $315.00 using recent close $4.22
- Short leg: `JPM260522C00330000` at strike $330.00 using recent close $0.72
- Estimated net debit: $3.50
- Max loss: $3.50
- Max profit: $11.50
- Breakeven at expiry: $318.50
- Reward/risk estimate: 3.29x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: snapshot +0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.02% and final score 0.33%
- Underlying spot: $287.46
- Expiry: 2026-05-20
- Long leg: `AAPL260520C00285000` at strike $285.00 using recent close $4.99
- Short leg: `AAPL260520C00300000` at strike $300.00 using recent close $1.02
- Estimated net debit: $3.97
- Max loss: $3.97
- Max profit: $11.03
- Breakeven at expiry: $288.97
- Reward/risk estimate: 2.78x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0024; snapshot +0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
