# AI Lab Bot Champion / Challenger

Generated at 2026-06-09T22:50:31.212833+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute AI Lab composite score = 0.0049

## Models being tested
- Champion: the current AI Lab adaptive sleeve ensemble using trend, reversal, breakout, volume-confirmation, low-volatility, and market-alignment sleeves plus its self-updated policy file.
- Challenger: a stricter shadow version of the AI Lab policy that counts only selected decisions whose absolute composite score is at or above 0.0049.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": -0.0017862274254823018,
  "avg_signed_return": -0.0005574916008824002,
  "hit_rate": 0.496551724137931,
  "samples": 145.0
}

## Challenger metrics
{
  "avg_beat_spy": -0.0017280671545535818,
  "avg_signed_return": -0.0003041175487927127,
  "hit_rate": 0.4772727272727273,
  "samples": 132.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": -0.002376777868758536,
  "avg_signed_return": -0.0031302127451776885,
  "hit_rate": 0.6923076923076923,
  "samples": 13.0
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