# ML Bot Champion / Challenger

Generated at 2026-05-01T12:55:41.401323+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current confidence threshold.

Threshold used: minimum absolute signal score = 0.0015

## Models being tested
- Champion: the current ML ensemble policy using the trained return model, research overlays, symbol memory, confidence gate, and normal execution/risk controls.
- Challenger: a stricter shadow version of the ML policy that counts only selected decisions with absolute final score at or above 0.0015.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": 0.0020055546862070782,
  "avg_signed_return": 0.0025144199767116577,
  "hit_rate": 0.5116279069767442,
  "samples": 86.0
}

## Challenger metrics
{
  "avg_beat_spy": 0.0009310238152428088,
  "avg_signed_return": 0.00181535057857911,
  "hit_rate": 0.4675324675324675,
  "samples": 77.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": 0.011198763248901381,
  "avg_signed_return": 0.008495347049623451,
  "hit_rate": 0.8888888888888888,
  "samples": 9.0
}

## Changes implemented
- ML confidence gate is active at 0.0015; weaker selected signals are converted to HOLD before sizing.
- Post-trade attribution now tracks which signal components are associated with wins or losses.
- Champion/challenger remains a shadow evaluation; it does not automatically promote a new policy.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- This is shadow evaluation only; it reports what would have happened without automatically changing the strategy.