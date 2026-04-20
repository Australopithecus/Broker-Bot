from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable


def init_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS equity (
                ts TEXT PRIMARY KEY,
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
                report_type TEXT NOT NULL,
                headline TEXT,
                summary TEXT,
                body TEXT,
                metrics TEXT,
                changes TEXT
            )
            """
        )


def log_equity(db_path: str, ts: str, equity: float, cash: float, portfolio_value: float, spy_value: float | None) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO equity (ts, equity, cash, portfolio_value, spy_value) VALUES (?, ?, ?, ?, ?)",
            (ts, equity, cash, portfolio_value, spy_value),
        )


def log_trades(db_path: str, rows: Iterable[tuple[str, str, float, float | None, str | None, str | None]]) -> None:
    with sqlite3.connect(db_path) as conn:
        normalized = []
        for ts, symbol, side, qty, price, order_id, status in rows:
            price_val = float(price) if price is not None else None
            qty_val = float(qty)
            order_id_val = str(order_id) if order_id is not None else None
            status_val = str(status) if status is not None else None
            normalized.append((ts, symbol, side, qty_val, price_val, order_id_val, status_val))
        conn.executemany(
            "INSERT INTO trades (ts, symbol, side, qty, price, order_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            normalized,
        )


def log_positions(db_path: str, ts: str, rows: Iterable[tuple[str, float, float | None, float | None, float | None]]) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.executemany(
            "INSERT INTO positions (ts, symbol, qty, avg_entry_price, market_value, unrealized_pl) VALUES (?, ?, ?, ?, ?, ?)",
            [(ts, *row) for row in rows],
        )


def log_signals(db_path: str, ts: str, rows: Iterable[tuple[str, float, str]]) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.executemany(
            "INSERT INTO signals (ts, symbol, score, signal) VALUES (?, ?, ?, ?)",
            [(ts, *row) for row in rows],
        )


def read_latest_equity(db_path: str, limit: int = 120) -> list[tuple[str, float, float, float, float | None]]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "SELECT ts, equity, cash, portfolio_value, spy_value FROM equity ORDER BY ts DESC LIMIT ?",
            (limit,),
        )
        return cursor.fetchall()


def read_latest_positions(db_path: str, limit: int = 200) -> list[tuple[str, float, float | None, float | None, float | None]]:
    with sqlite3.connect(db_path) as conn:
        latest = conn.execute("SELECT ts FROM positions ORDER BY ts DESC LIMIT 1").fetchone()
        if not latest:
            return []
        cursor = conn.execute(
            """
            SELECT symbol, qty, avg_entry_price, market_value, unrealized_pl
            FROM positions
            WHERE ts = ?
            ORDER BY ABS(COALESCE(market_value, 0)) DESC, symbol ASC
            LIMIT ?
            """,
            (latest[0], limit),
        )
        return cursor.fetchall()


def read_latest_trades(db_path: str, limit: int = 200) -> list[tuple[str, str, str, float, float | None, str | None]]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "SELECT ts, symbol, side, qty, price, status FROM trades ORDER BY ts DESC LIMIT ?",
            (limit,),
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
) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO advisor_reports (ts, headline, summary, suggestions, metrics, overrides) VALUES (?, ?, ?, ?, ?, ?)",
            (ts, headline, summary, suggestions_json, metrics_json, overrides_json),
        )


def read_latest_advisor_reports(db_path: str, limit: int = 10) -> list[tuple[str, str, str, str, str, str]]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "SELECT ts, headline, summary, suggestions, metrics, overrides FROM advisor_reports ORDER BY ts DESC LIMIT ?",
            (limit,),
        )
        return cursor.fetchall()


def log_decision_run(db_path: str, ts: str, regime_leverage: float, spy_vol: float, context_json: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO decision_runs (ts, regime_leverage, spy_vol, context) VALUES (?, ?, ?, ?)",
            (ts, regime_leverage, spy_vol, context_json),
        )


def read_latest_decision_run(db_path: str) -> tuple[str, float | None, float | None, str | None] | None:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT ts, regime_leverage, spy_vol, context FROM decision_runs ORDER BY ts DESC LIMIT 1"
        ).fetchone()
        return row


def log_decision_logs(
    db_path: str,
    ts: str,
    rows: Iterable[tuple[str, str, int, float, float, str | None, str | None]],
) -> None:
    with sqlite3.connect(db_path) as conn:
        normalized = []
        for symbol, side, selected, base_score, final_score, components, rationale in rows:
            normalized.append(
                (
                    ts,
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
            (ts, symbol, side, selected, base_score, final_score, components, rationale)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            normalized,
        )


def read_pending_decision_logs(
    db_path: str,
    cutoff_ts: str,
    limit: int = 1000,
) -> list[tuple[int, str, str, str, float, str | None]]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            """
            SELECT dl.id, dl.ts, dl.symbol, dl.side, dl.final_score, dl.components
            FROM decision_logs dl
            LEFT JOIN decision_outcomes do ON do.decision_id = dl.id
            WHERE dl.selected = 1
              AND do.decision_id IS NULL
              AND dl.ts <= ?
            ORDER BY dl.ts ASC, ABS(dl.final_score) DESC
            LIMIT ?
            """,
            (cutoff_ts, limit),
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
    db_path: str, limit: int = 300
) -> list[tuple[str, str, str, float, float, float | None, float | None, str | None]]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            """
            SELECT dl.symbol, dl.side, do.evaluated_ts, do.realized_return, do.signed_return, do.spy_return, do.beat_spy, dl.components
            FROM decision_outcomes do
            JOIN decision_logs dl ON dl.id = do.decision_id
            ORDER BY do.evaluated_ts DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cursor.fetchall()


def read_recent_decision_logs(
    db_path: str, limit: int = 100
) -> list[tuple[str, str, str, int, float, float, str | None, str | None]]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            """
            SELECT ts, symbol, side, selected, base_score, final_score, components, rationale
            FROM decision_logs
            ORDER BY ts DESC, ABS(final_score) DESC
            LIMIT ?
            """,
            (limit,),
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
) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO strategy_reports
            (ts, report_type, headline, summary, body, metrics, changes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (ts, report_type, headline, summary, body, metrics_json, changes_json),
        )


def read_latest_strategy_reports(
    db_path: str, limit: int = 10
) -> list[tuple[str, str, str, str, str, str, str]]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            """
            SELECT ts, report_type, headline, summary, body, metrics, changes
            FROM strategy_reports
            ORDER BY ts DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cursor.fetchall()


def read_recent_selected_decisions(
    db_path: str, limit: int = 100
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
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            """
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
            ORDER BY dl.ts DESC, ABS(dl.final_score) DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cursor.fetchall()
