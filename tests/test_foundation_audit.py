from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from broker_bot.foundation_audit import FAIL, PASS, run_foundation_audit
from broker_bot.logging_db import init_db, log_equity


def _write_base_project(root: Path) -> None:
    (root / "data" / "reports").mkdir(parents=True)
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / ".env").write_text(
        "\n".join(
            [
                "ALPACA_API_KEY=test-key",
                "ALPACA_SECRET_KEY=test-secret",
                "UNIVERSE_PATH=data/sp500.csv",
                "SECTOR_MAP_PATH=data/sector_map.csv",
                "BROKER_BOT_DB=data/broker_bot.sqlite",
                "REPORTS_DIR=data/reports",
                "LEARNED_POLICY_PATH=data/learned_policy.json",
                "CHAMPION_POLICY_PATH=data/champion_challenger_policy.json",
                "AI_LAB_POLICY_PATH=data/ai_lab_policy.json",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    for filename in ["learned_policy.json", "champion_challenger_policy.json", "ai_lab_policy.json"]:
        (root / "data" / filename).write_text("{}", encoding="utf-8")
    for filename in ["advisor_snapshot.yml", "market_caretaker.yml"]:
        (root / ".github" / "workflows" / filename).write_text("name: test\n", encoding="utf-8")
    init_db(str(root / "data" / "broker_bot.sqlite"))


def _write_reports(root: Path, now: datetime) -> None:
    for prefix in ["summary", "supervisor", "model_eval"]:
        path = root / "data" / "reports" / f"{prefix}_20260813_120000.md"
        path.write_text("# report\n", encoding="utf-8")
        ts = now.timestamp()
        os.utime(path, (ts, ts))


def _write_snapshot(root: Path, now: datetime) -> None:
    (root / "data" / "dashboard_snapshot.json").write_text(
        json.dumps({"generated_at": now.isoformat(), "bots": {"ml": {}}}),
        encoding="utf-8",
    )


def _write_universe(root: Path, count: int) -> None:
    symbols = [f"T{i:03d}" for i in range(count)]
    sectors = ["Information Technology", "Health Care", "Industrials", "Financials"]
    (root / "data" / "sp500.csv").write_text(
        "symbol\n" + "\n".join(symbols) + "\n",
        encoding="utf-8",
    )
    (root / "data" / "sector_map.csv").write_text(
        "symbol,sector\n"
        + "\n".join(f"{symbol},{sectors[i % len(sectors)]}" for i, symbol in enumerate(symbols))
        + "\n",
        encoding="utf-8",
    )


def _insert_evaluated_decisions(root: Path, count: int, now: datetime) -> None:
    db_path = root / "data" / "broker_bot.sqlite"
    with sqlite3.connect(db_path) as conn:
        for i in range(count):
            cursor = conn.execute(
                """
                INSERT INTO decision_logs
                (ts, bot_name, symbol, side, selected, base_score, final_score, components, rationale)
                VALUES (?, 'ml', ?, 'LONG', 1, 0.01, 0.012, '{}', 'test')
                """,
                ((now - timedelta(days=2)).isoformat(), f"T{i:03d}"),
            )
            conn.execute(
                """
                INSERT INTO decision_outcomes
                (decision_id, evaluated_ts, horizon_days, realized_return, signed_return, spy_return, beat_spy, outcome_label)
                VALUES (?, ?, 1, 0.01, 0.01, 0.005, 0.005, 'win')
                """,
                (cursor.lastrowid, (now - timedelta(days=1)).isoformat()),
            )


class FoundationAuditTests(unittest.TestCase):
    def test_audit_flags_tiny_universe_and_stale_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict(os.environ, {}, clear=True):
            root = Path(tmpdir)
            _write_base_project(root)
            _write_universe(root, 10)
            stale_ts = datetime.now(timezone.utc) - timedelta(days=10)
            log_equity(
                str(root / "data" / "broker_bot.sqlite"),
                stale_ts.isoformat(),
                100000.0,
                50000.0,
                100000.0,
                500.0,
            )

            audit = run_foundation_audit(root)
            by_name = {check.name: check for check in audit.checks}

            self.assertEqual(audit.overall_status, FAIL)
            self.assertEqual(by_name["universe"].status, FAIL)
            self.assertEqual(by_name["database"].status, FAIL)

    def test_audit_passes_for_fresh_minimum_viable_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict(os.environ, {}, clear=True):
            root = Path(tmpdir)
            now = datetime.now(timezone.utc)
            _write_base_project(root)
            _write_universe(root, 120)
            _write_reports(root, now)
            _write_snapshot(root, now)
            log_equity(
                str(root / "data" / "broker_bot.sqlite"),
                now.isoformat(),
                100000.0,
                50000.0,
                100000.0,
                500.0,
            )
            _insert_evaluated_decisions(root, 30, now)

            audit = run_foundation_audit(root)

            self.assertEqual(audit.overall_status, PASS)
            self.assertEqual(audit.fail_count, 0)
            self.assertEqual(audit.warn_count, 0)

    def test_report_freshness_uses_embedded_timestamp_not_checkout_mtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict(os.environ, {}, clear=True):
            root = Path(tmpdir)
            now = datetime.now(timezone.utc)
            _write_base_project(root)
            _write_universe(root, 120)
            _write_snapshot(root, now)
            log_equity(
                str(root / "data" / "broker_bot.sqlite"),
                now.isoformat(),
                100000.0,
                50000.0,
                100000.0,
                500.0,
            )
            _insert_evaluated_decisions(root, 30, now)

            stale_report_ts = now - timedelta(days=30)
            for prefix in ["summary", "supervisor", "model_eval"]:
                path = root / "data" / "reports" / f"{prefix}_20260813_120000.md"
                path.write_text(f"# report\n\nGenerated at {stale_report_ts.isoformat()}\n", encoding="utf-8")
                fresh_mtime = now.timestamp()
                os.utime(path, (fresh_mtime, fresh_mtime))

            audit = run_foundation_audit(root)
            by_name = {check.name: check for check in audit.checks}

            self.assertEqual(by_name["reports"].status, FAIL)


if __name__ == "__main__":
    unittest.main()
