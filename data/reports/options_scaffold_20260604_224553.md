# Options Scaffold Report

Generated at: 2026-06-04T22:45:53.020138+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.30% and final score 0.83%
- Underlying spot: $396.52
- Expiry: 2026-06-18
- Long leg: `UNH260618C00397500` at strike $397.50 using recent close $3.20
- Short leg: `UNH260618C00417500` at strike $417.50 using recent close $0.97
- Estimated net debit: $2.23
- Max loss: $2.23
- Max profit: $17.77
- Breakeven at expiry: $399.73
- Reward/risk estimate: 7.97x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0034; snapshot +0.0017

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## JPM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.29% and final score 0.46%
- Underlying spot: $310.89
- Expiry: 2026-06-18
- Long leg: `JPM260618C00310000` at strike $310.00 using recent close $2.90
- Short leg: `JPM260618C00325000` at strike $325.00 using recent close $0.50
- Estimated net debit: $2.40
- Max loss: $2.40
- Max profit: $12.60
- Breakeven at expiry: $312.40
- Reward/risk estimate: 5.25x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0007; snapshot +0.0012

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score -0.09% and final score 0.33%
- Underlying spot: $311.21
- Expiry: 2026-06-18
- Long leg: `AAPL260618C00310000` at strike $310.00 using recent close $6.90
- Short leg: `AAPL260618C00325000` at strike $325.00 using recent close $2.07
- Estimated net debit: $4.83
- Max loss: $4.83
- Max profit: $10.17
- Breakeven at expiry: $314.83
- Reward/risk estimate: 2.11x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0039

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.00% and final score -0.29%
- Underlying spot: $253.85
- Expiry: 2026-06-18
- Long leg: `AMZN260618P00255000` at strike $255.00 using recent close $9.09
- Short leg: `AMZN260618P00242500` at strike $242.50 using recent close $3.45
- Estimated net debit: $5.64
- Max loss: $5.64
- Max profit: $6.86
- Breakeven at expiry: $249.36
- Reward/risk estimate: 1.22x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0033; snapshot +0.0007

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bull Call Debit Spread

- Signal: LONG idea with base score -0.10% and final score 0.22%
- Underlying spot: $218.64
- Expiry: 2026-06-18
- Long leg: `NVDA260618C00219000` at strike $219.00 using recent close $5.30
- Short leg: `NVDA260618C00230000` at strike $230.00 using recent close $2.25
- Estimated net debit: $3.05
- Max loss: $3.05
- Max profit: $7.95
- Breakeven at expiry: $222.05
- Reward/risk estimate: 2.61x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0016; screener +0.0012

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## XOM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.16% and final score 0.17%
- Underlying spot: $152.09
- Expiry: 2026-06-18
- Long leg: `XOM260618C00152500` at strike $152.50 using recent close $4.15
- Short leg: `XOM260618C00160000` at strike $160.00 using recent close $1.57
- Estimated net debit: $2.58
- Max loss: $2.58
- Max profit: $4.92
- Breakeven at expiry: $155.08
- Reward/risk estimate: 1.91x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: No additional rationale captured.

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
