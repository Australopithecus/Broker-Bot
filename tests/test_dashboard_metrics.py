from __future__ import annotations

import unittest

import pandas as pd

from broker_bot.dashboard_metrics import bot_performance_metrics, equity_frame, selected_window_return


class DashboardMetricWindowTests(unittest.TestCase):
    def test_window_return_requires_recent_window_coverage(self) -> None:
        anchor = pd.Timestamp("2026-08-13T21:00:00Z")
        frame = equity_frame(
            [
                {"ts": "2026-02-01T21:00:00Z", "equity": 100.0, "spy_value": 500.0},
                {"ts": "2026-08-13T21:00:00Z", "equity": 110.0, "spy_value": 550.0},
            ]
        )

        bot_ret, spy_ret = selected_window_return(frame, pd.Timedelta(days=7), anchor)

        self.assertIsNone(bot_ret)
        self.assertIsNone(spy_ret)

    def test_window_return_uses_nearby_baseline_before_cutoff(self) -> None:
        anchor = pd.Timestamp("2026-08-13T21:00:00Z")
        frame = equity_frame(
            [
                {"ts": "2026-08-06T12:00:00Z", "equity": 100.0, "spy_value": 500.0},
                {"ts": "2026-08-10T21:00:00Z", "equity": 105.0, "spy_value": 510.0},
                {"ts": "2026-08-13T21:00:00Z", "equity": 110.0, "spy_value": 550.0},
            ]
        )

        bot_ret, spy_ret = selected_window_return(frame, pd.Timedelta(days=7), anchor)

        self.assertAlmostEqual(bot_ret or 0.0, 0.10)
        self.assertAlmostEqual(spy_ret or 0.0, 0.10)

    def test_bot_metrics_report_none_for_sparse_window(self) -> None:
        metrics = bot_performance_metrics(
            {
                "equity": [
                    {"ts": "2026-02-01T21:00:00Z", "equity": 100.0, "spy_value": 500.0},
                    {"ts": "2026-08-13T21:00:00Z", "equity": 110.0, "spy_value": 550.0},
                ]
            },
            pd.Timedelta(days=7),
            pd.Timestamp("2026-08-13T21:00:00Z"),
        )

        self.assertIsNone(metrics["window_return"])
        self.assertIsNone(metrics["spy_window_return"])
        self.assertIsNone(metrics["window_alpha"])


if __name__ == "__main__":
    unittest.main()
