# Options Scaffold Report

Generated at: 2026-04-27T13:53:16.839446+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.68% and final score 1.06%
- Underlying spot: $352.47
- Expiry: 2026-05-15
- Long leg: `UNH260515C00350000` at strike $350.00 using recent close $12.61
- Short leg: `UNH260515C00370000` at strike $370.00 using recent close $3.89
- Estimated net debit: $8.72
- Max loss: $8.72
- Max profit: $11.28
- Breakeven at expiry: $358.72
- Reward/risk estimate: 1.29x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0035

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bull Call Debit Spread

- Signal: LONG idea with base score 0.39% and final score 0.58%
- Underlying spot: $676.89
- Expiry: 2026-05-15
- Long leg: `META260515C00677500` at strike $677.50 using recent close $32.00
- Short leg: `META260515C00710000` at strike $710.00 using recent close $16.90
- Estimated net debit: $15.10
- Max loss: $15.10
- Max profit: $17.40
- Breakeven at expiry: $692.60
- Reward/risk estimate: 1.15x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0012; memory +0.0005

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## MSFT — Bull Call Debit Spread

- Signal: LONG idea with base score 0.50% and final score 0.47%
- Underlying spot: $420.34
- Expiry: 2026-05-15
- Long leg: `MSFT260515C00420000` at strike $420.00 using recent close $20.00
- Short leg: `MSFT260515C00440000` at strike $440.00 using recent close $11.05
- Estimated net debit: $8.95
- Max loss: $8.95
- Max profit: $11.05
- Breakeven at expiry: $428.95
- Reward/risk estimate: 1.23x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech -0.0007

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.06% and final score 0.44%
- Underlying spot: $260.55
- Expiry: 2026-05-15
- Long leg: `AMZN260515C00260000` at strike $260.00 using recent close $13.70
- Short leg: `AMZN260515C00272500` at strike $272.50 using recent close $8.00
- Estimated net debit: $5.70
- Max loss: $5.70
- Max profit: $6.80
- Breakeven at expiry: $265.70
- Reward/risk estimate: 1.19x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0034; memory +0.0003

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bull Call Debit Spread

- Signal: LONG idea with base score 0.20% and final score 0.43%
- Underlying spot: $208.77
- Expiry: 2026-05-15
- Long leg: `NVDA260515C00210000` at strike $210.00 using recent close $6.77
- Short leg: `NVDA260515C00220000` at strike $220.00 using recent close $3.05
- Estimated net debit: $3.72
- Max loss: $3.72
- Max profit: $6.28
- Breakeven at expiry: $213.72
- Reward/risk estimate: 1.69x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0009; memory +0.0010

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.07% and final score 0.37%
- Underlying spot: $346.76
- Expiry: 2026-05-15
- Long leg: `GOOGL260515C00347500` at strike $347.50 using recent close $11.50
- Short leg: `GOOGL260515C00365000` at strike $365.00 using recent close $5.25
- Estimated net debit: $6.25
- Max loss: $6.25
- Max profit: $11.25
- Breakeven at expiry: $353.75
- Reward/risk estimate: 1.80x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0016; snapshot +0.0007; memory +0.0007

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
