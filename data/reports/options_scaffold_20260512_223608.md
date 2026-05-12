# Options Scaffold Report

Generated at: 2026-05-12T22:36:08.867434+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.79% and final score 1.36%
- Underlying spot: $396.46
- Expiry: 2026-05-29
- Long leg: `UNH260529C00397500` at strike $397.50 using recent close $3.95
- Short leg: `UNH260529C00415000` at strike $415.00 using recent close $1.54
- Estimated net debit: $2.41
- Max loss: $2.41
- Max profit: $15.09
- Breakeven at expiry: $399.91
- Reward/risk estimate: 6.26x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0050; memory +0.0005

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bull Call Debit Spread

- Signal: LONG idea with base score 0.34% and final score 0.68%
- Underlying spot: $220.88
- Expiry: 2026-05-26
- Long leg: `NVDA260526C00220000` at strike $220.00 using recent close $9.05
- Short leg: `NVDA260526C00230000` at strike $230.00 using recent close $5.20
- Estimated net debit: $3.85
- Max loss: $3.85
- Max profit: $6.15
- Breakeven at expiry: $223.85
- Reward/risk estimate: 1.60x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0022; screener +0.0013

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.22% and final score 0.61%
- Underlying spot: $294.72
- Expiry: 2026-05-26
- Long leg: `AAPL260526C00295000` at strike $295.00 using recent close $4.60
- Short leg: `AAPL260526C00310000` at strike $310.00 using recent close $0.82
- Estimated net debit: $3.78
- Max loss: $3.78
- Max profit: $11.22
- Breakeven at expiry: $298.78
- Reward/risk estimate: 2.97x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0035; memory +0.0003

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.29% and final score 0.59%
- Underlying spot: $387.42
- Expiry: 2026-05-26
- Long leg: `GOOGL260526C00385000` at strike $385.00 using recent close $12.50
- Short leg: `GOOGL260526C00405000` at strike $405.00 using recent close $5.70
- Estimated net debit: $6.80
- Max loss: $6.80
- Max profit: $13.20
- Breakeven at expiry: $391.80
- Reward/risk estimate: 1.94x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0029

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## JPM — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.10% and final score -0.19%
- Underlying spot: $304.89
- Expiry: 2026-05-29
- Long leg: `JPM260529P00305000` at strike $305.00 using recent close $9.54
- Short leg: `JPM260529P00290000` at strike $290.00 using recent close $3.35
- Estimated net debit: $6.19
- Max loss: $6.19
- Max profit: $8.81
- Breakeven at expiry: $298.81
- Reward/risk estimate: 1.42x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0024; memory -0.0006

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## XOM — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.01% and final score -0.17%
- Underlying spot: $150.65
- Expiry: 2026-05-29
- Long leg: `XOM260529P00150000` at strike $150.00 using recent close $4.70
- Short leg: `XOM260529P00142000` at strike $142.00 using recent close $1.67
- Estimated net debit: $3.03
- Max loss: $3.03
- Max profit: $4.97
- Breakeven at expiry: $146.97
- Reward/risk estimate: 1.64x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0016

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
