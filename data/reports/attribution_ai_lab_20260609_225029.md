# AI Lab Bot Post-Trade Attribution

Generated at 2026-06-09T22:50:29.521544+00:00

This report asks a simple question: which ingredients in the bot's decisions have actually been associated with profitable outcomes so far?

## Overall outcome attribution
- Evaluated decisions: 145
- Hit rate: 49.7%
- Average signed return: -0.06%
- Average alpha versus SPY: -0.18%

## Side breakdown
{
  "LONG": {
    "avg_beat_spy": -0.0003814247506871721,
    "avg_signed_return": 0.0009037931359899497,
    "hit_rate": 0.4939759036144578,
    "samples": 83.0
  },
  "SHORT": {
    "avg_beat_spy": -0.003666850361095137,
    "avg_signed_return": -0.0025137276195986106,
    "hit_rate": 0.5,
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
- MSFT LONG evaluated 2026-05-28T22:46:10.686386+00:00: signed=3.46%, raw=3.46%
- XOM SHORT evaluated 2026-05-26T22:40:13.501782+00:00: signed=3.27%, raw=-3.27%

## Worst recent decisions
- NVDA LONG evaluated 2026-06-08T22:50:13.840776+00:00: signed=-6.16%, raw=-6.16%
- META SHORT evaluated 2026-06-03T23:14:56.559120+00:00: signed=-4.24%, raw=4.24%
- MSFT LONG evaluated 2026-06-02T23:09:16.139917+00:00: signed=-4.15%, raw=-4.15%
- PG SHORT evaluated 2026-06-08T22:50:13.840776+00:00: signed=-4.06%, raw=4.06%
- GOOGL LONG evaluated 2026-06-02T23:09:16.139917+00:00: signed=-3.83%, raw=-3.83%