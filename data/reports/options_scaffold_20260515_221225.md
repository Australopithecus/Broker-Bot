# Options Scaffold Report

Generated at: 2026-05-15T22:12:25.425594+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.58% and final score 1.10%
- Underlying spot: $393.52
- Expiry: 2026-05-29
- Long leg: `UNH260529C00392500` at strike $392.50 using recent close $12.46
- Short leg: `UNH260529C00410000` at strike $410.00 using recent close $4.77
- Estimated net debit: $7.69
- Max loss: $7.69
- Max profit: $9.81
- Breakeven at expiry: $400.19
- Reward/risk estimate: 1.28x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0047; memory +0.0005

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## XOM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.82% and final score 1.04%
- Underlying spot: $157.93
- Expiry: 2026-05-29
- Long leg: `XOM260529C00157500` at strike $157.50 using recent close $1.60
- Short leg: `XOM260529C00165000` at strike $165.00 using recent close $0.43
- Estimated net debit: $1.17
- Max loss: $1.17
- Max profit: $6.33
- Breakeven at expiry: $158.67
- Reward/risk estimate: 5.41x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0022

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.18% and final score 0.43%
- Underlying spot: $396.75
- Expiry: 2026-05-29
- Long leg: `GOOGL260529C00397500` at strike $397.50 using recent close $12.70
- Short leg: `GOOGL260529C00417500` at strike $417.50 using recent close $4.05
- Estimated net debit: $8.65
- Max loss: $8.65
- Max profit: $11.35
- Breakeven at expiry: $406.15
- Reward/risk estimate: 1.31x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0024

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.11% and final score 0.39%
- Underlying spot: $300.19
- Expiry: 2026-05-29
- Long leg: `AAPL260529C00300000` at strike $300.00 using recent close $5.02
- Short leg: `AAPL260529C00315000` at strike $315.00 using recent close $1.05
- Estimated net debit: $3.97
- Max loss: $3.97
- Max profit: $11.03
- Breakeven at expiry: $303.97
- Reward/risk estimate: 2.78x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0025; memory +0.0003

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## MSFT — Bull Call Debit Spread

- Signal: LONG idea with base score 0.35% and final score 0.25%
- Underlying spot: $422.00
- Expiry: 2026-05-29
- Long leg: `MSFT260529C00422500` at strike $422.50 using recent close $4.48
- Short leg: `MSFT260529C00445000` at strike $445.00 using recent close $1.16
- Estimated net debit: $3.32
- Max loss: $3.32
- Max profit: $19.18
- Breakeven at expiry: $425.82
- Reward/risk estimate: 5.78x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech -0.0008; memory -0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
