# Options Scaffold Report

Generated at: 2026-04-30T13:52:17.848637+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.56% and final score 1.11%
- Underlying spot: $370.40
- Expiry: 2026-05-15
- Long leg: `GOOGL260515C00370000` at strike $370.00 using recent close $5.40
- Short leg: `GOOGL260515C00390000` at strike $390.00 using recent close $2.01
- Estimated net debit: $3.39
- Max loss: $3.39
- Max profit: $16.61
- Breakeven at expiry: $373.39
- Reward/risk estimate: 4.90x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0036; snapshot +0.0018

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.27% and final score -0.78%
- Underlying spot: $607.15
- Expiry: 2026-05-15
- Long leg: `META260515P00605000` at strike $605.00 using recent close $7.03
- Short leg: `META260515P00575000` at strike $575.00 using recent close $3.15
- Estimated net debit: $3.88
- Max loss: $3.88
- Max profit: $26.12
- Breakeven at expiry: $601.12
- Reward/risk estimate: 6.73x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech -0.0029; snapshot -0.0022

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.30% and final score 0.73%
- Underlying spot: $365.99
- Expiry: 2026-05-15
- Long leg: `UNH260515C00365000` at strike $365.00 using recent close $12.10
- Short leg: `UNH260515C00380000` at strike $380.00 using recent close $4.88
- Estimated net debit: $7.22
- Max loss: $7.22
- Max profit: $7.78
- Breakeven at expiry: $372.22
- Reward/risk estimate: 1.08x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0035; memory +0.0010

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AAPL — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.14% and final score -0.17%
- Underlying spot: $269.79
- Expiry: 2026-05-15
- Long leg: `AAPL260515P00270000` at strike $270.00 using recent close $7.05
- Short leg: `AAPL260515P00257500` at strike $257.50 using recent close $2.69
- Estimated net debit: $4.36
- Max loss: $4.36
- Max profit: $8.14
- Breakeven at expiry: $265.64
- Reward/risk estimate: 1.87x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: No additional rationale captured.

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bear Put Debit Spread

- Signal: SHORT idea with base score -0.29% and final score -0.15%
- Underlying spot: $205.36
- Expiry: 2026-05-15
- Long leg: `NVDA260515P00205000` at strike $205.00 using recent close $4.85
- Short leg: `NVDA260515P00195000` at strike $195.00 using recent close $2.05
- Estimated net debit: $2.80
- Max loss: $2.80
- Max profit: $7.20
- Breakeven at expiry: $202.20
- Reward/risk estimate: 2.57x
- Thesis: Uses a bearish stock signal with defined risk instead of naked short gamma exposure.
- Bot rationale: tech +0.0016

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
