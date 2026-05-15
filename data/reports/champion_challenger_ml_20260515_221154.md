# ML Bot Champion / Challenger

Generated at 2026-05-15T22:11:54.851886+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute signal score = 0.0020

## Models being tested
- Champion: the current ML ensemble policy using the trained return model, research overlays, symbol memory, confidence gate, and normal execution/risk controls.
- Challenger: a stricter shadow version of the ML policy that counts only selected decisions with absolute final score at or above 0.0020.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": -0.0011919866116648669,
  "avg_signed_return": 0.0016478904510879267,
  "hit_rate": 0.5328467153284672,
  "samples": 137.0
}

## Challenger metrics
{
  "avg_beat_spy": -0.0008286035630195258,
  "avg_signed_return": 0.002218530179732392,
  "hit_rate": 0.5447154471544715,
  "samples": 123.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": -0.00438456625333465,
  "avg_signed_return": -0.003365587164859875,
  "hit_rate": 0.42857142857142855,
  "samples": 14.0
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