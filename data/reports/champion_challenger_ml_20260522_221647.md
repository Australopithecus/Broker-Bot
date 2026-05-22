# ML Bot Champion / Challenger

Generated at 2026-05-22T22:16:47.625303+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute signal score = 0.0020

## Models being tested
- Champion: the current ML ensemble policy using the trained return model, research overlays, symbol memory, confidence gate, and normal execution/risk controls.
- Challenger: a stricter shadow version of the ML policy that counts only selected decisions with absolute final score at or above 0.0020.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": -0.0016747573763452332,
  "avg_signed_return": -0.000724809956517656,
  "hit_rate": 0.45185185185185184,
  "samples": 135.0
}

## Challenger metrics
{
  "avg_beat_spy": -0.0017320136995600188,
  "avg_signed_return": -0.0006005450899533313,
  "hit_rate": 0.45081967213114754,
  "samples": 122.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": -0.001137428804637246,
  "avg_signed_return": -0.0018909879350443943,
  "hit_rate": 0.46153846153846156,
  "samples": 13.0
}

## Changes implemented
- ML confidence gate is active at 0.0020; weaker selected signals are converted to HOLD before sizing.
- Post-trade attribution now tracks which signal components are associated with wins or losses.
- Champion/challenger can promote bounded threshold changes only after enough evaluated evidence supports the challenger.
- Champion/challenger adjustment status: Champion/challenger evidence did not justify a threshold change.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- Threshold changes are bounded and written to the champion/challenger policy file only when enough evaluated evidence exists.