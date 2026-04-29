# Options Scaffold Report

Generated at: 2026-04-29T22:12:01.541545+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.36% and final score 0.85%
- Underlying spot: $370.71
- Expiry: 2026-05-15
- Long leg: `UNH260515C00370000` at strike $370.00 using recent close $7.54
- Short leg: `UNH260515C00390000` at strike $390.00 using recent close $2.00
- Estimated net debit: $5.54
- Max loss: $5.54
- Max profit: $14.46
- Breakeven at expiry: $375.54
- Reward/risk estimate: 2.61x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0035; snapshot +0.0005; memory +0.0010

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score -0.01% and final score 0.48%
- Underlying spot: $350.27
- Expiry: 2026-05-13
- Long leg: `GOOGL260513C00350000` at strike $350.00 using recent close $11.94
- Short leg: `GOOGL260513C00370000` at strike $370.00 using recent close $5.46
- Estimated net debit: $6.48
- Max loss: $6.48
- Max profit: $13.52
- Breakeven at expiry: $356.48
- Reward/risk estimate: 2.09x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0025; snapshot +0.0023

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## XOM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.49% and final score 0.33%
- Underlying spot: $154.65
- Expiry: 2026-05-15
- Long leg: `XOM260515C00155000` at strike $155.00 using recent close $2.70
- Short leg: `XOM260515C00162500` at strike $162.50 using recent close $0.99
- Estimated net debit: $1.71
- Max loss: $1.71
- Max profit: $5.79
- Breakeven at expiry: $156.71
- Reward/risk estimate: 3.39x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech -0.0026; snapshot +0.0010

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.10% and final score 0.29%
- Underlying spot: $263.22
- Expiry: 2026-05-13
- Long leg: `AMZN260513C00265000` at strike $265.00 using recent close $8.10
- Short leg: `AMZN260513C00280000` at strike $280.00 using recent close $3.60
- Estimated net debit: $4.50
- Max loss: $4.50
- Max profit: $10.50
- Breakeven at expiry: $269.50
- Reward/risk estimate: 2.33x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0028; snapshot -0.0010

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.38% and final score -0.22%
- Underlying spot: $209.35
- Expiry: 2026-05-13
- Long leg: `NVDA260513P00210000` at strike $210.00 using recent close $4.94
- Short leg: `NVDA260513P00200000` at strike $200.00 using recent close $2.14
- Estimated net debit: $2.80
- Max loss: $2.80
- Max profit: $7.20
- Breakeven at expiry: $207.20
- Reward/risk estimate: 2.57x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech +0.0020; snapshot -0.0005

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
