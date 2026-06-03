# Options Scaffold Report

Generated at: 2026-06-03T23:15:11.685403+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## XOM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.36% and final score 0.46%
- Underlying spot: $152.74
- Expiry: 2026-06-18
- Long leg: `XOM260618C00152500` at strike $152.50 using recent close $3.10
- Short leg: `XOM260618C00160000` at strike $160.00 using recent close $1.07
- Estimated net debit: $2.03
- Max loss: $2.03
- Max profit: $5.47
- Breakeven at expiry: $154.53
- Reward/risk estimate: 2.69x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: snapshot +0.0008

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bull Call Debit Spread

- Signal: LONG idea with base score 0.37% and final score 0.45%
- Underlying spot: $623.05
- Expiry: 2026-06-17
- Long leg: `META260617C00625000` at strike $625.00 using recent close $9.45
- Short leg: `META260617C00655000` at strike $655.00 using recent close $4.53
- Estimated net debit: $4.92
- Max loss: $4.92
- Max profit: $25.08
- Breakeven at expiry: $629.92
- Reward/risk estimate: 5.10x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: snapshot +0.0010; memory -0.0003

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.06% and final score 0.38%
- Underlying spot: $310.22
- Expiry: 2026-06-17
- Long leg: `AAPL260617C00310000` at strike $310.00 using recent close $9.54
- Short leg: `AAPL260617C00325000` at strike $325.00 using recent close $2.78
- Estimated net debit: $6.76
- Max loss: $6.76
- Max profit: $8.24
- Breakeven at expiry: $316.76
- Reward/risk estimate: 1.22x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0034

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.02% and final score -0.38%
- Underlying spot: $249.99
- Expiry: 2026-06-17
- Long leg: `AMZN260617P00250000` at strike $250.00 using recent close $3.22
- Short leg: `AMZN260617P00240000` at strike $240.00 using recent close $1.12
- Estimated net debit: $2.10
- Max loss: $2.10
- Max profit: $7.90
- Breakeven at expiry: $247.90
- Reward/risk estimate: 3.76x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0034

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.04% and final score -0.27%
- Underlying spot: $359.37
- Expiry: 2026-06-17
- Long leg: `GOOGL260617P00360000` at strike $360.00 using recent close $7.93
- Short leg: `GOOGL260617P00340000` at strike $340.00 using recent close $1.95
- Estimated net debit: $5.98
- Max loss: $5.98
- Max profit: $14.02
- Breakeven at expiry: $354.02
- Reward/risk estimate: 2.34x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0027

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
