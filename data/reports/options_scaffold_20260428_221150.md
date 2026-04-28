# Options Scaffold Report

Generated at: 2026-04-28T22:11:50.867124+00:00

This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.
These are candidate structures for review, not unattended auto-execution.

## UNH — Bull Call Debit Spread

- Signal: LONG idea with base score 0.31% and final score 0.84%
- Underlying spot: $366.74
- Expiry: 2026-05-15
- Long leg: `UNH260515C00365000` at strike $365.00 using recent close $5.35
- Short leg: `UNH260515C00380000` at strike $380.00 using recent close $1.75
- Estimated net debit: $3.60
- Max loss: $3.60
- Max profit: $11.40
- Breakeven at expiry: $368.60
- Reward/risk estimate: 3.17x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0033; snapshot +0.0010; memory +0.0010

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## AMZN — Bull Call Debit Spread

- Signal: LONG idea with base score 0.48% and final score 0.75%
- Underlying spot: $259.71
- Expiry: 2026-05-15
- Long leg: `AMZN260515C00260000` at strike $260.00 using recent close $11.85
- Short leg: `AMZN260515C00272500` at strike $272.50 using recent close $6.72
- Estimated net debit: $5.13
- Max loss: $5.13
- Max profit: $7.37
- Breakeven at expiry: $265.13
- Reward/risk estimate: 1.44x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0028

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## MSFT — Bull Call Debit Spread

- Signal: LONG idea with base score 0.66% and final score 0.71%
- Underlying spot: $429.40
- Expiry: 2026-05-15
- Long leg: `MSFT260515C00430000` at strike $430.00 using recent close $15.65
- Short leg: `MSFT260515C00450000` at strike $450.00 using recent close $8.55
- Estimated net debit: $7.10
- Max loss: $7.10
- Max profit: $12.90
- Breakeven at expiry: $437.10
- Reward/risk estimate: 1.82x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech -0.0006; snapshot +0.0004; memory +0.0007

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## NVDA — Bull Call Debit Spread

- Signal: LONG idea with base score 0.39% and final score 0.66%
- Underlying spot: $213.15
- Expiry: 2026-05-15
- Long leg: `NVDA260515C00212500` at strike $212.50 using recent close $10.27
- Short leg: `NVDA260515C00222500` at strike $222.50 using recent close $5.44
- Estimated net debit: $4.83
- Max loss: $4.83
- Max profit: $5.17
- Breakeven at expiry: $217.33
- Reward/risk estimate: 1.07x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0027; snapshot -0.0004

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## META — Bull Call Debit Spread

- Signal: LONG idea with base score 0.49% and final score 0.39%
- Underlying spot: $671.30
- Expiry: 2026-05-15
- Long leg: `META260515C00672500` at strike $672.50 using recent close $33.50
- Short leg: `META260515C00705000` at strike $705.00 using recent close $20.10
- Estimated net debit: $13.40
- Max loss: $13.40
- Max profit: $19.10
- Breakeven at expiry: $685.90
- Reward/risk estimate: 1.43x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech -0.0006

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.

## GOOGL — Bull Call Debit Spread

- Signal: LONG idea with base score 0.08% and final score 0.31%
- Underlying spot: $349.76
- Expiry: 2026-05-15
- Long leg: `GOOGL260515C00350000` at strike $350.00 using recent close $13.25
- Short leg: `GOOGL260515C00365000` at strike $365.00 using recent close $7.29
- Estimated net debit: $5.96
- Max loss: $5.96
- Max profit: $9.04
- Breakeven at expiry: $355.96
- Reward/risk estimate: 1.52x
- Thesis: Uses a bullish stock signal with capped downside and capped upside.
- Bot rationale: tech +0.0020

Risk notes:
- This estimate uses Alpaca contract close prices, not live bid/ask spreads.
- Actual fill quality can be materially worse around wide spreads or low liquidity.
- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.
- Defined risk does not mean low risk; time decay and volatility compression still matter.
