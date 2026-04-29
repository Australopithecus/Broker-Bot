# Options Scaffold Report

Generated at: 2026-04-29T18:44:56.022047+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.50% and final score 0.96%
- Underlying spot: $368.72
- Expiry: 2026-05-15
- Long leg: `UNH260515C00370000` at strike $370.00 using recent close $7.54
- Short leg: `UNH260515C00390000` at strike $390.00 using recent close $2.00
- Estimated net debit: $5.54
- Max loss: $5.54
- Max profit: $14.46
- Breakeven at expiry: $375.54
- Reward/risk estimate: 2.61x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0035; memory +0.0009

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.13% and final score 0.51%
- Underlying spot: $263.20
- Expiry: 2026-05-13
- Long leg: `AMZN260513C00265000` at strike $265.00 using recent close $8.10
- Short leg: `AMZN260513C00280000` at strike $280.00 using recent close $3.60
- Estimated net debit: $4.50
- Max loss: $4.50
- Max profit: $10.50
- Breakeven at expiry: $269.50
- Reward/risk estimate: 2.33x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0034

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.19% and final score 0.47%
- Underlying spot: $349.35
- Expiry: 2026-05-13
- Long leg: `GOOGL260513C00350000` at strike $350.00 using recent close $11.94
- Short leg: `GOOGL260513C00370000` at strike $370.00 using recent close $5.46
- Estimated net debit: $6.48
- Max loss: $6.48
- Max profit: $13.52
- Breakeven at expiry: $356.48
- Reward/risk estimate: 2.09x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0027

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## XOM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.54% and final score 0.32%
- Underlying spot: $153.91
- Expiry: 2026-05-15
- Long leg: `XOM260515C00155000` at strike $155.00 using recent close $2.70
- Short leg: `XOM260515C00162500` at strike $162.50 using recent close $0.99
- Estimated net debit: $1.71
- Max loss: $1.71
- Max profit: $5.79
- Breakeven at expiry: $156.71
- Reward/risk estimate: 3.39x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech -0.0028; snapshot +0.0006

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bull Call Debit Spread

- Signal: LONG idea with base score 0.29% and final score 0.29%
- Underlying spot: $671.67
- Expiry: 2026-05-13
- Long leg: `META260513C00670000` at strike $670.00 using recent close $29.55
- Short leg: `META260513C00705000` at strike $705.00 using recent close $15.83
- Estimated net debit: $13.72
- Max loss: $13.72
- Max profit: $21.28
- Breakeven at expiry: $683.72
- Reward/risk estimate: 1.55x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: No additional rationale captured.

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## MSFT — Bull Call Debit Spread

- Signal: LONG idea with base score 0.34% and final score 0.25%
- Underlying spot: $423.74
- Expiry: 2026-05-13
- Long leg: `MSFT260513C00425000` at strike $425.00 using recent close $20.25
- Short leg: `MSFT260513C00445000` at strike $445.00 using recent close $10.20
- Estimated net debit: $10.05
- Max loss: $10.05
- Max profit: $9.95
- Breakeven at expiry: $435.05
- Reward/risk estimate: 0.99x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech -0.0011; memory +0.0005

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
