# ML Bot Champion / Challenger

Generated at 2026-04-30T17:51:15.962454+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current confidence threshold.

Threshold used: minimum absolute signal score = 0.0015

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": 0.003999695713845941,
  "avg_signed_return": 0.003577760453625759,
  "hit_rate": 0.5256410256410257,
  "samples": 78.0
}

## Challenger metrics
{
  "avg_beat_spy": 0.003060686904925666,
  "avg_signed_return": 0.0029363361150173645,
  "hit_rate": 0.4782608695652174,
  "samples": 69.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": 0.011198763248901381,
  "avg_signed_return": 0.008495347049623451,
  "hit_rate": 0.8888888888888888,
  "samples": 9.0
}

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- This is shadow evaluation only; it reports what would have happened without automatically changing the strategy.