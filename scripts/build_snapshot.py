#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from broker_bot.config import load_config
from broker_bot.logging_db import (
    init_db,
    read_recent_selected_decisions,
    read_latest_equity,
    read_latest_positions,
    read_latest_trades,
    read_latest_advisor_reports,
    read_latest_strategy_reports,
)


def main() -> None:
    config = load_config()
    init_db(config.db_path)

    equity_rows = list(reversed(read_latest_equity(config.db_path, limit=365)))
    trades_rows = list(reversed(read_latest_trades(config.db_path, limit=1000)))
    positions_rows = read_latest_positions(config.db_path, limit=500)
    advisor_rows = read_latest_advisor_reports(config.db_path, limit=20)
    strategy_rows = read_latest_strategy_reports(config.db_path, limit=20)
    decision_rows = read_recent_selected_decisions(config.db_path, limit=100)

    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "equity": [
            {
                "ts": row[0],
                "equity": row[1],
                "cash": row[2],
                "portfolio_value": row[3],
                "spy_value": row[4],
            }
            for row in equity_rows
        ],
        "trades": [
            {
                "ts": row[0],
                "symbol": row[1],
                "side": row[2],
                "qty": row[3],
                "price": row[4],
                "status": row[5],
            }
            for row in trades_rows
        ],
        "positions": [
            {
                "symbol": row[0],
                "qty": row[1],
                "avg_entry_price": row[2],
                "market_value": row[3],
                "unrealized_pl": row[4],
            }
            for row in positions_rows
        ],
        "advisor_reports": [
            {
                "ts": row[0],
                "headline": row[1],
                "summary": row[2],
                "suggestions": json.loads(row[3]) if row[3] else [],
                "metrics": json.loads(row[4]) if row[4] else {},
                "overrides": json.loads(row[5]) if row[5] else {},
            }
            for row in advisor_rows
        ],
        "strategy_reports": [
            {
                "ts": row[0],
                "report_type": row[1],
                "headline": row[2],
                "summary": row[3],
                "body": row[4],
                "metrics": json.loads(row[5]) if row[5] else {},
                "changes": json.loads(row[6]) if row[6] else {},
            }
            for row in strategy_rows
        ],
        "decisions": [
            {
                "ts": row[0],
                "symbol": row[1],
                "side": row[2],
                "base_score": row[3],
                "final_score": row[4],
                "components": json.loads(row[5]) if row[5] else {},
                "rationale": row[6],
                "evaluated_ts": row[7],
                "horizon_days": row[8],
                "realized_return": row[9],
                "signed_return": row[10],
                "beat_spy": row[11],
                "outcome_label": row[12],
            }
            for row in decision_rows
        ],
    }

    out_path = Path("data/dashboard_snapshot.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote snapshot to {out_path}")


if __name__ == "__main__":
    main()
