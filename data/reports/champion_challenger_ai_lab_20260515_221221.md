# AI Lab Bot Champion / Challenger

Generated at 2026-05-15T22:12:21.410930+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute AI Lab composite score = 0.0060

## Models being tested
- Champion: the current AI Lab adaptive sleeve ensemble using trend, reversal, breakout, volume-confirmation, low-volatility, and market-alignment sleeves plus its self-updated policy file.
- Challenger: a stricter shadow version of the AI Lab policy that counts only selected decisions whose absolute composite score is at or above 0.0060.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": 2.8384529493348982e-05,
  "avg_signed_return": 0.0021401374957331436,
  "hit_rate": 0.42105263157894735,
  "samples": 57.0
}

## Challenger metrics
{
  "avg_beat_spy": -0.0002687131308590751,
  "avg_signed_return": 0.001730334383924219,
  "hit_rate": 0.4,
  "samples": 50.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": 0.0021505106748678066,
  "avg_signed_return": 0.0050673025800826044,
  "hit_rate": 0.5714285714285714,
  "samples": 7.0
}

## Changes implemented
- AI Lab composite gate is active at 0.0060.
- AI Lab self-updates sleeve weights from mature decision outcomes in its own policy file.
- Champion/challenger can promote bounded threshold changes only after enough evaluated evidence supports the challenger.
- Champion/challenger adjustment status: Champion/challenger evidence did not justify a threshold change.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- Threshold changes are bounded and written to the champion/challenger policy file only when enough evaluated evidence exists.