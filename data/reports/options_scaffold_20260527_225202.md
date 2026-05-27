# Options Scaffold Report

Generated at: 2026-05-27T22:52:02.642481+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.19% and final score 0.69%
- Underlying spot: $310.93
- Expiry: 2026-06-10
- Long leg: `AAPL260610C00310000` at strike $310.00 using recent close $5.10
- Short leg: `AAPL260610C00325000` at strike $325.00 using recent close $0.97
- Estimated net debit: $4.13
- Max loss: $4.13
- Max profit: $10.87
- Breakeven at expiry: $314.13
- Reward/risk estimate: 2.63x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0047

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.17% and final score 0.49%
- Underlying spot: $271.85
- Expiry: 2026-06-10
- Long leg: `AMZN260610C00270000` at strike $270.00 using recent close $4.20
- Short leg: `AMZN260610C00285000` at strike $285.00 using recent close $1.00
- Estimated net debit: $3.20
- Max loss: $3.20
- Max profit: $11.80
- Breakeven at expiry: $273.20
- Reward/risk estimate: 3.69x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0028; snapshot +0.0005

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## PG — Bull Call Debit Spread

- Signal: LONG idea with base score 0.27% and final score 0.45%
- Underlying spot: $147.54
- Expiry: 2026-06-12
- Long leg: `PG260612C00148000` at strike $148.00 using recent close $1.15
- Short leg: `PG260612C00155000` at strike $155.00 using recent close $0.17
- Estimated net debit: $0.98
- Max loss: $0.98
- Max profit: $6.02
- Breakeven at expiry: $148.98
- Reward/risk estimate: 6.14x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0010; snapshot +0.0006

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## XOM — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.08% and final score -0.31%
- Underlying spot: $148.04
- Expiry: 2026-06-12
- Long leg: `XOM260612P00148000` at strike $148.00 using recent close $3.12
- Short leg: `XOM260612P00141000` at strike $141.00 using recent close $0.90
- Estimated net debit: $2.22
- Max loss: $2.22
- Max profit: $4.78
- Breakeven at expiry: $145.78
- Reward/risk estimate: 2.15x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0019

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score -0.01% and final score 0.21%
- Underlying spot: $384.15
- Expiry: 2026-06-12
- Long leg: `UNH260612C00385000` at strike $385.00 using recent close $6.16
- Short leg: `UNH260612C00405000` at strike $405.00 using recent close $1.74
- Estimated net debit: $4.42
- Max loss: $4.42
- Max profit: $15.58
- Breakeven at expiry: $389.42
- Reward/risk estimate: 3.52x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0016

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## MSFT — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.01% and final score -0.19%
- Underlying spot: $412.71
- Expiry: 2026-06-10
- Long leg: `MSFT260610P00415000` at strike $415.00 using recent close $8.78
- Short leg: `MSFT260610P00395000` at strike $395.00 using recent close $2.30
- Estimated net debit: $6.48
- Max loss: $6.48
- Max profit: $13.52
- Breakeven at expiry: $408.52
- Reward/risk estimate: 2.09x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0017

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
