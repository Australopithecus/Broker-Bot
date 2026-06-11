# ML Bot Champion / Challenger

Generated at 2026-06-11T14:48:15.777120+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute signal score = 0.0035

## Models being tested
- Champion: the current ML ensemble policy using the trained return model, research overlays, symbol memory, confidence gate, and normal execution/risk controls.
- Challenger: a stricter shadow version of the ML policy that counts only selected decisions with absolute final score at or above 0.0035.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": -0.0007253579521548886,
  "avg_signed_return": -0.0005699011493685611,
  "hit_rate": 0.4825174825174825,
  "samples": 143.0
}

## Challenger metrics
{
  "avg_beat_spy": 0.0003447424386933575,
  "avg_signed_return": -0.0003064269439465732,
  "hit_rate": 0.4948453608247423,
  "samples": 97.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": -0.00298187399372619,
  "avg_signed_return": -0.0011254880608018835,
  "hit_rate": 0.45652173913043476,
  "samples": 46.0
}

## Changes implemented
- ML confidence gate is active at 0.0035; weaker selected signals are converted to HOLD before sizing.
- Post-trade attribution now tracks which signal components are associated with wins or losses.
- Champion/challenger can promote bounded threshold changes only after enough evaluated evidence supports the challenger.
- Champion/challenger adjustment status: Champion/challenger evidence did not justify a threshold change.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- Threshold changes are bounded and written to the champion/challenger policy file only when enough evaluated evidence exists.