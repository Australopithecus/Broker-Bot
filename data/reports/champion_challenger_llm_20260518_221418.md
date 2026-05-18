# LLM Bot Champion / Challenger

Generated at 2026-05-18T22:14:18.068387+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: LLM minimum conviction = 0.6000

## Models being tested
- Champion: the current LLM network, including Stock Selector, Analyst, Trader, Skeptic review, conviction gate, and normal execution/risk controls.
- Challenger: a stricter shadow version of the LLM policy that counts only selected decisions with absolute conviction/final score at or above 0.6000.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": 0.0003172121244354613,
  "avg_signed_return": 5.5550366685785734e-05,
  "hit_rate": 0.4519230769230769,
  "samples": 104.0
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
  "avg_beat_spy": -0.005918102661175095,
  "avg_signed_return": -0.006158694374807008,
  "hit_rate": 0.2222222222222222,
  "samples": 9.0
}

## Changes implemented
- LLM conviction gate is active at 0.6000.
- LLM Skeptic review can caution, reduce conviction, or veto weakly supported trades before execution.
- Champion/challenger can promote bounded threshold changes only after enough evaluated evidence supports the challenger.
- Champion/challenger adjustment status: Champion/challenger evidence did not justify a threshold change.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- Threshold changes are bounded and written to the champion/challenger policy file only when enough evaluated evidence exists.