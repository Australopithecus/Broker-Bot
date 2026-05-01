# Options Scaffold Report

Generated at: 2026-05-01T12:55:53.717713+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.62% and final score 1.24%
- Underlying spot: $384.99
- Expiry: 2026-05-15
- Long leg: `GOOGL260515C00385000` at strike $385.00 using recent close $10.06
- Short leg: `GOOGL260515C00405000` at strike $405.00 using recent close $3.60
- Estimated net debit: $6.46
- Max loss: $6.46
- Max profit: $13.54
- Breakeven at expiry: $391.46
- Reward/risk estimate: 2.10x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0032; snapshot +0.0024; memory +0.0006

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.32% and final score 0.78%
- Underlying spot: $370.58
- Expiry: 2026-05-15
- Long leg: `UNH260515C00370000` at strike $370.00 using recent close $8.60
- Short leg: `UNH260515C00390000` at strike $390.00 using recent close $1.78
- Estimated net debit: $6.82
- Max loss: $6.82
- Max profit: $13.18
- Breakeven at expiry: $376.82
- Reward/risk estimate: 1.93x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0035; memory +0.0008

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.16% and final score -0.38%
- Underlying spot: $612.16
- Expiry: 2026-05-15
- Long leg: `META260515P00610000` at strike $610.00 using recent close $15.15
- Short leg: `META260515P00580000` at strike $580.00 using recent close $5.10
- Estimated net debit: $10.05
- Max loss: $10.05
- Max profit: $19.95
- Breakeven at expiry: $599.95
- Reward/risk estimate: 1.99x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0029; snapshot -0.0021; memory -0.0005

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.03% and final score 0.33%
- Underlying spot: $265.04
- Expiry: 2026-05-15
- Long leg: `AMZN260515C00265000` at strike $265.00 using recent close $6.70
- Short leg: `AMZN260515C00277500` at strike $277.50 using recent close $2.25
- Estimated net debit: $4.45
- Max loss: $4.45
- Max profit: $8.05
- Breakeven at expiry: $269.45
- Reward/risk estimate: 1.81x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0027

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## JPM — Bull Call Debit Spread

- Signal: LONG idea with base score 0.18% and final score 0.23%
- Underlying spot: $313.30
- Expiry: 2026-05-15
- Long leg: `JPM260515C00312500` at strike $312.50 using recent close $6.87
- Short leg: `JPM260515C00327500` at strike $327.50 using recent close $1.20
- Estimated net debit: $5.67
- Max loss: $5.67
- Max profit: $9.33
- Breakeven at expiry: $318.17
- Reward/risk estimate: 1.65x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: snapshot +0.0008

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.13% and final score -0.15%
- Underlying spot: $199.54
- Expiry: 2026-05-15
- Long leg: `NVDA260515P00200000` at strike $200.00 using recent close $6.25
- Short leg: `NVDA260515P00190000` at strike $190.00 using recent close $2.62
- Estimated net debit: $3.63
- Max loss: $3.63
- Max profit: $6.37
- Breakeven at expiry: $196.37
- Reward/risk estimate: 1.75x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech +0.0008; snapshot -0.0009; memory -0.0004

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
