# AI Lab Bot Post-Trade Attribution

Generated at 2026-06-15T23:09:45.420120+00:00

This report asks a simple question: which ingredients in the bot's decisions have actually been associated with profitable outcomes so far?

## Overall outcome attribution
- Evaluated decisions: 144
- Hit rate: 50.7%
- Average signed return: -0.16%
- Average alpha versus SPY: -0.34%

## Side breakdown
{
  "LONG": {
    "avg_beat_spy": -0.0007397607717709836,
    "avg_signed_return": 0.00043703616776056967,
    "hit_rate": 0.4875,
    "samples": 80.0
  },
  "SHORT": {
    "avg_beat_spy": -0.006714799071712697,
    "avg_signed_return": -0.004107872297885017,
    "hit_rate": 0.53125,
    "samples": 64.0
  }
}

## Components most associated with better outcomes
- Not enough component data yet.

## Components most associated with worse outcomes
- Not enough component data yet.

## Best recent decisions
- MSFT LONG evaluated 2026-06-01T23:10:05.404109+00:00: signed=5.26%, raw=5.26%
- UNH LONG evaluated 2026-06-05T22:35:37.090282+00:00: signed=5.19%, raw=5.19%
- META SHORT evaluated 2026-06-01T23:10:05.404109+00:00: signed=5.06%, raw=-5.06%
- XOM SHORT evaluated 2026-06-15T23:09:38.607111+00:00: signed=4.19%, raw=-4.19%
- MSFT LONG evaluated 2026-05-28T22:46:10.686386+00:00: signed=3.46%, raw=3.46%

## Worst recent decisions
- NVDA LONG evaluated 2026-06-08T22:50:13.840776+00:00: signed=-6.16%, raw=-6.16%
- META SHORT evaluated 2026-06-15T23:09:38.607111+00:00: signed=-4.68%, raw=4.68%
- META SHORT evaluated 2026-06-15T23:09:38.607111+00:00: signed=-4.68%, raw=4.68%
- META SHORT evaluated 2026-06-03T23:14:56.559120+00:00: signed=-4.24%, raw=4.24%
- MSFT LONG evaluated 2026-06-02T23:09:16.139917+00:00: signed=-4.15%, raw=-4.15%