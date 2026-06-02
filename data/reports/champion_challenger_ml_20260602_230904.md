# ML Bot Champion / Challenger

Generated at 2026-06-02T23:09:04.692285+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute signal score = 0.0031

## Models being tested
- Champion: the current ML ensemble policy using the trained return model, research overlays, symbol memory, confidence gate, and normal execution/risk controls.
- Challenger: a stricter shadow version of the ML policy that counts only selected decisions with absolute final score at or above 0.0031.

## Verdict
The challenger is outperforming the current champion on recent evaluated decisions.


## Champion metrics
{
  "avg_beat_spy": -0.001733107999775195,
  "avg_signed_return": -0.00014387936348693586,
  "hit_rate": 0.4657534246575342,
  "samples": 146.0
}

## Challenger metrics
{
  "avg_beat_spy": -0.0003787761426174629,
  "avg_signed_return": 0.001398583850255597,
  "hit_rate": 0.5048543689320388,
  "samples": 103.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": -0.004977205239013484,
  "avg_signed_return": -0.0038386168289632353,
  "hit_rate": 0.37209302325581395,
  "samples": 43.0
}

## Changes implemented
- ML confidence gate is active at 0.0031; weaker selected signals are converted to HOLD before sizing.
- Post-trade attribution now tracks which signal components are associated with wins or losses.
- Champion/challenger can promote bounded threshold changes only after enough evaluated evidence supports the challenger.
- Champion/challenger policy updated min_signal_abs_score from 0.0031 to 0.0035.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- Threshold changes are bounded and written to the champion/challenger policy file only when enough evaluated evidence exists.