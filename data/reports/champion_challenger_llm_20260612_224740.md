# LLM Bot Champion / Challenger

Generated at 2026-06-12T22:47:40.506979+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: LLM minimum conviction = 0.8000

## Models being tested
- Champion: the current LLM network, including Stock Selector, Analyst, Trader, Skeptic review, conviction gate, and normal execution/risk controls.
- Challenger: a stricter shadow version of the LLM policy that counts only selected decisions with absolute conviction/final score at or above 0.8000.

## Verdict
Too early to promote the challenger because it has fewer than 10 evaluated samples.
The dashboard should treat this as directional evidence, not proof.

## Champion metrics
{
  "avg_beat_spy": -0.0001918699879700585,
  "avg_signed_return": -0.0003696792642083171,
  "hit_rate": 0.4444444444444444,
  "samples": 108.0
}

## Challenger metrics
{
  "avg_beat_spy": 0.0,
  "avg_signed_return": 0.0,
  "hit_rate": 0.0,
  "samples": 0.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": -0.0001918699879700585,
  "avg_signed_return": -0.0003696792642083171,
  "hit_rate": 0.4444444444444444,
  "samples": 108.0
}

## Changes implemented
- LLM conviction gate is active at 0.8000.
- LLM Skeptic review can caution, reduce conviction, or veto weakly supported trades before execution.
- Champion/challenger can promote bounded threshold changes only after enough evaluated evidence supports the challenger.
- Champion/challenger adjustment status: Champion/challenger evidence did not justify a threshold change.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- Threshold changes are bounded and written to the champion/challenger policy file only when enough evaluated evidence exists.