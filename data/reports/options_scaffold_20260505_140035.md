# Options Scaffold Report

Generated at: 2026-05-05T14:00:35.166718+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.40% and final score 0.84%
- Underlying spot: $387.99
- Expiry: 2026-05-22
- Long leg: `GOOGL260522C00387500` at strike $387.50 using recent close $8.90
- Short leg: `GOOGL260522C00407500` at strike $407.50 using recent close $3.28
- Estimated net debit: $5.62
- Max loss: $5.62
- Max profit: $14.38
- Breakeven at expiry: $393.12
- Reward/risk estimate: 2.56x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0033; snapshot +0.0006; memory +0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.08% and final score 0.65%
- Underlying spot: $276.11
- Expiry: 2026-05-22
- Long leg: `AMZN260522C00275000` at strike $275.00 using recent close $5.80
- Short leg: `AMZN260522C00290000` at strike $290.00 using recent close $1.70
- Estimated net debit: $4.10
- Max loss: $4.10
- Max profit: $10.90
- Breakeven at expiry: $279.10
- Reward/risk estimate: 2.66x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0047; snapshot +0.0005; memory +0.0005

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.05% and final score 0.32%
- Underlying spot: $368.79
- Expiry: 2026-05-22
- Long leg: `UNH260522C00370000` at strike $370.00 using recent close $9.20
- Short leg: `UNH260522C00387500` at strike $387.50 using recent close $2.29
- Estimated net debit: $6.91
- Max loss: $6.91
- Max profit: $10.59
- Breakeven at expiry: $376.91
- Reward/risk estimate: 1.53x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0022

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.01% and final score -0.27%
- Underlying spot: $606.94
- Expiry: 2026-05-22
- Long leg: `META260522P00607500` at strike $607.50 using recent close $14.43
- Short leg: `META260522P00577500` at strike $577.50 using recent close $5.30
- Estimated net debit: $9.13
- Max loss: $9.13
- Max profit: $20.87
- Breakeven at expiry: $598.37
- Reward/risk estimate: 2.29x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0024; memory -0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.02% and final score 0.17%
- Underlying spot: $279.62
- Expiry: 2026-05-22
- Long leg: `AAPL260522C00280000` at strike $280.00 using recent close $4.50
- Short leg: `AAPL260522C00295000` at strike $295.00 using recent close $0.85
- Estimated net debit: $3.65
- Max loss: $3.65
- Max profit: $11.35
- Breakeven at expiry: $283.65
- Reward/risk estimate: 3.11x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0010; snapshot +0.0005

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
