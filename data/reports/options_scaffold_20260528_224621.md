# Options Scaffold Report

Generated at: 2026-05-28T22:46:21.595477+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.34% and final score 0.89%
- Underlying spot: $312.45
- Expiry: 2026-06-12
- Long leg: `AAPL260612C00312500` at strike $312.50 using recent close $5.55
- Short leg: `AAPL260612C00330000` at strike $330.00 using recent close $0.89
- Estimated net debit: $4.66
- Max loss: $4.66
- Max profit: $12.84
- Breakeven at expiry: $317.16
- Reward/risk estimate: 2.76x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0052

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.47% and final score 0.81%
- Underlying spot: $273.98
- Expiry: 2026-06-12
- Long leg: `AMZN260612C00275000` at strike $275.00 using recent close $5.70
- Short leg: `AMZN260612C00287500` at strike $287.50 using recent close $2.13
- Estimated net debit: $3.57
- Max loss: $3.57
- Max profit: $8.93
- Breakeven at expiry: $278.57
- Reward/risk estimate: 2.50x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0034

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.27% and final score 0.48%
- Underlying spot: $390.15
- Expiry: 2026-06-12
- Long leg: `GOOGL260612C00390000` at strike $390.00 using recent close $9.60
- Short leg: `GOOGL260612C00410000` at strike $410.00 using recent close $3.25
- Estimated net debit: $6.35
- Max loss: $6.35
- Max profit: $13.65
- Breakeven at expiry: $396.35
- Reward/risk estimate: 2.15x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0021

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## MSFT — Bull Call Debit Spread

- Signal: LONG idea with base score 0.30% and final score 0.36%
- Underlying spot: $426.97
- Expiry: 2026-06-12
- Long leg: `MSFT260612C00427500` at strike $427.50 using recent close $4.96
- Short leg: `MSFT260612C00450000` at strike $450.00 using recent close $1.40
- Estimated net debit: $3.56
- Max loss: $3.56
- Max profit: $18.94
- Breakeven at expiry: $431.06
- Reward/risk estimate: 5.32x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: snapshot +0.0008

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.19% and final score 0.34%
- Underlying spot: $382.41
- Expiry: 2026-06-12
- Long leg: `UNH260612C00382500` at strike $382.50 using recent close $10.25
- Short leg: `UNH260612C00402500` at strike $402.50 using recent close $2.69
- Estimated net debit: $7.56
- Max loss: $7.56
- Max profit: $12.44
- Breakeven at expiry: $390.06
- Reward/risk estimate: 1.65x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0012

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## XOM — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.12% and final score -0.24%
- Underlying spot: $146.99
- Expiry: 2026-06-12
- Long leg: `XOM260612P00147000` at strike $147.00 using recent close $3.33
- Short leg: `XOM260612P00140000` at strike $140.00 using recent close $0.99
- Estimated net debit: $2.34
- Max loss: $2.34
- Max profit: $4.66
- Breakeven at expiry: $144.66
- Reward/risk estimate: 1.99x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0034

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
