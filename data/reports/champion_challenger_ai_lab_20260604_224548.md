# AI Lab Bot Champion / Challenger

Generated at 2026-06-04T22:45:48.945980+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute AI Lab composite score = 0.0049

## Models being tested
- Champion: the current AI Lab adaptive sleeve ensemble using trend, reversal, breakout, volume-confirmation, low-volatility, and market-alignment sleeves plus its self-updated policy file.
- Challenger: a stricter shadow version of the AI Lab policy that counts only selected decisions whose absolute composite score is at or above 0.0049.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": -0.0028928061016791373,
  "avg_signed_return": -0.0008729809635527555,
  "hit_rate": 0.46715328467153283,
  "samples": 137.0
}

## Challenger metrics
{
  "avg_beat_spy": -0.0032457758330867127,
  "avg_signed_return": -0.001235722907635687,
  "hit_rate": 0.4375,
  "samples": 128.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": 0.002127207856117493,
  "avg_signed_return": 0.004286015574515602,
  "hit_rate": 0.8888888888888888,
  "samples": 9.0
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