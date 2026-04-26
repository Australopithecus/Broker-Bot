# Options Scaffold Report

Generated at: 2026-04-26T13:31:39.202408+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.26% and final score 0.73%
- Underlying spot: $263.96
- Expiry: 2026-05-15
- Long leg: `AMZN260515C00265000` at strike $265.00 using recent close $11.18
- Short leg: `AMZN260515C00277500` at strike $277.50 using recent close $6.30
- Estimated net debit: $4.88
- Max loss: $4.88
- Max profit: $7.62
- Breakeven at expiry: $269.88
- Reward/risk estimate: 1.56x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0031; snapshot +0.0011; memory +0.0005

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.22% and final score 0.61%
- Underlying spot: $354.88
- Expiry: 2026-05-15
- Long leg: `UNH260515C00355000` at strike $355.00 using recent close $9.80
- Short leg: `UNH260515C00375000` at strike $375.00 using recent close $2.74
- Estimated net debit: $7.06
- Max loss: $7.06
- Max profit: $12.94
- Breakeven at expiry: $362.06
- Reward/risk estimate: 1.83x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0035

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bull Call Debit Spread

- Signal: LONG idea with base score 0.24% and final score 0.56%
- Underlying spot: $208.18
- Expiry: 2026-05-15
- Long leg: `NVDA260515C00207500` at strike $207.50 using recent close $8.00
- Short leg: `NVDA260515C00217500` at strike $217.50 using recent close $3.79
- Estimated net debit: $4.21
- Max loss: $4.21
- Max profit: $5.79
- Breakeven at expiry: $211.71
- Reward/risk estimate: 1.38x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0013; snapshot +0.0011; memory +0.0005

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bull Call Debit Spread

- Signal: LONG idea with base score 0.05% and final score 0.25%
- Underlying spot: $674.93
- Expiry: 2026-05-15
- Long leg: `META260515C00675000` at strike $675.00 using recent close $31.10
- Short leg: `META260515C00707500` at strike $707.50 using recent close $18.40
- Estimated net debit: $12.70
- Max loss: $12.70
- Max profit: $19.80
- Breakeven at expiry: $687.70
- Reward/risk estimate: 1.56x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0006; snapshot +0.0010; memory +0.0005

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.00% and final score 0.23%
- Underlying spot: $344.33
- Expiry: 2026-05-15
- Long leg: `GOOGL260515C00345000` at strike $345.00 using recent close $12.50
- Short leg: `GOOGL260515C00362500` at strike $362.50 using recent close $5.91
- Estimated net debit: $6.59
- Max loss: $6.59
- Max profit: $10.91
- Breakeven at expiry: $351.59
- Reward/risk estimate: 1.66x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0014; memory +0.0004

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## MSFT — Bull Call Debit Spread

- Signal: LONG idea with base score 0.08% and final score 0.14%
- Underlying spot: $424.59
- Expiry: 2026-05-15
- Long leg: `MSFT260515C00425000` at strike $425.00 using recent close $17.35
- Short leg: `MSFT260515C00445000` at strike $445.00 using recent close $9.40
- Estimated net debit: $7.95
- Max loss: $7.95
- Max profit: $12.05
- Breakeven at expiry: $432.95
- Reward/risk estimate: 1.52x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: snapshot +0.0005; memory +0.0005

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
