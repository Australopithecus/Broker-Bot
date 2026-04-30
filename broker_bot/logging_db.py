from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from .bots import ML_BOT_NAME, normalize_bot_name


BOT_SQL = "COALESCE(NULLIF(bot_name, ''), 'ml')"


def _column_names(conn: sqlite3.Connection, table_name: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {str(row[1]) for row in rows}


def _ensure_column(conn: sqlite3.Connection, table_name: str, column_name: str, ddl: str) -> None:
    if column_name in _column_names(conn, table_name):
        return
    conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {ddl}")


def init_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS equity (
                ts TEXT PRIMARY KEY,
                bot_name TEXT DEFAULT 'ml',
                equity REAL NOT NULL,
                cash REAL NOT NULL,
                portfolio_value REAL NOT NULL,
                spy_value REAL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                bot_name TEXT DEFAULT 'ml',
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                qty REAL NOT NULL,
                price REAL,
                order_id TEXT,
                status TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                bot_name TEXT DEFAULT 'ml',
                symbol TEXT NOT NULL,
                qty REAL NOT NULL,
                avg_entry_price REAL,
                market_value REAL,
                unrealized_pl REAL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                bot_name TEXT DEFAULT 'ml',
                symbol TEXT NOT NULL,
                score REAL NOT NULL,
                signal TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS advisor_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                bot_name TEXT DEFAULT 'ml',
                headline TEXT,
                summary TEXT,
                suggestions TEXT,
                metrics TEXT,
                overrides TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS decision_runs (
                ts TEXT PRIMARY KEY,
                bot_name TEXT DEFAULT 'ml',
                regime_leverage REAL,
                spy_vol REAL,
                context TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS decision_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                bot_name TEXT DEFAULT 'ml',
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                selected INTEGER NOT NULL,
                base_score REAL NOT NULL,
                final_score REAL NOT NULL,
                components TEXT,
                rationale TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS decision_outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_id INTEGER NOT NULL UNIQUE,
                evaluated_ts TEXT NOT NULL,
                horizon_days INTEGER NOT NULL,
                realized_return REAL NOT NULL,
                signed_return REAL NOT NULL,
                spy_return REAL,
                beat_spy REAL,
                outcome_label TEXT NOT NULL,
                FOREIGN KEY(decision_id) REFERENCES decision_logs(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS strategy_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                bot_name TEXT DEFAULT 'ml',
                report_type TEXT NOT NULL,
                headline TEXT,
                summary TEXT,
                body TEXT,
                metrics TEXT,
                changes TEXT
            )
            """
        )
        for table_name in ["equity", "trades", "positions", "signals", "advisor_reports", "decision_runs", "decision_logs", "strategy_reports"]:
            _ensure_column(conn, table_name, "bot_name", "bot_name TEXT DEFAULT 'ml'")


def log_equity(
    db_path: str,
    ts: str,
    equity: float,
    cash: float,
    portfolio_value: float,
    spy_value: float | None,
    bot_name: str = ML_BOT_NAME,
) -> None:
    bot = normalize_bot_name(bot_name)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO equity (ts, bot_name, equity, cash, portfolio_value, spy_value) VALUES (?, ?, ?, ?, ?, ?)",
            (ts, bot, equity, cash, portfolio_value, spy_value),
        )


def log_trades(
    db_path: str,
    rows: Iterable[tuple[str, str, str, float, float | None, str | None, str | None]],
    bot_name: str = ML_BOT_NAME,
) -> None:
    bot = normalize_bot_name(bot_name)
    with sqlite3.connect(db_path) as conn:
        normalized = []
        for ts, symbol, side, qty, price, order_id, status in rows:
            price_val = float(price) if price is not None else None
            qty_val = float(qty)
            order_id_val = str(order_id) if order_id is not None else None
            status_val = str(status) if status is not None else None
            normalized.append((ts, bot, symbol, side, qty_val, price_val, order_id_val, status_val))
        conn.executemany(
            "INSERT INTO trades (ts, bot_name, symbol, side, qty, price, order_id, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            normalized,
        )


def log_positions(
    db_path: str,
    ts: str,
    rows: Iterable[tuple[str, float, float | None, float | None, float | None]],
    bot_name: str = ML_BOT_NAME,
) -> None:
    bot = normalize_bot_name(bot_name)
    with sqlite3.connect(db_path) as conn:
        conn.executemany(
            "INSERT INTO positions (ts, bot_name, symbol, qty, avg_entry_price, market_value, unrealized_pl) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [(ts, bot, *row) for row in rows],
        )


def log_signals(
    db_path: str,
    ts: str,
    rows: Iterable[tuple[str, float, str]],
    bot_name: str = ML_BOT_NAME,
) -> None:
    bot = normalize_bot_name(bot_name)
    with sqlite3.connect(db_path) as conn:
        conn.executemany(
            "INSERT INTO signals (ts, bot_name, symbol, score, signal) VALUES (?, ?, ?, ?, ?)",
            [(ts, bot, *row) for row in rows],
        )


def read_latest_equity(db_path: str, limit: int = 120, bot_name: str = ML_BOT_NAME) -> list[tuple[str, float, float, float, float | None]]:
    bot = normalize_bot_name(bot_name)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            f"SELECT ts, equity, cash, portfolio_value, spy_value FROM equity WHERE {BOT_SQL} = ? ORDER BY ts DESC LIMIT ?",
            (bot, limit),
        )
        return cursor.fetchall()


def read_latest_positions(
    db_path: str,
    limit: int = 200,
    bot_name: str = ML_BOT_NAME,
) -> list[tuple[str, float, float | None, float | None, float | None]]:
    bot = normalize_bot_name(bot_name)
    with sqlite3.connect(db_path) as conn:
        latest = conn.execute(
            f"SELECT ts FROM positions WHERE {BOT_SQL} = ? ORDER BY ts DESC LIMIT 1",
            (bot,),
        ).fetchone()
        if not latest:
            return []
        cursor = conn.execute(
            """
            SELECT symbol, qty, avg_entry_price, market_value, unrealized_pl
            FROM positions
            WHERE ts = ? AND COALESCE(NULLIF(bot_name, ''), 'ml') = ?
            ORDER BY ABS(COALESCE(market_value, 0)) DESC, symbol ASC
            LIMIT ?
            """,
            (latest[0], bot, limit),
        )
        return cursor.fetchall()


def read_latest_trades(
    db_path: str,
    limit: int = 200,
    bot_name: str = ML_BOT_NAME,
) -> list[tuple[str, str, str, float, float | None, str | None]]:
    bot = normalize_bot_name(bot_name)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            f"SELECT ts, symbol, side, qty, price, status FROM trades WHERE {BOT_SQL} = ? ORDER BY ts DESC LIMIT ?",
            (bot, limit),
        )
        return cursor.fetchall()


def log_advisor_report(
    db_path: str,
    ts: str,
    headline: str,
    summary: str,
    suggestions_json: str,
    metrics_json: str,
    overrides_json: str,
    bot_name: str = ML_BOT_NAME,
) -> None:
    bot = normalize_bot_name(bot_name)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO advisor_reports (ts, bot_name, headline, summary, suggestions, metrics, overrides) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (ts, bot, headline, summary, suggestions_json, metrics_json, overrides_json),
        )


def read_latest_advisor_reports(
    db_path: str,
    limit: int = 10,
    bot_name: str = ML_BOT_NAME,
) -> list[tuple[str, str, str, str, str, str]]:
    bot = normalize_bot_name(bot_name)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            f"SELECT ts, headline, summary, suggestions, metrics, overrides FROM advisor_reports WHERE {BOT_SQL} = ? ORDER BY ts DESC LIMIT ?",
            (bot, limit),
        )
        return cursor.fetchall()


def log_decision_run(
    db_path: str,
    ts: str,
    regime_leverage: float,
    spy_vol: float,
    context_json: str,
    bot_name: str = ML_BOT_NAME,
) -> None:
    bot = normalize_bot_name(bot_name)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO decision_runs (ts, bot_name, regime_leverage, spy_vol, context) VALUES (?, ?, ?, ?, ?)",
            (ts, bot, regime_leverage, spy_vol, context_json),
        )


def read_latest_decision_run(db_path: str, bot_name: str = ML_BOT_NAME) -> tuple[str, float | None, float | None, str | None] | None:
    bot = normalize_bot_name(bot_name)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            f"SELECT ts, regime_leverage, spy_vol, context FROM decision_runs WHERE {BOT_SQL} = ? ORDER BY ts DESC LIMIT 1",
            (bot,),
        ).fetchone()
        return row


def log_decision_logs(
    db_path: str,
    ts: str,
    rows: Iterable[tuple[str, str, int, float, float, str | None, str | None]],
    bot_name: str = ML_BOT_NAME,
) -> None:
    bot = normalize_bot_name(bot_name)
    with sqlite3.connect(db_path) as conn:
        normalized = []
        for symbol, side, selected, base_score, final_score, components, rationale in rows:
            normalized.append(
                (
                    ts,
                    bot,
                    symbol,
                    side,
                    int(selected),
                    float(base_score),
                    float(final_score),
                    components,
                    rationale,
                )
            )
        conn.executemany(
            """
            INSERT INTO decision_logs
            (ts, bot_name, symbol, side, selected, base_score, final_score, components, rationale)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            normalized,
        )


def read_pending_decision_logs(
    db_path: str,
    cutoff_ts: str,
    limit: int = 1000,
    bot_name: str = ML_BOT_NAME,
) -> list[tuple[int, str, str, str, float, str | None]]:
    bot = normalize_bot_name(bot_name)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            f"""
            SELECT dl.id, dl.ts, dl.symbol, dl.side, dl.final_score, dl.components
            FROM decision_logs dl
            LEFT JOIN decision_outcomes do ON do.decision_id = dl.id
            WHERE dl.selected = 1
              AND {BOT_SQL} = ?
              AND do.decision_id IS NULL
              AND dl.ts <= ?
            ORDER BY dl.ts ASC, ABS(dl.final_score) DESC
            LIMIT ?
            """,
            (bot, cutoff_ts, limit),
        )
        return cursor.fetchall()


def log_decision_outcomes(
    db_path: str,
    rows: Iterable[tuple[int, str, int, float, float, float | None, float | None, str]],
) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO decision_outcomes
            (decision_id, evaluated_ts, horizon_days, realized_return, signed_return, spy_return, beat_spy, outcome_label)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            list(rows),
        )


def read_recent_evaluated_decisions(
    db_path: str,
    limit: int = 300,
    bot_name: str = ML_BOT_NAME,
) -> list[tuple[str, str, str, float, float, float | None, float | None, str | None]]:
    bot = normalize_bot_name(bot_name)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            f"""
            SELECT dl.symbol, dl.side, do.evaluated_ts, do.realized_return, do.signed_return, do.spy_return, do.beat_spy, dl.components
            FROM decision_outcomes do
            JOIN decision_logs dl ON dl.id = do.decision_id
            WHERE {BOT_SQL} = ?
            ORDER BY do.evaluated_ts DESC
            LIMIT ?
            """,
            (bot, limit),
        )
        return cursor.fetchall()


def read_recent_decision_logs(
    db_path: str,
    limit: int = 100,
    bot_name: str = ML_BOT_NAME,
) -> list[tuple[str, str, str, int, float, float, str | None, str | None]]:
    bot = normalize_bot_name(bot_name)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            f"""
            SELECT ts, symbol, side, selected, base_score, final_score, components, rationale
            FROM decision_logs
            WHERE {BOT_SQL} = ?
            ORDER BY ts DESC, ABS(final_score) DESC
            LIMIT ?
            """,
            (bot, limit),
        )
        return cursor.fetchall()


def log_strategy_report(
    db_path: str,
    ts: str,
    report_type: str,
    headline: str,
    summary: str,
    body: str,
    metrics_json: str,
    changes_json: str,
    bot_name: str = ML_BOT_NAME,
) -> None:
    bot = normalize_bot_name(bot_name)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO strategy_reports
            (ts, bot_name, report_type, headline, summary, body, metrics, changes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (ts, bot, report_type, headline, summary, body, metrics_json, changes_json),
        )


def read_latest_strategy_reports(
    db_path: str,
    limit: int = 10,
    bot_name: str = ML_BOT_NAME,
    report_type: str | None = None,
) -> list[tuple[str, str, str, str, str, str, str]]:
    bot = normalize_bot_name(bot_name)
    params: list[object] = [bot]
    where = [f"{BOT_SQL} = ?"]
    if report_type:
        where.append("report_type = ?")
        params.append(report_type)
    params.append(limit)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            f"""
            SELECT ts, report_type, headline, summary, body, metrics, changes
            FROM strategy_reports
            WHERE {" AND ".join(where)}
            ORDER BY ts DESC
            LIMIT ?
            """,
            params,
        )
        return cursor.fetchall()


def read_recent_selected_decisions(
    db_path: str,
    limit: int = 100,
    bot_name: str = ML_BOT_NAME,
) -> list[
    tuple[
        str,
        str,
        str,
        float,
        float,
        str | None,
        str | None,
        str | None,
        int | None,
        float | None,
        float | None,
        float | None,
        str | None,
    ]
]:
    bot = normalize_bot_name(bot_name)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            f"""
            SELECT
                dl.ts,
                dl.symbol,
                dl.side,
                dl.base_score,
                dl.final_score,
                dl.components,
                dl.rationale,
                do.evaluated_ts,
                do.horizon_days,
                do.realized_return,
                do.signed_return,
                do.beat_spy,
                do.outcome_label
            FROM decision_logs dl
            LEFT JOIN decision_outcomes do ON do.decision_id = dl.id
            WHERE dl.selected = 1
              AND {BOT_SQL} = ?
            ORDER BY dl.ts DESC, ABS(dl.final_score) DESC
            LIMIT ?
            """,
            (bot, limit),
        )
        return cursor.fetchall()


def read_available_bot_names(db_path: str) -> list[str]:
    bots: set[str] = {ML_BOT_NAME}
    with sqlite3.connect(db_path) as conn:
        for table_name in ["equity", "trades", "positions", "advisor_reports", "decision_logs", "strategy_reports"]:
            if "bot_name" not in _column_names(conn, table_name):
                continue
            rows = conn.execute(
                f"SELECT DISTINCT {BOT_SQL} FROM {table_name} WHERE bot_name IS NOT NULL"
            ).fetchall()
            bots.update(str(row[0]) for row in rows if row and row[0])
    return sorted(bots)
