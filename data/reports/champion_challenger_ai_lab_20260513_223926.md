# AI Lab Bot Champion / Challenger

Generated at 2026-05-13T22:39:26.021384+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute AI Lab composite score = 0.0060

## Models being tested
- Champion: the current AI Lab adaptive sleeve ensemble using trend, reversal, breakout, volume-confirmation, low-volatility, and market-alignment sleeves plus its self-updated policy file.
- Challenger: a stricter shadow version of the AI Lab policy that counts only selected decisions whose absolute composite score is at or above 0.0060.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": 0.0020133358633251104,
  "avg_signed_return": 0.0031941827878005607,
  "hit_rate": 0.46938775510204084,
  "samples": 49.0
}

## Challenger metrics
{
  "avg_beat_spy": 0.001674966750066261,
  "avg_signed_return": 0.002727466946225328,
  "hit_rate": 0.4418604651162791,
  "samples": 43.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": 0.004438314508346863,
  "avg_signed_return": 0.00653897965242306,
  "hit_rate": 0.6666666666666666,
  "samples": 6.0
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