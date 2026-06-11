# AI Lab Bot Champion / Challenger

Generated at 2026-06-11T22:59:18.000066+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute AI Lab composite score = 0.0049

## Models being tested
- Champion: the current AI Lab adaptive sleeve ensemble using trend, reversal, breakout, volume-confirmation, low-volatility, and market-alignment sleeves plus its self-updated policy file.
- Challenger: a stricter shadow version of the AI Lab policy that counts only selected decisions whose absolute composite score is at or above 0.0049.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": -0.0009456346511840201,
  "avg_signed_return": -0.0003967966264037045,
  "hit_rate": 0.5107913669064749,
  "samples": 139.0
}

## Challenger metrics
{
  "avg_beat_spy": -0.0007837224097894478,
  "avg_signed_return": -2.1772384679630717e-05,
  "hit_rate": 0.496,
  "samples": 125.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": -0.0023912796636355593,
  "avg_signed_return": -0.0037452273560829347,
  "hit_rate": 0.6428571428571429,
  "samples": 14.0
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