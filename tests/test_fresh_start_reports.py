from __future__ import annotations

import unittest

from broker_bot.fresh_start_reports import fresh_start_strategy_reports


class FreshStartReportFilterTests(unittest.TestCase):
    def test_hides_pre_fresh_start_reports_and_keeps_latest_per_type(self) -> None:
        reports = [
            {
                "ts": "2026-08-13T21:22:08+00:00",
                "report_type": "model_eval",
                "headline": "ML Bot Model Evaluation",
                "summary": "Latest evaluation",
                "body": "without llm details",
                "metrics": {"oos_symbol_days": 100, "base_directional_accuracy": 0.51},
                "changes": {"component_scales": {"llm_adjustment": 1.0}},
            },
            {
                "ts": "2026-08-13T21:18:51+00:00",
                "report_type": "model_eval",
                "headline": "ML Bot Model Evaluation",
                "summary": "Older same-day duplicate",
                "body": "",
                "metrics": {},
                "changes": {},
            },
            {
                "ts": "2026-05-01T17:37:23+00:00",
                "report_type": "learning",
                "headline": "ML Bot Learning Update",
                "summary": "Old learning update",
                "body": "",
                "metrics": {},
                "changes": {},
            },
            {
                "ts": "2026-08-13T21:23:30+00:00",
                "report_type": "summary",
                "headline": "All-Model Summary Report",
                "summary": "Reviewed old model set",
                "body": "LLM Bot and AI Lab Bot notes",
                "metrics": {},
                "changes": {},
            },
        ]

        visible = fresh_start_strategy_reports(reports)

        self.assertEqual([row["report_type"] for row in visible], ["model_eval"])
        self.assertEqual(visible[0]["headline"], "Broker Bot Model Evaluation")
        self.assertIn("Key Metrics", visible[0]["body"])
        self.assertNotIn("ML Bot", visible[0]["body"])
        self.assertEqual(visible[0]["changes"], {})


if __name__ == "__main__":
    unittest.main()
