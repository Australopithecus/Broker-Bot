# Options Scaffold Report

Generated at: 2026-05-22T14:30:37.481051+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.21% and final score 0.75%
- Underlying spot: $308.64
- Expiry: 2026-06-05
- Long leg: `AAPL260605C00307500` at strike $307.50 using recent close $4.20
- Short leg: `AAPL260605C00322500` at strike $322.50 using recent close $0.52
- Estimated net debit: $3.68
- Max loss: $3.68
- Max profit: $11.32
- Breakeven at expiry: $311.18
- Reward/risk estimate: 3.08x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0051

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.17% and final score 0.39%
- Underlying spot: $387.38
- Expiry: 2026-06-05
- Long leg: `UNH260605C00387500` at strike $387.50 using recent close $6.75
- Short leg: `UNH260605C00407500` at strike $407.50 using recent close $1.54
- Estimated net debit: $5.21
- Max loss: $5.21
- Max profit: $14.79
- Breakeven at expiry: $392.71
- Reward/risk estimate: 2.84x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0019

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.13% and final score -0.19%
- Underlying spot: $608.60
- Expiry: 2026-06-05
- Long leg: `META260605P00607500` at strike $607.50 using recent close $13.95
- Short leg: `META260605P00575000` at strike $575.00 using recent close $3.55
- Estimated net debit: $10.40
- Max loss: $10.40
- Max profit: $22.10
- Breakeven at expiry: $597.10
- Reward/risk estimate: 2.13x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0031

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
