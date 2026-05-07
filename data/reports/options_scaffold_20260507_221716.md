# Options Scaffold Report

Generated at: 2026-05-07T22:17:16.902492+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.82% and final score 1.35%
- Underlying spot: $397.89
- Expiry: 2026-05-22
- Long leg: `GOOGL260522C00397500` at strike $397.50 using recent close $11.68
- Short leg: `GOOGL260522C00417500` at strike $417.50 using recent close $3.55
- Estimated net debit: $8.13
- Max loss: $8.13
- Max profit: $11.87
- Breakeven at expiry: $405.63
- Reward/risk estimate: 1.46x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0045; memory +0.0008

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.59% and final score 0.94%
- Underlying spot: $369.65
- Expiry: 2026-05-22
- Long leg: `UNH260522C00370000` at strike $370.00 using recent close $6.85
- Short leg: `UNH260522C00387500` at strike $387.50 using recent close $2.30
- Estimated net debit: $4.55
- Max loss: $4.55
- Max profit: $12.95
- Breakeven at expiry: $374.55
- Reward/risk estimate: 2.85x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0030

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.26% and final score 0.64%
- Underlying spot: $271.08
- Expiry: 2026-05-22
- Long leg: `AMZN260522C00270000` at strike $270.00 using recent close $10.22
- Short leg: `AMZN260522C00282500` at strike $282.50 using recent close $3.85
- Estimated net debit: $6.37
- Max loss: $6.37
- Max profit: $6.13
- Breakeven at expiry: $276.37
- Reward/risk estimate: 0.96x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0035; memory +0.0004

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## MSFT — Bull Call Debit Spread

- Signal: LONG idea with base score 0.43% and final score 0.56%
- Underlying spot: $420.79
- Expiry: 2026-05-22
- Long leg: `MSFT260522C00420000` at strike $420.00 using recent close $6.86
- Short leg: `MSFT260522C00440000` at strike $440.00 using recent close $1.97
- Estimated net debit: $4.89
- Max loss: $4.89
- Max profit: $15.11
- Breakeven at expiry: $424.89
- Reward/risk estimate: 3.09x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0010

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## XOM — Bear Put Debit Spread

- Signal: SHORT idea with base score 0.11% and final score -0.37%
- Underlying spot: $146.51
- Expiry: 2026-05-22
- Long leg: `XOM260522P00147000` at strike $147.00 using recent close $3.50
- Short leg: `XOM260522P00140000` at strike $140.00 using recent close $1.05
- Estimated net debit: $2.45
- Max loss: $2.45
- Max profit: $4.55
- Breakeven at expiry: $144.55
- Reward/risk estimate: 1.86x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0045

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bull Call Debit Spread

- Signal: LONG idea with base score 0.12% and final score 0.32%
- Underlying spot: $211.56
- Expiry: 2026-05-22
- Long leg: `NVDA260522C00212500` at strike $212.50 using recent close $7.25
- Short leg: `NVDA260522C00222500` at strike $222.50 using recent close $4.03
- Estimated net debit: $3.22
- Max loss: $3.22
- Max profit: $6.78
- Breakeven at expiry: $215.72
- Reward/risk estimate: 2.11x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0023; memory -0.0011

Risk notes:
- This estimate uses brokerage-service contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
