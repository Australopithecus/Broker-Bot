# LLM Bot Champion / Challenger

Generated at 2026-05-20T22:44:37.187381+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: LLM minimum conviction = 0.6000

## Models being tested
- Champion: the current LLM network, including Stock Selector, Analyst, Trader, Skeptic review, conviction gate, and normal execution/risk controls.
- Challenger: a stricter shadow version of the LLM policy that counts only selected decisions with absolute conviction/final score at or above 0.6000.

## Verdict
The challenger is outperforming the current champion on recent evaluated decisions.


## Champion metrics
{
  "avg_beat_spy": -0.0001918699879700585,
  "avg_signed_return": -0.0003696792642083171,
  "hit_rate": 0.4444444444444444,
  "samples": 108.0
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
  "avg_beat_spy": -0.008228841814817704,
  "avg_signed_return": -0.00777929600331408,
  "hit_rate": 0.23076923076923078,
  "samples": 13.0
}

## Changes implemented
- LLM conviction gate is active at 0.6000.
- LLM Skeptic review can caution, reduce conviction, or veto weakly supported trades before execution.
- Champion/challenger can promote bounded threshold changes only after enough evaluated evidence supports the challenger.
- Champion/challenger policy updated llm_min_conviction from 0.6000 to 0.6500.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- Threshold changes are bounded and written to the champion/challenger policy file only when enough evaluated evidence exists.