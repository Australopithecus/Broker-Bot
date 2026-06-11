# Options Scaffold Report

Generated at: 2026-06-11T14:48:38.665679+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## MSFT — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.16% and final score -0.35%
- Underlying spot: $389.93
- Expiry: 2026-06-26
- Long leg: `MSFT260626P00390000` at strike $390.00 using recent close $6.90
- Short leg: `MSFT260626P00370000` at strike $370.00 using recent close $2.30
- Estimated net debit: $4.60
- Max loss: $4.60
- Max profit: $15.40
- Breakeven at expiry: $385.40
- Reward/risk estimate: 3.35x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0012; snapshot -0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.01% and final score -0.28%
- Underlying spot: $348.25
- Expiry: 2026-06-26
- Long leg: `GOOGL260626P00347500` at strike $347.50 using recent close $5.60
- Short leg: `GOOGL260626P00330000` at strike $330.00 using recent close $2.02
- Estimated net debit: $3.58
- Max loss: $3.58
- Max profit: $13.92
- Breakeven at expiry: $343.92
- Reward/risk estimate: 3.89x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0023; snapshot -0.0005

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## PG — Bull Call Debit Spread

- Signal: LONG idea with base score -0.21% and final score 0.27%
- Underlying spot: $148.94
- Expiry: 2026-06-26
- Long leg: `PG260626C00149000` at strike $149.00 using recent close $3.15
- Short leg: `PG260626C00157500` at strike $157.50 using recent close $0.46
- Estimated net debit: $2.69
- Max loss: $2.69
- Max profit: $5.81
- Breakeven at expiry: $151.69
- Reward/risk estimate: 2.16x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0047

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score -0.02% and final score 0.27%
- Underlying spot: $406.72
- Expiry: 2026-06-26
- Long leg: `UNH260626C00407500` at strike $407.50 using recent close $7.85
- Short leg: `UNH260626C00430000` at strike $430.00 using recent close $2.25
- Estimated net debit: $5.60
- Max loss: $5.60
- Max profit: $16.90
- Breakeven at expiry: $413.10
- Reward/risk estimate: 3.02x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0027

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## JPM — Bull Call Debit Spread

- Signal: LONG idea with base score -0.20% and final score 0.21%
- Underlying spot: $311.51
- Expiry: 2026-06-26
- Long leg: `JPM260626C00312500` at strike $312.50 using recent close $7.17
- Short leg: `JPM260626C00327500` at strike $327.50 using recent close $1.46
- Estimated net debit: $5.71
- Max loss: $5.71
- Max profit: $9.29
- Breakeven at expiry: $318.21
- Reward/risk estimate: 1.63x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0039

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.32% and final score -0.18%
- Underlying spot: $290.97
- Expiry: 2026-06-26
- Long leg: `AAPL260626P00290000` at strike $290.00 using recent close $5.35
- Short leg: `AAPL260626P00275000` at strike $275.00 using recent close $1.48
- Estimated net debit: $3.87
- Max loss: $3.87
- Max profit: $11.13
- Breakeven at expiry: $286.13
- Reward/risk estimate: 2.88x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech +0.0011

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
