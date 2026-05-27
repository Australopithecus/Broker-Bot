# AI Lab Bot Champion / Challenger

Generated at 2026-05-27T22:51:59.160230+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute AI Lab composite score = 0.0050

## Models being tested
- Champion: the current AI Lab adaptive sleeve ensemble using trend, reversal, breakout, volume-confirmation, low-volatility, and market-alignment sleeves plus its self-updated policy file.
- Challenger: a stricter shadow version of the AI Lab policy that counts only selected decisions whose absolute composite score is at or above 0.0050.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": -0.0017466579485018571,
  "avg_signed_return": 0.00020995918455526318,
  "hit_rate": 0.45,
  "samples": 140.0
}

## Challenger metrics
{
  "avg_beat_spy": -0.0021565158094100883,
  "avg_signed_return": -0.00029178743863704347,
  "hit_rate": 0.42857142857142855,
  "samples": 133.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": 0.006040641408754536,
  "avg_signed_return": 0.00974314502520909,
  "hit_rate": 0.8571428571428571,
  "samples": 7.0
}

## Changes implemented
- AI Lab composite gate is active at 0.0050.
- AI Lab self-updates sleeve weights from mature decision outcomes in its own policy file.
- Champion/challenger can promote bounded threshold changes only after enough evaluated evidence supports the challenger.
- Champion/challenger adjustment status: Champion/challenger evidence did not justify a threshold change.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- Threshold changes are bounded and written to the champion/challenger policy file only when enough evaluated evidence exists.