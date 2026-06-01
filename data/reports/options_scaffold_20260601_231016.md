# Options Scaffold Report

Generated at: 2026-06-01T23:10:16.548585+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## MSFT — Bull Call Debit Spread

- Signal: LONG idea with base score 0.59% and final score 0.94%
- Underlying spot: $460.48
- Expiry: 2026-06-18
- Long leg: `MSFT260618C00460000` at strike $460.00 using recent close $9.25
- Short leg: `MSFT260618C00485000` at strike $485.00 using recent close $3.22
- Estimated net debit: $6.03
- Max loss: $6.03
- Max profit: $18.97
- Breakeven at expiry: $466.03
- Reward/risk estimate: 3.15x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0033

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bull Call Debit Spread

- Signal: LONG idea with base score 0.20% and final score 0.88%
- Underlying spot: $224.42
- Expiry: 2026-06-18
- Long leg: `NVDA260618C00224000` at strike $224.00 using recent close $3.85
- Short leg: `NVDA260618C00235000` at strike $235.00 using recent close $1.83
- Estimated net debit: $2.02
- Max loss: $2.02
- Max profit: $8.98
- Breakeven at expiry: $226.02
- Reward/risk estimate: 4.45x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0035; snapshot +0.0019; screener +0.0013

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.44% and final score -0.53%
- Underlying spot: $600.50
- Expiry: 2026-06-18
- Long leg: `META260618P00600000` at strike $600.00 using recent close $6.00
- Short leg: `META260618P00570000` at strike $570.00 using recent close $1.94
- Estimated net debit: $4.06
- Max loss: $4.06
- Max profit: $25.94
- Breakeven at expiry: $595.94
- Reward/risk estimate: 6.39x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech +0.0008; snapshot -0.0015

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## JPM — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.03% and final score -0.31%
- Underlying spot: $296.68
- Expiry: 2026-06-18
- Long leg: `JPM260618P00297500` at strike $297.50 using recent close $6.20
- Short leg: `JPM260618P00282500` at strike $282.50 using recent close $1.76
- Estimated net debit: $4.44
- Max loss: $4.44
- Max profit: $10.56
- Breakeven at expiry: $293.06
- Reward/risk estimate: 2.38x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0029

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.03% and final score -0.23%
- Underlying spot: $376.26
- Expiry: 2026-06-18
- Long leg: `GOOGL260618P00377500` at strike $377.50 using recent close $8.75
- Short leg: `GOOGL260618P00360000` at strike $360.00 using recent close $3.15
- Estimated net debit: $5.60
- Max loss: $5.60
- Max profit: $11.90
- Breakeven at expiry: $371.90
- Reward/risk estimate: 2.12x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0006; snapshot -0.0013

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.02% and final score -0.22%
- Underlying spot: $261.20
- Expiry: 2026-06-18
- Long leg: `AMZN260618P00260000` at strike $260.00 using recent close $2.97
- Short leg: `AMZN260618P00247500` at strike $247.50 using recent close $1.00
- Estimated net debit: $1.97
- Max loss: $1.97
- Max profit: $10.53
- Breakeven at expiry: $258.03
- Reward/risk estimate: 5.35x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0012; snapshot -0.0010

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
