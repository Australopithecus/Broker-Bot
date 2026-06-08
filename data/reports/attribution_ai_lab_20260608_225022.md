# AI Lab Bot Post-Trade Attribution

Generated at 2026-06-08T22:50:22.362923+00:00

This report asks a simple question: which ingredients in the bot's decisions have actually been associated with profitable outcomes so far?

## Overall outcome attribution
- Evaluated decisions: 143
- Hit rate: 48.3%
- Average signed return: -0.06%
- Average alpha versus SPY: -0.23%

## Side breakdown
{
  "LONG": {
    "avg_beat_spy": -0.0006424705092130009,
    "avg_signed_return": 0.0010718096200147149,
    "hit_rate": 0.49382716049382713,
    "samples": 81.0
  },
  "SHORT": {
    "avg_beat_spy": -0.0045032768125933065,
    "avg_signed_return": -0.002713229896180092,
    "hit_rate": 0.46774193548387094,
    "samples": 62.0
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
- XOM SHORT evaluated 2026-05-20T22:44:39.041418+00:00: signed=3.88%, raw=-3.88%
- MSFT LONG evaluated 2026-05-28T22:46:10.686386+00:00: signed=3.46%, raw=3.46%

## Worst recent decisions
- NVDA LONG evaluated 2026-06-08T22:50:13.840776+00:00: signed=-6.16%, raw=-6.16%
- META SHORT evaluated 2026-06-03T23:14:56.559120+00:00: signed=-4.24%, raw=4.24%
- MSFT LONG evaluated 2026-06-02T23:09:16.139917+00:00: signed=-4.15%, raw=-4.15%
- PG SHORT evaluated 2026-06-08T22:50:13.840776+00:00: signed=-4.06%, raw=4.06%
- GOOGL LONG evaluated 2026-06-02T23:09:16.139917+00:00: signed=-3.83%, raw=-3.83%