# ML Bot Champion / Challenger

Generated at 2026-05-29T22:43:01.645164+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute signal score = 0.0023

## Models being tested
- Champion: the current ML ensemble policy using the trained return model, research overlays, symbol memory, confidence gate, and normal execution/risk controls.
- Challenger: a stricter shadow version of the ML policy that counts only selected decisions with absolute final score at or above 0.0023.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": -0.0009166919040039277,
  "avg_signed_return": 0.0008703470840276117,
  "hit_rate": 0.5,
  "samples": 140.0
}

## Challenger metrics
{
  "avg_beat_spy": -0.00018043953527328605,
  "avg_signed_return": 0.0017281992578375598,
  "hit_rate": 0.5210084033613446,
  "samples": 119.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": -0.00508878866014423,
  "avg_signed_return": -0.0039908152342287605,
  "hit_rate": 0.38095238095238093,
  "samples": 21.0
}

## Changes implemented
- ML confidence gate is active at 0.0023; weaker selected signals are converted to HOLD before sizing.
- Post-trade attribution now tracks which signal components are associated with wins or losses.
- Champion/challenger can promote bounded threshold changes only after enough evaluated evidence supports the challenger.
- Champion/challenger adjustment status: Champion/challenger evidence did not justify a threshold change.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- Threshold changes are bounded and written to the champion/challenger policy file only when enough evaluated evidence exists.