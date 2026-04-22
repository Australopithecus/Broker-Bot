#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from broker_bot.config import load_config
from broker_bot.logging_db import init_db, log_advisor_report, log_equity, log_positions, log_strategy_report, log_trades


def main() -> None:
    snapshot_path = Path("data/dashboard_snapshot.json")
    if not snapshot_path.exists():
        print("No snapshot found. Skipping restore.")
        return

    data = json.loads(snapshot_path.read_text(encoding="utf-8"))
    config = load_config()
    init_db(config.db_path)
    bots = data.get("bots")
    if not isinstance(bots, dict):
        bots = {"ml": data}

    for bot_name, bot_data in bots.items():
        for row in bot_data.get("equity", []):
            log_equity(
                config.db_path,
                row["ts"],
                float(row["equity"]),
                float(row.get("cash", 0.0)),
                float(row.get("portfolio_value", 0.0)),
                row.get("spy_value"),
                bot_name=bot_name,
            )

        trades = []
        for row in bot_data.get("trades", []):
            trades.append(
                (
                    row["ts"],
                    row["symbol"],
                    row["side"],
                    float(row["qty"]),
                    row.get("price"),
                    None,
                    row.get("status"),
                )
            )
        if trades:
            log_trades(config.db_path, trades, bot_name=bot_name)

        positions = []
        for row in bot_data.get("positions", []):
            positions.append(
                (
                    row["symbol"],
                    float(row["qty"]),
                    row.get("avg_entry_price"),
                    row.get("market_value"),
                    row.get("unrealized_pl"),
                )
            )
        if positions:
            log_positions(config.db_path, data.get("generated_at", ""), positions, bot_name=bot_name)

        for row in bot_data.get("advisor_reports", []):
            log_advisor_report(
                config.db_path,
                row["ts"],
                row.get("headline", "Advisor Report"),
                row.get("summary", ""),
                json.dumps(row.get("suggestions", [])),
                json.dumps(row.get("metrics", {})),
                json.dumps(row.get("overrides", {})),
                bot_name=bot_name,
            )

        for row in bot_data.get("strategy_reports", []):
            log_strategy_report(
                config.db_path,
                row["ts"],
                row.get("report_type", "strategy"),
                row.get("headline", "Strategy Report"),
                row.get("summary", ""),
                row.get("body", ""),
                json.dumps(row.get("metrics", {})),
                json.dumps(row.get("changes", {})),
                bot_name=bot_name,
            )

        decisions = bot_data.get("decisions", [])
        if decisions:
            with sqlite3.connect(config.db_path) as conn:
                for row in decisions:
                    cursor = conn.execute(
                        """
                        INSERT INTO decision_logs
                        (ts, bot_name, symbol, side, selected, base_score, final_score, components, rationale)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            row["ts"],
                            bot_name,
                            row["symbol"],
                            row.get("side", "HOLD"),
                            1,
                            float(row.get("base_score", 0.0)),
                            float(row.get("final_score", 0.0)),
                            json.dumps(row.get("components", {})),
                            row.get("rationale"),
                        ),
                    )
                    decision_id = int(cursor.lastrowid)
                    if row.get("outcome_label"):
                        signed_return = row.get("signed_return")
                        realized_return = row.get("realized_return")
                        if realized_return is None and signed_return is not None:
                            realized_return = float(signed_return) if row.get("side") == "LONG" else -float(signed_return)
                        beat_spy = row.get("beat_spy")
                        spy_return = None
                        if signed_return is not None and beat_spy is not None:
                            spy_return = float(signed_return) - float(beat_spy)
                        conn.execute(
                            """
                            INSERT OR REPLACE INTO decision_outcomes
                            (decision_id, evaluated_ts, horizon_days, realized_return, signed_return, spy_return, beat_spy, outcome_label)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                decision_id,
                                row.get("evaluated_ts") or data.get("generated_at", row["ts"]),
                                int(row.get("horizon_days") or config.prediction_horizon_days),
                                float(realized_return or 0.0),
                                float(signed_return or 0.0),
                                float(spy_return) if spy_return is not None else None,
                                float(beat_spy) if beat_spy is not None else None,
                                row.get("outcome_label", "flat"),
                            ),
                        )

    print("Snapshot restored into local DB")


if __name__ == "__main__":
    main()
