# ML Bot Champion / Challenger

Generated at 2026-05-04T12:49:29.770341+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current confidence threshold.

Threshold used: minimum absolute signal score = 0.0015

## Models being tested
- Champion: the current ML ensemble policy using the trained return model, research overlays, symbol memory, confidence gate, and normal execution/risk controls.
- Challenger: a stricter shadow version of the ML policy that counts only selected decisions with absolute final score at or above 0.0015.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": 0.00018075654084340225,
  "avg_signed_return": 0.0008528903829886639,
  "hit_rate": 0.494949494949495,
  "samples": 99.0
}

## Challenger metrics
{
  "avg_beat_spy": -0.0003897880259080338,
  "avg_signed_return": 0.0006118145934822019,
  "hit_rate": 0.45977011494252873,
  "samples": 87.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": 0.0043172046497913135,
  "avg_signed_return": 0.0026006898569105132,
  "hit_rate": 0.75,
  "samples": 12.0
}

## Changes implemented
- ML confidence gate is active at 0.0015; weaker selected signals are converted to HOLD before sizing.
- Post-trade attribution now tracks which signal components are associated with wins or losses.
- Champion/challenger remains a shadow evaluation; it does not automatically promote a new policy.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- This is shadow evaluation only; it reports what would have happened without automatically changing the strategy.