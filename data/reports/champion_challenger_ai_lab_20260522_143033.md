# AI Lab Bot Champion / Challenger

Generated at 2026-05-22T14:30:33.399502+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute AI Lab composite score = 0.0051

## Models being tested
- Champion: the current AI Lab adaptive sleeve ensemble using trend, reversal, breakout, volume-confirmation, low-volatility, and market-alignment sleeves plus its self-updated policy file.
- Challenger: a stricter shadow version of the AI Lab policy that counts only selected decisions whose absolute composite score is at or above 0.0051.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": -0.0012294732454630197,
  "avg_signed_return": 0.00025865553343798047,
  "hit_rate": 0.4230769230769231,
  "samples": 104.0
}

## Challenger metrics
{
  "avg_beat_spy": -0.0015752507594232522,
  "avg_signed_return": -0.00021517853418635523,
  "hit_rate": 0.4020618556701031,
  "samples": 97.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": 0.0035620151622716306,
  "avg_signed_return": 0.00682464189908949,
  "hit_rate": 0.7142857142857143,
  "samples": 7.0
}

## Changes implemented
- AI Lab composite gate is active at 0.0051.
- AI Lab self-updates sleeve weights from mature decision outcomes in its own policy file.
- Champion/challenger can promote bounded threshold changes only after enough evaluated evidence supports the challenger.
- Champion/challenger adjustment status: Champion/challenger evidence did not justify a threshold change.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- Threshold changes are bounded and written to the champion/challenger policy file only when enough evaluated evidence exists.