# LLM Bot Champion / Challenger

Generated at 2026-05-04T22:15:55.838557+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current confidence threshold.

Threshold used: LLM minimum conviction = 0.5500

## Models being tested
- Champion: the current LLM network, including Stock Selector, Analyst, Trader, Skeptic review, conviction gate, and normal execution/risk controls.
- Challenger: a stricter shadow version of the LLM policy that counts only selected decisions with absolute conviction/final score at or above 0.5500.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": 0.0008199996424966712,
  "avg_signed_return": 0.0004930962394192025,
  "hit_rate": 0.4639175257731959,
  "samples": 97.0
}

## Challenger metrics
{
  "avg_beat_spy": 0.0009079261567564614,
  "avg_signed_return": 0.0006442682895640504,
  "hit_rate": 0.47368421052631576,
  "samples": 95.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": -0.0033565097848433645,
  "avg_signed_return": -0.006687576142461071,
  "hit_rate": 0.0,
  "samples": 2.0
}

## Changes implemented
- LLM conviction gate is active at 0.5500.
- LLM Skeptic review can caution, reduce conviction, or veto weakly supported trades before execution.
- Champion/challenger remains a shadow evaluation; it does not automatically promote a new policy.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- This is shadow evaluation only; it reports what would have happened without automatically changing the strategy.