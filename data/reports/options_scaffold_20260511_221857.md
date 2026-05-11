# Options Scaffold Report

Generated at: 2026-05-11T22:18:57.740674+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.88% and final score 1.20%
- Underlying spot: $388.64
- Expiry: 2026-06-05
- Long leg: `GOOGL260605C00390000` at strike $390.00 using recent close $20.50
- Short leg: `GOOGL260605C00410000` at strike $410.00 using recent close $10.15
- Estimated net debit: $10.35
- Max loss: $10.35
- Max profit: $9.65
- Breakeven at expiry: $400.35
- Reward/risk estimate: 0.93x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0029; memory +0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bull Call Debit Spread

- Signal: LONG idea with base score 0.51% and final score 0.94%
- Underlying spot: $219.45
- Expiry: 2026-05-29
- Long leg: `NVDA260529C00220000` at strike $220.00 using recent close $7.77
- Short leg: `NVDA260529C00230000` at strike $230.00 using recent close $4.41
- Estimated net debit: $3.36
- Max loss: $3.36
- Max profit: $6.64
- Breakeven at expiry: $223.36
- Reward/risk estimate: 1.98x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0033; screener +0.0013; memory -0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.24% and final score 0.78%
- Underlying spot: $384.46
- Expiry: 2026-05-29
- Long leg: `UNH260529C00385000` at strike $385.00 using recent close $7.32
- Short leg: `UNH260529C00405000` at strike $405.00 using recent close $2.37
- Estimated net debit: $4.95
- Max loss: $4.95
- Max profit: $15.05
- Breakeven at expiry: $389.95
- Reward/risk estimate: 3.04x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0050

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.11% and final score -0.60%
- Underlying spot: $598.71
- Expiry: 2026-05-29
- Long leg: `META260529P00600000` at strike $600.00 using recent close $11.90
- Short leg: `META260529P00570000` at strike $570.00 using recent close $3.95
- Estimated net debit: $7.95
- Max loss: $7.95
- Max profit: $22.05
- Breakeven at expiry: $592.05
- Reward/risk estimate: 2.77x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0047

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## JPM — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.01% and final score -0.29%
- Underlying spot: $299.81
- Expiry: 2026-05-29
- Long leg: `JPM260529P00300000` at strike $300.00 using recent close $5.90
- Short leg: `JPM260529P00285000` at strike $285.00 using recent close $1.90
- Estimated net debit: $4.00
- Max loss: $4.00
- Max profit: $11.00
- Breakeven at expiry: $296.00
- Reward/risk estimate: 2.75x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0026; memory -0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score -0.04% and final score 0.28%
- Underlying spot: $292.66
- Expiry: 2026-05-29
- Long leg: `AAPL260529C00295000` at strike $295.00 using recent close $5.80
- Short leg: `AAPL260529C00310000` at strike $310.00 using recent close $1.39
- Estimated net debit: $4.41
- Max loss: $4.41
- Max profit: $10.59
- Breakeven at expiry: $299.41
- Reward/risk estimate: 2.40x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0029

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
