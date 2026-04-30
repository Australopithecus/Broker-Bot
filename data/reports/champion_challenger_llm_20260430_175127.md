# LLM Bot Champion / Challenger

Generated at 2026-04-30T17:51:27.373239+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current confidence threshold.

Threshold used: LLM minimum conviction = 0.5500

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": 0.002545995257131429,
  "avg_signed_return": 0.0011754387098839056,
  "hit_rate": 0.4788732394366197,
  "samples": 71.0
}

## Challenger metrics
{
  "avg_beat_spy": 0.002545995257131429,
  "avg_signed_return": 0.0011754387098839056,
  "hit_rate": 0.4788732394366197,
  "samples": 71.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": 0.0,
  "avg_signed_return": 0.0,
  "hit_rate": 0.0,
  "samples": 0.0
}

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- This is shadow evaluation only; it reports what would have happened without automatically changing the strategy.