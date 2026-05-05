# LLM Bot Champion / Challenger

Generated at 2026-05-05T14:00:16.180851+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: LLM minimum conviction = 0.5500

## Models being tested
- Champion: the current LLM network, including Stock Selector, Analyst, Trader, Skeptic review, conviction gate, and normal execution/risk controls.
- Challenger: a stricter shadow version of the LLM policy that counts only selected decisions with absolute conviction/final score at or above 0.5500.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": 0.0008915143531554893,
  "avg_signed_return": 0.000630257687905437,
  "hit_rate": 0.46938775510204084,
  "samples": 98.0
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
  "avg_beat_spy": 0.0003718072391247033,
  "avg_signed_return": 0.00018658863538267845,
  "hit_rate": 0.3333333333333333,
  "samples": 3.0
}

## Changes implemented
- LLM conviction gate is active at 0.5500.
- LLM Skeptic review can caution, reduce conviction, or veto weakly supported trades before execution.
- Champion/challenger can promote bounded threshold changes only after enough evaluated evidence supports the challenger.
- Champion/challenger adjustment status: Champion/challenger evidence did not justify a threshold change.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- Threshold changes are bounded and written to the champion/challenger policy file only when enough evaluated evidence exists.