# Options Scaffold Report

Generated at: 2026-06-12T22:47:52.576785+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## AMZN — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.31% and final score -0.57%
- Underlying spot: $238.56
- Expiry: 2026-06-26
- Long leg: `AMZN260626P00237500` at strike $237.50 using recent close $4.83
- Short leg: `AMZN260626P00225000` at strike $225.00 using recent close $1.45
- Estimated net debit: $3.38
- Max loss: $3.38
- Max profit: $9.12
- Breakeven at expiry: $234.12
- Reward/risk estimate: 2.70x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0024

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.25% and final score -0.55%
- Underlying spot: $205.17
- Expiry: 2026-06-26
- Long leg: `NVDA260626P00205000` at strike $205.00 using recent close $6.55
- Short leg: `NVDA260626P00195000` at strike $195.00 using recent close $2.82
- Estimated net debit: $3.73
- Max loss: $3.73
- Max profit: $6.27
- Breakeven at expiry: $201.27
- Reward/risk estimate: 1.68x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0031

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## JPM — Bull Call Debit Spread

- Signal: LONG idea with base score -0.15% and final score 0.45%
- Underlying spot: $320.71
- Expiry: 2026-06-26
- Long leg: `JPM260626C00320000` at strike $320.00 using recent close $4.35
- Short leg: `JPM260626C00335000` at strike $335.00 using recent close $0.84
- Estimated net debit: $3.51
- Max loss: $3.51
- Max profit: $11.49
- Breakeven at expiry: $323.51
- Reward/risk estimate: 3.27x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0050; snapshot +0.0010

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.33% and final score -0.42%
- Underlying spot: $359.65
- Expiry: 2026-06-26
- Long leg: `GOOGL260626P00360000` at strike $360.00 using recent close $10.07
- Short leg: `GOOGL260626P00340000` at strike $340.00 using recent close $3.28
- Estimated net debit: $6.79
- Max loss: $6.79
- Max profit: $13.21
- Breakeven at expiry: $353.21
- Reward/risk estimate: 1.95x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0012

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.53% and final score -0.42%
- Underlying spot: $291.08
- Expiry: 2026-06-26
- Long leg: `AAPL260626P00290000` at strike $290.00 using recent close $3.45
- Short leg: `AAPL260626P00275000` at strike $275.00 using recent close $0.80
- Estimated net debit: $2.65
- Max loss: $2.65
- Max profit: $12.35
- Breakeven at expiry: $287.35
- Reward/risk estimate: 4.66x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech +0.0012

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.07% and final score -0.23%
- Underlying spot: $566.92
- Expiry: 2026-06-26
- Long leg: `META260626P00567500` at strike $567.50 using recent close $14.75
- Short leg: `META260626P00540000` at strike $540.00 using recent close $5.60
- Estimated net debit: $9.15
- Max loss: $9.15
- Max profit: $18.35
- Breakeven at expiry: $558.35
- Reward/risk estimate: 2.01x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0016

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
