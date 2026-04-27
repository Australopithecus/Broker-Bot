# Options Scaffold Report

Generated at: 2026-04-27T22:07:29.589622+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## NVDA — Bull Call Debit Spread

- Signal: LONG idea with base score 0.48% and final score 0.98%
- Underlying spot: $216.54
- Expiry: 2026-05-15
- Long leg: `NVDA260515C00217500` at strike $217.50 using recent close $3.79
- Short leg: `NVDA260515C00230000` at strike $230.00 using recent close $1.24
- Estimated net debit: $2.55
- Max loss: $2.55
- Max profit: $9.95
- Breakeven at expiry: $220.05
- Reward/risk estimate: 3.90x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0025; snapshot +0.0012; memory +0.0010

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.58% and final score 0.95%
- Underlying spot: $354.69
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

## META — Bull Call Debit Spread

- Signal: LONG idea with base score 0.49% and final score 0.62%
- Underlying spot: $678.50
- Expiry: 2026-05-15
- Long leg: `META260515C00677500` at strike $677.50 using recent close $32.00
- Short leg: `META260515C00710000` at strike $710.00 using recent close $16.90
- Estimated net debit: $15.10
- Max loss: $15.10
- Max profit: $17.40
- Breakeven at expiry: $692.60
- Reward/risk estimate: 1.15x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: memory +0.0005

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## MSFT — Bull Call Debit Spread

- Signal: LONG idea with base score 0.54% and final score 0.57%
- Underlying spot: $424.96
- Expiry: 2026-05-15
- Long leg: `MSFT260515C00425000` at strike $425.00 using recent close $17.35
- Short leg: `MSFT260515C00445000` at strike $445.00 using recent close $9.40
- Estimated net debit: $7.95
- Max loss: $7.95
- Max profit: $12.05
- Breakeven at expiry: $432.95
- Reward/risk estimate: 1.52x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: No additional rationale captured.

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.21% and final score 0.54%
- Underlying spot: $261.05
- Expiry: 2026-05-15
- Long leg: `AMZN260515C00260000` at strike $260.00 using recent close $13.70
- Short leg: `AMZN260515C00272500` at strike $272.50 using recent close $8.00
- Estimated net debit: $5.70
- Max loss: $5.70
- Max profit: $6.80
- Breakeven at expiry: $265.70
- Reward/risk estimate: 1.19x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0032; memory +0.0003

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.26% and final score 0.50%
- Underlying spot: $350.30
- Expiry: 2026-05-15
- Long leg: `GOOGL260515C00350000` at strike $350.00 using recent close $10.10
- Short leg: `GOOGL260515C00370000` at strike $370.00 using recent close $4.15
- Estimated net debit: $5.95
- Max loss: $5.95
- Max profit: $14.05
- Breakeven at expiry: $355.95
- Reward/risk estimate: 2.36x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0012; snapshot +0.0006; memory +0.0007

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
