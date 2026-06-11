# Options Scaffold Report

Generated at: 2026-06-11T22:59:20.471361+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## JPM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.05% and final score 0.59%
- Underlying spot: $313.54
- Expiry: 2026-06-26
- Long leg: `JPM260626C00312500` at strike $312.50 using recent close $7.17
- Short leg: `JPM260626C00327500` at strike $327.50 using recent close $1.46
- Estimated net debit: $5.71
- Max loss: $5.71
- Max profit: $9.29
- Breakeven at expiry: $318.21
- Reward/risk estimate: 1.63x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0046; snapshot +0.0009

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.20% and final score 0.41%
- Underlying spot: $295.48
- Expiry: 2026-06-26
- Long leg: `AAPL260626C00295000` at strike $295.00 using recent close $5.30
- Short leg: `AAPL260626C00310000` at strike $310.00 using recent close $1.26
- Estimated net debit: $4.04
- Max loss: $4.04
- Max profit: $10.96
- Breakeven at expiry: $299.04
- Reward/risk estimate: 2.71x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0016

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.04% and final score 0.33%
- Underlying spot: $405.27
- Expiry: 2026-06-26
- Long leg: `UNH260626C00405000` at strike $405.00 using recent close $9.33
- Short leg: `UNH260626C00425000` at strike $425.00 using recent close $3.00
- Estimated net debit: $6.33
- Max loss: $6.33
- Max profit: $13.67
- Breakeven at expiry: $411.33
- Reward/risk estimate: 2.16x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0028

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## PG — Bull Call Debit Spread

- Signal: LONG idea with base score -0.12% and final score 0.33%
- Underlying spot: $148.30
- Expiry: 2026-06-26
- Long leg: `PG260626C00148000` at strike $148.00 using recent close $4.05
- Short leg: `PG260626C00155000` at strike $155.00 using recent close $0.88
- Estimated net debit: $3.17
- Max loss: $3.17
- Max profit: $3.83
- Breakeven at expiry: $151.17
- Reward/risk estimate: 1.21x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0040

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## XOM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.28% and final score 0.30%
- Underlying spot: $146.56
- Expiry: 2026-07-24
- Long leg: `XOM260724C00145000` at strike $145.00 using recent close $9.09
- Short leg: `XOM260724C00150000` at strike $150.00 using recent close $7.90
- Estimated net debit: $1.19
- Max loss: $1.19
- Max profit: $3.81
- Breakeven at expiry: $146.19
- Reward/risk estimate: 3.20x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0008; snapshot -0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.44% and final score 0.27%
- Underlying spot: $241.42
- Expiry: 2026-06-26
- Long leg: `AMZN260626C00242500` at strike $242.50 using recent close $5.10
- Short leg: `AMZN260626C00255000` at strike $255.00 using recent close $1.61
- Estimated net debit: $3.49
- Max loss: $3.49
- Max profit: $9.01
- Breakeven at expiry: $245.99
- Reward/risk estimate: 2.58x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech -0.0022; snapshot +0.0006

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
