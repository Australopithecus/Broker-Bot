# AI Lab Bot Champion / Challenger

Generated at 2026-06-02T23:09:24.230941+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute AI Lab composite score = 0.0057

## Models being tested
- Champion: the current AI Lab adaptive sleeve ensemble using trend, reversal, breakout, volume-confirmation, low-volatility, and market-alignment sleeves plus its self-updated policy file.
- Challenger: a stricter shadow version of the AI Lab policy that counts only selected decisions whose absolute composite score is at or above 0.0057.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": -0.002470877183550845,
  "avg_signed_return": -0.0005777424127930502,
  "hit_rate": 0.45774647887323944,
  "samples": 142.0
}

## Challenger metrics
{
  "avg_beat_spy": -0.003067542350544736,
  "avg_signed_return": -0.0013169901656874404,
  "hit_rate": 0.4274193548387097,
  "samples": 124.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": 0.0016394828557404052,
  "avg_signed_return": 0.004514853218257194,
  "hit_rate": 0.6666666666666666,
  "samples": 18.0
}

## Changes implemented
- AI Lab composite gate is active at 0.0057.
- AI Lab self-updates sleeve weights from mature decision outcomes in its own policy file.
- Champion/challenger can promote bounded threshold changes only after enough evaluated evidence supports the challenger.
- Champion/challenger policy updated ai_lab_min_abs_score from 0.0057 to 0.0049.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- Threshold changes are bounded and written to the champion/challenger policy file only when enough evaluated evidence exists.