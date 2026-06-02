# Options Scaffold Report

Generated at: 2026-06-02T23:09:26.769315+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## AAPL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.21% and final score 0.81%
- Underlying spot: $315.19
- Expiry: 2026-06-18
- Long leg: `AAPL260618C00315000` at strike $315.00 using recent close $3.30
- Short leg: `AAPL260618C00330000` at strike $330.00 using recent close $0.84
- Estimated net debit: $2.46
- Max loss: $2.46
- Max profit: $12.54
- Breakeven at expiry: $317.46
- Reward/risk estimate: 5.10x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0046; snapshot +0.0012

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.11% and final score -0.48%
- Underlying spot: $256.53
- Expiry: 2026-06-18
- Long leg: `AMZN260618P00257500` at strike $257.50 using recent close $5.28
- Short leg: `AMZN260618P00245000` at strike $245.00 using recent close $1.89
- Estimated net debit: $3.39
- Max loss: $3.39
- Max profit: $9.11
- Breakeven at expiry: $254.11
- Reward/risk estimate: 2.69x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0032

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.33% and final score -0.38%
- Underlying spot: $597.73
- Expiry: 2026-06-18
- Long leg: `META260618P00597500` at strike $597.50 using recent close $17.45
- Short leg: `META260618P00570000` at strike $570.00 using recent close $7.00
- Estimated net debit: $10.45
- Max loss: $10.45
- Max profit: $17.05
- Breakeven at expiry: $587.05
- Reward/risk estimate: 1.63x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0006

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.06% and final score -0.37%
- Underlying spot: $361.84
- Expiry: 2026-06-18
- Long leg: `GOOGL260618P00360000` at strike $360.00 using recent close $3.63
- Short leg: `GOOGL260618P00340000` at strike $340.00 using recent close $1.00
- Estimated net debit: $2.63
- Max loss: $2.63
- Max profit: $17.37
- Breakeven at expiry: $357.37
- Reward/risk estimate: 6.60x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0032; snapshot -0.0011

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bull Call Debit Spread

- Signal: LONG idea with base score -0.22% and final score 0.19%
- Underlying spot: $222.82
- Expiry: 2026-06-18
- Long leg: `NVDA260618C00223000` at strike $223.00 using recent close $9.10
- Short leg: `NVDA260618C00235000` at strike $235.00 using recent close $4.40
- Estimated net debit: $4.70
- Max loss: $4.70
- Max profit: $7.30
- Breakeven at expiry: $227.70
- Reward/risk estimate: 1.55x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0027; screener +0.0013

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score -0.05% and final score 0.15%
- Underlying spot: $377.92
- Expiry: 2026-06-18
- Long leg: `UNH260618C00377500` at strike $377.50 using recent close $10.51
- Short leg: `UNH260618C00397500` at strike $397.50 using recent close $3.40
- Estimated net debit: $7.11
- Max loss: $7.11
- Max profit: $12.89
- Breakeven at expiry: $384.61
- Reward/risk estimate: 1.81x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0018

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
