# Options Scaffold Report

Generated at: 2026-05-13T22:39:29.592483+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.63% and final score 1.22%
- Underlying spot: $401.05
- Expiry: 2026-05-29
- Long leg: `UNH260529C00400000` at strike $400.00 using recent close $8.78
- Short leg: `UNH260529C00420000` at strike $420.00 using recent close $2.69
- Estimated net debit: $6.09
- Max loss: $6.09
- Max profit: $13.91
- Breakeven at expiry: $406.09
- Reward/risk estimate: 2.28x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0053; memory +0.0005

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bull Call Debit Spread

- Signal: LONG idea with base score 0.78% and final score 1.09%
- Underlying spot: $225.91
- Expiry: 2026-05-27
- Long leg: `NVDA260527C00225000` at strike $225.00 using recent close $7.70
- Short leg: `NVDA260527C00235000` at strike $235.00 using recent close $4.34
- Estimated net debit: $3.36
- Max loss: $3.36
- Max profit: $6.64
- Breakeven at expiry: $228.36
- Reward/risk estimate: 1.98x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0029

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.47% and final score 0.80%
- Underlying spot: $402.63
- Expiry: 2026-05-27
- Long leg: `GOOGL260527C00405000` at strike $405.00 using recent close $3.64
- Short leg: `GOOGL260527C00425000` at strike $425.00 using recent close $0.86
- Estimated net debit: $2.78
- Max loss: $2.78
- Max profit: $17.22
- Breakeven at expiry: $407.78
- Reward/risk estimate: 6.19x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0027

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.36% and final score 0.68%
- Underlying spot: $298.95
- Expiry: 2026-05-27
- Long leg: `AAPL260527C00300000` at strike $300.00 using recent close $4.30
- Short leg: `AAPL260527C00315000` at strike $315.00 using recent close $0.52
- Estimated net debit: $3.78
- Max loss: $3.78
- Max profit: $11.22
- Breakeven at expiry: $303.78
- Reward/risk estimate: 2.97x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0027; memory +0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.26% and final score 0.40%
- Underlying spot: $270.14
- Expiry: 2026-05-27
- Long leg: `AMZN260527C00270000` at strike $270.00 using recent close $3.57
- Short leg: `AMZN260527C00285000` at strike $285.00 using recent close $0.70
- Estimated net debit: $2.87
- Max loss: $2.87
- Max profit: $12.13
- Breakeven at expiry: $272.87
- Reward/risk estimate: 4.23x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0014

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## JPM — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.17% and final score -0.19%
- Underlying spot: $300.31
- Expiry: 2026-05-29
- Long leg: `JPM260529P00300000` at strike $300.00 using recent close $4.25
- Short leg: `JPM260529P00285000` at strike $285.00 using recent close $1.18
- Estimated net debit: $3.07
- Max loss: $3.07
- Max profit: $11.93
- Breakeven at expiry: $296.93
- Reward/risk estimate: 3.89x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0031; memory -0.0005

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
