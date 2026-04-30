#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient

from broker_bot.bot_blueprint import get_strategy_blueprint
from broker_bot.config import configured_bot_names, get_bot_account_config, load_config
from broker_bot.bots import bot_label
from broker_bot.dashboard_metrics import agreement_summary, comparison_table, freshness_status
from broker_bot.logging_db import (
    init_db,
    read_recent_selected_decisions,
    read_latest_equity,
    read_latest_positions,
    read_latest_trades,
    read_latest_advisor_reports,
    read_latest_strategy_reports,
    read_available_bot_names,
)
from broker_bot.trader import snapshot_positions_with_protection


def _check_bot_auth(config, bot_name: str) -> dict:
    account = get_bot_account_config(config, bot_name)
    trading_status = "unknown"
    trading_message = ""
    data_status = "unknown"
    data_message = ""

    try:
        trading_account = TradingClient(account.api_key, account.secret_key, paper=True).get_account()
        trading_status = "ok"
        trading_message = str(getattr(trading_account, "status", "active"))
    except Exception as exc:
        trading_status = "failed"
        trading_message = f"{type(exc).__name__}: {exc}"

    try:
        request = StockBarsRequest(
            symbol_or_symbols=["SPY"],
            timeframe=TimeFrame.Day,
            start=datetime.now(timezone.utc) - timedelta(days=10),
            end=datetime.now(timezone.utc),
            feed=account.data_feed or "iex",
        )
        bars = StockHistoricalDataClient(account.api_key, account.secret_key).get_stock_bars(request).df
        data_status = "ok"
        data_message = f"{len(bars)} SPY bars via {account.data_feed or 'iex'}"
    except Exception as exc:
        data_status = "failed"
        data_message = f"{type(exc).__name__}: {exc}"

    return {
        "bot_name": bot_name,
        "label": bot_label(bot_name),
        "trading_auth": trading_status,
        "trading_message": trading_message,
        "market_data_auth": data_status,
        "market_data_message": data_message,
    }


def main() -> None:
    config = load_config()
    init_db(config.db_path)
    bot_names = sorted(set(read_available_bot_names(config.db_path)) | set(configured_bot_names(config)))

    bots_payload: dict[str, dict] = {}
    for bot_name in bot_names:
        equity_rows = list(reversed(read_latest_equity(config.db_path, limit=365, bot_name=bot_name)))
        trades_rows = list(reversed(read_latest_trades(config.db_path, limit=1000, bot_name=bot_name)))
        try:
            _, positions_live = snapshot_positions_with_protection(config, bot_name=bot_name)
        except Exception:
            positions_live = []
        positions_rows = read_latest_positions(config.db_path, limit=500, bot_name=bot_name) if not positions_live else []
        advisor_rows = read_latest_advisor_reports(config.db_path, limit=20, bot_name=bot_name)
        strategy_rows = read_latest_strategy_reports(config.db_path, limit=80, bot_name=bot_name)
        decision_rows = read_recent_selected_decisions(config.db_path, limit=150, bot_name=bot_name)

        bots_payload[bot_name] = {
            "label": bot_label(bot_name),
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
            "positions": positions_live if positions_live else [
                {
                    "symbol": row[0],
                    "qty": row[1],
                    "avg_entry": row[2],
                    "avg_entry_price": row[2],
                    "market_value": row[3],
                    "unreal_pl": row[4],
                    "unrealized_pl": row[4],
                    "protection_mode": "Unknown",
                    "protection_summary": "Snapshot built from DB only; no live Alpaca protection check.",
                    "take_profit_price": None,
                    "stop_price": None,
                    "trailing_stop": None,
                    "open_exit_order_count": 0,
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

    generated_at = datetime.now(timezone.utc).isoformat()
    data = {
        "generated_at": generated_at,
        "strategy_blueprint": get_strategy_blueprint(),
        "health": {
            "generated_at": generated_at,
            "freshness": freshness_status(generated_at),
            "bots": [_check_bot_auth(config, bot_name) for bot_name in bot_names],
        },
        "comparison": {
            "windows": {
                window_key: comparison_table(bots_payload, window_key=window_key)
                for window_key in ["24h", "7d", "14d", "28d", "90d", "180d", "360d"]
            },
            "agreement": agreement_summary(bots_payload),
        },
        "bots": bots_payload,
    }

    out_path = Path("data/dashboard_snapshot.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote snapshot to {out_path}")


if __name__ == "__main__":
    main()
