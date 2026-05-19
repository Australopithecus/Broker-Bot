# AI Lab Bot Champion / Challenger

Generated at 2026-05-19T22:39:12.203007+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute AI Lab composite score = 0.0060

## Models being tested
- Champion: the current AI Lab adaptive sleeve ensemble using trend, reversal, breakout, volume-confirmation, low-volatility, and market-alignment sleeves plus its self-updated policy file.
- Challenger: a stricter shadow version of the AI Lab policy that counts only selected decisions whose absolute composite score is at or above 0.0060.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": 0.00031285121246247297,
  "avg_signed_return": 3.871802432521537e-05,
  "hit_rate": 0.41975308641975306,
  "samples": 81.0
}

## Challenger metrics
{
  "avg_beat_spy": -7.41615372936479e-05,
  "avg_signed_return": -0.0004930915367564274,
  "hit_rate": 0.4027777777777778,
  "samples": 72.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": 0.00340895321051144,
  "avg_signed_return": 0.004293194512978358,
  "hit_rate": 0.5555555555555556,
  "samples": 9.0
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