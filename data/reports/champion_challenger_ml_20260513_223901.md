# ML Bot Champion / Challenger

Generated at 2026-05-13T22:39:01.491042+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute signal score = 0.0018

## Models being tested
- Champion: the current ML ensemble policy using the trained return model, research overlays, symbol memory, confidence gate, and normal execution/risk controls.
- Challenger: a stricter shadow version of the ML policy that counts only selected decisions with absolute final score at or above 0.0018.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": -0.0011310744546462498,
  "avg_signed_return": 0.001830164131484937,
  "hit_rate": 0.5586206896551724,
  "samples": 145.0
}

## Challenger metrics
{
  "avg_beat_spy": -0.0008963090519033962,
  "avg_signed_return": 0.0021478864455733077,
  "hit_rate": 0.5661764705882353,
  "samples": 136.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": -0.004678640540538261,
  "avg_signed_return": -0.0029709730591837755,
  "hit_rate": 0.4444444444444444,
  "samples": 9.0
}

## Changes implemented
- ML confidence gate is active at 0.0018; weaker selected signals are converted to HOLD before sizing.
- Post-trade attribution now tracks which signal components are associated with wins or losses.
- Champion/challenger can promote bounded threshold changes only after enough evaluated evidence supports the challenger.
- Champion/challenger adjustment status: Champion/challenger evidence did not justify a threshold change.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- Threshold changes are bounded and written to the champion/challenger policy file only when enough evaluated evidence exists.