# AI Lab Bot Champion / Challenger

Generated at 2026-05-12T22:36:06.581806+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute AI Lab composite score = 0.0060

## Models being tested
- Champion: the current AI Lab adaptive sleeve ensemble using trend, reversal, breakout, volume-confirmation, low-volatility, and market-alignment sleeves plus its self-updated policy file.
- Challenger: a stricter shadow version of the AI Lab policy that counts only selected decisions whose absolute composite score is at or above 0.0060.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": 0.00038220540595840057,
  "avg_signed_return": -0.000984136585383601,
  "hit_rate": 0.2903225806451613,
  "samples": 31.0
}

## Challenger metrics
{
  "avg_beat_spy": 0.00032801804153589513,
  "avg_signed_return": -0.0010383239498061064,
  "hit_rate": 0.2857142857142857,
  "samples": 28.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": 0.0008879541405684513,
  "avg_signed_return": -0.00047838785077355023,
  "hit_rate": 0.3333333333333333,
  "samples": 3.0
}

## Changes implemented
- AI Lab composite gate is active at 0.0060.
- AI Lab self-updates sleeve weights from mature decision outcomes in its own policy file.
- Champion/challenger can promote bounded threshold changes only after enough evaluated evidence supports the challenger.
- Champion/challenger adjustment status: Champion/challenger evidence did not justify a threshold change.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- Threshold changes are bounded and written to the champion/challenger policy file only when enough evaluated evidence exists.