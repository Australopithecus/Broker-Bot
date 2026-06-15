# ML Bot Champion / Challenger

Generated at 2026-06-15T23:09:26.759452+00:00

Champion is the bot's current selected-decision policy. Challenger is a stricter shadow policy that only counts trades passing the current threshold.

Threshold used: minimum absolute signal score = 0.0035

## Models being tested
- Champion: the current ML ensemble policy using the trained return model, research overlays, symbol memory, confidence gate, and normal execution/risk controls.
- Challenger: a stricter shadow version of the ML policy that counts only selected decisions with absolute final score at or above 0.0035.

## Verdict
The challenger has not yet shown enough improvement over the current champion.


## Champion metrics
{
  "avg_beat_spy": -0.001923099867943431,
  "avg_signed_return": -0.0007336920095180575,
  "hit_rate": 0.47586206896551725,
  "samples": 145.0
}

## Challenger metrics
{
  "avg_beat_spy": -0.001556289517227738,
  "avg_signed_return": -0.0007212627590645991,
  "hit_rate": 0.4752475247524752,
  "samples": 101.0
}

## Trades excluded by the challenger
{
  "avg_beat_spy": -0.0027650963548135443,
  "avg_signed_return": -0.0007622227889680417,
  "hit_rate": 0.4772727272727273,
  "samples": 44.0
}

## Changes implemented
- ML confidence gate is active at 0.0035; weaker selected signals are converted to HOLD before sizing.
- Post-trade attribution now tracks which signal components are associated with wins or losses.
- Champion/challenger can promote bounded threshold changes only after enough evaluated evidence supports the challenger.
- Champion/challenger adjustment status: Champion/challenger evidence did not justify a threshold change.

## Interpretation
- If challenger returns and hit rate beat the champion with enough samples, tightening the gate may improve future results.
- If excluded trades perform well, the gate may be too strict and should be relaxed.
- Threshold changes are bounded and written to the champion/challenger policy file only when enough evaluated evidence exists.