# Options Scaffold Report

Generated at: 2026-05-21T22:42:15.395990+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.19% and final score 0.64%
- Underlying spot: $305.07
- Expiry: 2026-06-05
- Long leg: `AAPL260605C00305000` at strike $305.00 using recent close $4.40
- Short leg: `AAPL260605C00320000` at strike $320.00 using recent close $0.80
- Estimated net debit: $3.60
- Max loss: $3.60
- Max profit: $11.40
- Breakeven at expiry: $308.60
- Reward/risk estimate: 3.17x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0043

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.13% and final score -0.23%
- Underlying spot: $607.34
- Expiry: 2026-06-05
- Long leg: `META260605P00607500` at strike $607.50 using recent close $16.60
- Short leg: `META260605P00575000` at strike $575.00 using recent close $4.90
- Estimated net debit: $11.70
- Max loss: $11.70
- Max profit: $20.80
- Breakeven at expiry: $595.80
- Reward/risk estimate: 1.78x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0035

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score -0.03% and final score 0.22%
- Underlying spot: $387.52
- Expiry: 2026-06-05
- Long leg: `GOOGL260605C00387500` at strike $387.50 using recent close $11.25
- Short leg: `GOOGL260605C00407500` at strike $407.50 using recent close $3.50
- Estimated net debit: $7.75
- Max loss: $7.75
- Max profit: $12.25
- Breakeven at expiry: $395.25
- Reward/risk estimate: 1.58x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0024

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.05% and final score 0.15%
- Underlying spot: $268.50
- Expiry: 2026-06-05
- Long leg: `AMZN260605C00267500` at strike $267.50 using recent close $5.25
- Short leg: `AMZN260605C00280000` at strike $280.00 using recent close $1.76
- Estimated net debit: $3.49
- Max loss: $3.49
- Max profit: $9.01
- Breakeven at expiry: $270.99
- Reward/risk estimate: 2.58x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0011

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
