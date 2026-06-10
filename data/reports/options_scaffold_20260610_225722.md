# Options Scaffold Report

Generated at: 2026-06-10T22:57:22.589529+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## GOOGL — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.24% and final score -0.42%
- Underlying spot: $356.33
- Expiry: 2026-06-24
- Long leg: `GOOGL260624P00355000` at strike $355.00 using recent close $4.59
- Short leg: `GOOGL260624P00340000` at strike $340.00 using recent close $1.71
- Estimated net debit: $2.88
- Max loss: $2.88
- Max profit: $12.12
- Breakeven at expiry: $352.12
- Reward/risk estimate: 4.21x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0011; snapshot -0.0006

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.01% and final score -0.34%
- Underlying spot: $237.97
- Expiry: 2026-06-24
- Long leg: `AMZN260624P00240000` at strike $240.00 using recent close $4.30
- Short leg: `AMZN260624P00230000` at strike $230.00 using recent close $1.63
- Estimated net debit: $2.67
- Max loss: $2.67
- Max profit: $7.33
- Breakeven at expiry: $237.33
- Reward/risk estimate: 2.75x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0027; snapshot -0.0007

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## JPM — Bull Call Debit Spread

- Signal: LONG idea with base score -0.00% and final score 0.31%
- Underlying spot: $309.12
- Expiry: 2026-06-26
- Long leg: `JPM260626C00310000` at strike $310.00 using recent close $9.00
- Short leg: `JPM260626C00325000` at strike $325.00 using recent close $2.63
- Estimated net debit: $6.37
- Max loss: $6.37
- Max profit: $8.63
- Breakeven at expiry: $316.37
- Reward/risk estimate: 1.35x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0033

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## XOM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.10% and final score 0.27%
- Underlying spot: $150.68
- Expiry: 2026-06-26
- Long leg: `XOM260626C00150000` at strike $150.00 using recent close $3.85
- Short leg: `XOM260626C00157500` at strike $157.50 using recent close $1.54
- Estimated net debit: $2.31
- Max loss: $2.31
- Max profit: $5.19
- Breakeven at expiry: $152.31
- Reward/risk estimate: 2.25x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0012; snapshot +0.0006

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.07% and final score -0.20%
- Underlying spot: $571.04
- Expiry: 2026-06-24
- Long leg: `META260624P00570000` at strike $570.00 using recent close $8.70
- Short leg: `META260624P00535000` at strike $535.00 using recent close $2.40
- Estimated net debit: $6.30
- Max loss: $6.30
- Max profit: $28.70
- Breakeven at expiry: $563.70
- Reward/risk estimate: 4.56x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0021

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## PG — Bull Call Debit Spread

- Signal: LONG idea with base score -0.32% and final score 0.20%
- Underlying spot: $149.07
- Expiry: 2026-06-26
- Long leg: `PG260626C00149000` at strike $149.00 using recent close $2.73
- Short leg: `PG260626C00157500` at strike $157.50 using recent close $0.55
- Estimated net debit: $2.18
- Max loss: $2.18
- Max profit: $6.32
- Breakeven at expiry: $151.18
- Reward/risk estimate: 2.90x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0045; snapshot +0.0006

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
