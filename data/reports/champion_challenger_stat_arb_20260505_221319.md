# Stat Arb Bot Champion / Challenger

Generated at 2026-05-05T22:13:19.822016+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute pair-spread z-score = 1.2500

## Models being tested
- Champion: the current statistical pairs strategy using liquidity filters, correlation gates, hedge-ratio spread z-scores, pair sizing, and normal execution/risk controls.
- Challenger: a stricter shadow version of the Stat Arb policy that counts only selected decisions whose absolute pair-spread z-score is at or above 1.2500.

## Verdict
Too early to promote the challenger because it has fewer than 10 evaluated samples.
The dashboard should treat this as directional evidence, not proof.

## Champion metrics
{
  "avg_beat_spy": 0.0,
  "avg_signed_return": 0.0,
  "hit_rate": 0.0,
  "samples": 0.0
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
  "avg_beat_spy": 0.0,
  "avg_signed_return": 0.0,
  "hit_rate": 0.0,
  "samples": 0.0
}

## Changes implemented
- Stat Arb entry gate is active at 1.2500 absolute z-score.
- Pair candidates must pass the minimum correlation gate of 0.72.
- Champion/challenger can promote bounded threshold changes only after enough evaluated evidence supports the challenger.
- Champion/challenger adjustment status: Not enough evaluated champion/challenger evidence to adjust this bot yet.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- Threshold changes are bounded and written to the champion/challenger policy file only when enough evaluated evidence exists.