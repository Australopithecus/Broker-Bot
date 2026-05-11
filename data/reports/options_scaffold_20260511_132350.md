# Options Scaffold Report

Generated at: 2026-05-11T13:23:50.612039+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.46% and final score 0.90%
- Underlying spot: $379.79
- Expiry: 2026-05-29
- Long leg: `UNH260529C00380000` at strike $380.00 using recent close $9.68
- Short leg: `UNH260529C00400000` at strike $400.00 using recent close $3.20
- Estimated net debit: $6.48
- Max loss: $6.48
- Max profit: $13.52
- Breakeven at expiry: $386.48
- Reward/risk estimate: 2.09x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0039

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.19% and final score 0.69%
- Underlying spot: $400.67
- Expiry: 2026-05-29
- Long leg: `GOOGL260529C00400000` at strike $400.00 using recent close $12.40
- Short leg: `GOOGL260529C00420000` at strike $420.00 using recent close $4.79
- Estimated net debit: $7.61
- Max loss: $7.61
- Max profit: $12.39
- Breakeven at expiry: $407.61
- Reward/risk estimate: 1.63x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0046; memory +0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bull Call Debit Spread

- Signal: LONG idea with base score 0.34% and final score 0.64%
- Underlying spot: $215.21
- Expiry: 2026-05-29
- Long leg: `NVDA260529C00215000` at strike $215.00 using recent close $10.05
- Short leg: `NVDA260529C00225000` at strike $225.00 using recent close $5.90
- Estimated net debit: $4.15
- Max loss: $4.15
- Max profit: $5.85
- Breakeven at expiry: $219.15
- Reward/risk estimate: 1.41x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0023; screener +0.0013; memory -0.0005

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.15% and final score 0.52%
- Underlying spot: $272.54
- Expiry: 2026-05-29
- Long leg: `AMZN260529C00275000` at strike $275.00 using recent close $6.23
- Short leg: `AMZN260529C00290000` at strike $290.00 using recent close $1.99
- Estimated net debit: $4.24
- Max loss: $4.24
- Max profit: $10.76
- Breakeven at expiry: $279.24
- Reward/risk estimate: 2.54x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0035

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.10% and final score 0.35%
- Underlying spot: $293.15
- Expiry: 2026-05-29
- Long leg: `AAPL260529C00295000` at strike $295.00 using recent close $5.80
- Short leg: `AAPL260529C00310000` at strike $310.00 using recent close $1.39
- Estimated net debit: $4.41
- Max loss: $4.41
- Max profit: $10.59
- Breakeven at expiry: $299.41
- Reward/risk estimate: 2.40x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0022

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## XOM — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.23% and final score -0.22%
- Underlying spot: $144.38
- Expiry: 2026-05-29
- Long leg: `XOM260529P00145000` at strike $145.00 using recent close $4.60
- Short leg: `XOM260529P00140000` at strike $140.00 using recent close $2.35
- Estimated net debit: $2.25
- Max loss: $2.25
- Max profit: $2.75
- Breakeven at expiry: $142.75
- Reward/risk estimate: 1.22x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0046

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
