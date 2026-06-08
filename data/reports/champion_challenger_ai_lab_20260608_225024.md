# AI Lab Bot Champion / Challenger

Generated at 2026-06-08T22:50:24.125798+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute AI Lab composite score = 0.0049

## Models being tested
- Champion: the current AI Lab adaptive sleeve ensemble using trend, reversal, breakout, volume-confirmation, low-volatility, and market-alignment sleeves plus its self-updated policy file.
- Challenger: a stricter shadow version of the AI Lab policy that counts only selected decisions whose absolute composite score is at or above 0.0049.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": -0.002316386528860406,
  "avg_signed_return": -0.0005692564639298869,
  "hit_rate": 0.4825174825174825,
  "samples": 143.0
}

## Challenger metrics
{
  "avg_beat_spy": -0.002251001315786268,
  "avg_signed_return": -0.0003284494518835474,
  "hit_rate": 0.4621212121212121,
  "samples": 132.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": -0.0031010090857500616,
  "avg_signed_return": -0.0034589406084859597,
  "hit_rate": 0.7272727272727273,
  "samples": 11.0
}

## Changes implemented
- AI Lab composite gate is active at 0.0049.
- AI Lab self-updates sleeve weights from mature decision outcomes in its own policy file.
- Champion/challenger can promote bounded threshold changes only after enough evaluated evidence supports the challenger.
- Champion/challenger adjustment status: Champion/challenger evidence did not justify a threshold change.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- Threshold changes are bounded and written to the champion/challenger policy file only when enough evaluated evidence exists.