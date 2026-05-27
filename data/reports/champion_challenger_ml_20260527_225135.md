# ML Bot Champion / Challenger

Generated at 2026-05-27T22:51:35.270687+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute signal score = 0.0023

## Models being tested
- Champion: the current ML ensemble policy using the trained return model, research overlays, symbol memory, confidence gate, and normal execution/risk controls.
- Challenger: a stricter shadow version of the ML policy that counts only selected decisions with absolute final score at or above 0.0023.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": -0.0011149234943646355,
  "avg_signed_return": 0.0003221101890366818,
  "hit_rate": 0.4897959183673469,
  "samples": 147.0
}

## Challenger metrics
{
  "avg_beat_spy": -0.0002844983820251807,
  "avg_signed_return": 0.0012183972194168226,
  "hit_rate": 0.5080645161290323,
  "samples": 124.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": -0.005591998013064305,
  "avg_signed_return": -0.004510045974751903,
  "hit_rate": 0.391304347826087,
  "samples": 23.0
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