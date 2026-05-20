# AI Lab Bot Champion / Challenger

Generated at 2026-05-20T22:44:49.202336+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute AI Lab composite score = 0.0060

## Models being tested
- Champion: the current AI Lab adaptive sleeve ensemble using trend, reversal, breakout, volume-confirmation, low-volatility, and market-alignment sleeves plus its self-updated policy file.
- Challenger: a stricter shadow version of the AI Lab policy that counts only selected decisions whose absolute composite score is at or above 0.0060.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": -0.0012182136955018491,
  "avg_signed_return": 0.0002410188040153412,
  "hit_rate": 0.4329896907216495,
  "samples": 97.0
}

## Challenger metrics
{
  "avg_beat_spy": -0.0017027025872440695,
  "avg_signed_return": -0.0004923003301715788,
  "hit_rate": 0.4117647058823529,
  "samples": 85.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": 0.0022135826210055443,
  "avg_signed_return": 0.00543536267117269,
  "hit_rate": 0.5833333333333334,
  "samples": 12.0
}

## Changes implemented
- AI Lab composite gate is active at 0.0060.
- AI Lab self-updates sleeve weights from mature decision outcomes in its own policy file.
- Champion/challenger can promote bounded threshold changes only after enough evaluated evidence supports the challenger.
- Champion/challenger policy updated ai_lab_min_abs_score from 0.0060 to 0.0051.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- Threshold changes are bounded and written to the champion/challenger policy file only when enough evaluated evidence exists.