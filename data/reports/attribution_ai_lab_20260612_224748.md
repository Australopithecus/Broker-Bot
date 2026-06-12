# AI Lab Bot Post-Trade Attribution

Generated at 2026-06-12T22:47:48.200669+00:00

This report asks a simple question: which ingredients in the bot's decisions have actually been associated with profitable outcomes so far?

## Overall outcome attribution
- Evaluated decisions: 132
- Hit rate: 53.0%
- Average signed return: -0.01%
- Average alpha versus SPY: -0.05%

## Side breakdown
{
  "LONG": {
    "avg_beat_spy": -0.00015577818587898733,
    "avg_signed_return": 0.0001432830287863621,
    "hit_rate": 0.47368421052631576,
    "samples": 76.0
  },
  "SHORT": {
    "avg_beat_spy": -0.0009331638347048457,
    "avg_signed_return": -0.00043746998342766456,
    "hit_rate": 0.6071428571428571,
    "samples": 56.0
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
- MSFT LONG evaluated 2026-05-28T22:46:10.686386+00:00: signed=3.46%, raw=3.46%
- XOM SHORT evaluated 2026-05-26T22:40:13.501782+00:00: signed=3.27%, raw=-3.27%

## Worst recent decisions
- NVDA LONG evaluated 2026-06-08T22:50:13.840776+00:00: signed=-6.16%, raw=-6.16%
- META SHORT evaluated 2026-06-03T23:14:56.559120+00:00: signed=-4.24%, raw=4.24%
- MSFT LONG evaluated 2026-06-02T23:09:16.139917+00:00: signed=-4.15%, raw=-4.15%
- PG SHORT evaluated 2026-06-08T22:50:13.840776+00:00: signed=-4.06%, raw=4.06%
- GOOGL LONG evaluated 2026-06-02T23:09:16.139917+00:00: signed=-3.83%, raw=-3.83%