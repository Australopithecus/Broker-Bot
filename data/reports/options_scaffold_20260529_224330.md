# Options Scaffold Report

Generated at: 2026-05-29T22:43:30.671650+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## MSFT — Bull Call Debit Spread

- Signal: LONG idea with base score 0.47% and final score 0.93%
- Underlying spot: $449.44
- Expiry: 2026-06-12
- Long leg: `MSFT260612C00450000` at strike $450.00 using recent close $3.40
- Short leg: `MSFT260612C00470000` at strike $470.00 using recent close $1.05
- Estimated net debit: $2.35
- Max loss: $2.35
- Max profit: $17.65
- Breakeven at expiry: $452.35
- Reward/risk estimate: 7.51x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0035; snapshot +0.0013

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.30% and final score 0.81%
- Underlying spot: $312.01
- Expiry: 2026-06-12
- Long leg: `AAPL260612C00312500` at strike $312.50 using recent close $5.95
- Short leg: `AAPL260612C00330000` at strike $330.00 using recent close $0.89
- Estimated net debit: $5.06
- Max loss: $5.06
- Max profit: $12.44
- Breakeven at expiry: $317.56
- Reward/risk estimate: 2.46x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0050

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## XOM — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.02% and final score -0.48%
- Underlying spot: $145.34
- Expiry: 2026-06-12
- Long leg: `XOM260612P00145000` at strike $145.00 using recent close $2.35
- Short leg: `XOM260612P00140000` at strike $140.00 using recent close $0.95
- Estimated net debit: $1.40
- Max loss: $1.40
- Max profit: $3.60
- Breakeven at expiry: $143.60
- Reward/risk estimate: 2.57x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0045

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bull Call Debit Spread

- Signal: LONG idea with base score 0.08% and final score 0.34%
- Underlying spot: $632.52
- Expiry: 2026-06-12
- Long leg: `META260612C00632500` at strike $632.50 using recent close $18.25
- Short leg: `META260612C00665000` at strike $665.00 using recent close $6.60
- Estimated net debit: $11.65
- Max loss: $11.65
- Max profit: $20.85
- Breakeven at expiry: $644.15
- Reward/risk estimate: 1.79x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0029

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
