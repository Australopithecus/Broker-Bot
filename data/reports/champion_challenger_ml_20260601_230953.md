# ML Bot Champion / Challenger

Generated at 2026-06-01T23:09:53.574777+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute signal score = 0.0027

## Models being tested
- Champion: the current ML ensemble policy using the trained return model, research overlays, symbol memory, confidence gate, and normal execution/risk controls.
- Challenger: a stricter shadow version of the ML policy that counts only selected decisions with absolute final score at or above 0.0027.

## Verdict
The challenger is outperforming the current champion on recent evaluated decisions.


## Champion metrics
{
  "avg_beat_spy": -0.0017376302742351832,
  "avg_signed_return": 1.6632283088094503e-05,
  "hit_rate": 0.4726027397260274,
  "samples": 146.0
}

## Challenger metrics
{
  "avg_beat_spy": 0.00010174488818091755,
  "avg_signed_return": 0.0019445443126184087,
  "hit_rate": 0.5178571428571429,
  "samples": 112.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": -0.007796748456311751,
  "avg_signed_return": -0.0063341367553647054,
  "hit_rate": 0.3235294117647059,
  "samples": 34.0
}

## Changes implemented
- ML confidence gate is active at 0.0027; weaker selected signals are converted to HOLD before sizing.
- Post-trade attribution now tracks which signal components are associated with wins or losses.
- Champion/challenger can promote bounded threshold changes only after enough evaluated evidence supports the challenger.
- Champion/challenger policy updated min_signal_abs_score from 0.0027 to 0.0031.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- Threshold changes are bounded and written to the champion/challenger policy file only when enough evaluated evidence exists.