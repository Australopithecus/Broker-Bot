# AI Lab Bot Champion / Challenger

Generated at 2026-05-18T12:40:24.588713+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute AI Lab composite score = 0.0060

## Models being tested
- Champion: the current AI Lab adaptive sleeve ensemble using trend, reversal, breakout, volume-confirmation, low-volatility, and market-alignment sleeves plus its self-updated policy file.
- Challenger: a stricter shadow version of the AI Lab policy that counts only selected decisions whose absolute composite score is at or above 0.0060.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": 0.0005843869129274985,
  "avg_signed_return": 0.0011493334537581792,
  "hit_rate": 0.421875,
  "samples": 64.0
}

## Challenger metrics
{
  "avg_beat_spy": 0.0003920559246190395,
  "avg_signed_return": 0.000668179350525355,
  "hit_rate": 0.40350877192982454,
  "samples": 57.0
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