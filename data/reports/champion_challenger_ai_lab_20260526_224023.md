# AI Lab Bot Champion / Challenger

Generated at 2026-05-26T22:40:23.812602+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute AI Lab composite score = 0.0059

## Models being tested
- Champion: the current AI Lab adaptive sleeve ensemble using trend, reversal, breakout, volume-confirmation, low-volatility, and market-alignment sleeves plus its self-updated policy file.
- Challenger: a stricter shadow version of the AI Lab policy that counts only selected decisions whose absolute composite score is at or above 0.0059.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": -0.0020610092783330484,
  "avg_signed_return": 0.00016729601612892862,
  "hit_rate": 0.41228070175438597,
  "samples": 114.0
}

## Challenger metrics
{
  "avg_beat_spy": -0.002698687684713573,
  "avg_signed_return": -0.0007270257856690488,
  "hit_rate": 0.39,
  "samples": 100.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": 0.0024938364815278447,
  "avg_signed_return": 0.006555308886114481,
  "hit_rate": 0.5714285714285714,
  "samples": 14.0
}

## Changes implemented
- AI Lab composite gate is active at 0.0059.
- AI Lab self-updates sleeve weights from mature decision outcomes in its own policy file.
- Champion/challenger can promote bounded threshold changes only after enough evaluated evidence supports the challenger.
- Champion/challenger policy updated ai_lab_min_abs_score from 0.0059 to 0.0050.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- Threshold changes are bounded and written to the champion/challenger policy file only when enough evaluated evidence exists.