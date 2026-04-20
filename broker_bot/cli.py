from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .config import load_config
from .logging_db import (
    init_db,
    log_advisor_report,
    log_decision_logs,
    log_decision_run,
    log_equity,
    log_positions,
    log_signals,
    log_trades,
)
from .learning import generate_strategy_report, review_and_learn
from .pipeline import train_on_history, run_backtest_on_history
from .data import fetch_latest_close
from .trader import rebalance_portfolio, snapshot_equity, snapshot_positions
from .universe import load_universe
from .dashboard_tk import launch_dashboard
from .dashboard_web import create_app
from .advisor import generate_advisor_report, save_overrides


def _load_symbols(config) -> list[str]:
    return load_universe(config.universe_path)


def cmd_init_db(args: argparse.Namespace) -> None:
    config = load_config()
    init_db(config.db_path)
    print(f"Initialized DB at {config.db_path}")


def cmd_train(args: argparse.Namespace) -> None:
    config = load_config()
    symbols = _load_symbols(config)
    model_path, metrics = train_on_history(config, symbols)
    print(
        f"Model saved to {model_path} (in-sample r2: {metrics['r2']:.3f}, MAE: {metrics['mae']:.6f})"
    )


def cmd_backtest(args: argparse.Namespace) -> None:
    config = load_config()
    symbols = _load_symbols(config)
    results = run_backtest_on_history(config, symbols)
    if results.empty:
        print("Backtest returned no rows.")
        return

    total_return = float(results["strategy_equity"].iloc[-1] - 1.0)
    avg_daily = float(results["strategy_return"].mean())
    vol = float(results["strategy_return"].std()) if len(results) > 1 else 0.0
    hit_rate = float((results["strategy_return"] > 0).mean())
    avg_alpha = float(results["alpha"].mean()) if "alpha" in results.columns else 0.0
    avg_turnover = float(results["turnover"].mean()) if "turnover" in results.columns else 0.0
    print(
        "Backtest summary: "
        f"total_return={total_return:.2%}, avg_period_return={avg_daily:.3%}, "
        f"vol={vol:.3%}, hit_rate={hit_rate:.1%}, avg_alpha={avg_alpha:.3%}, "
        f"avg_turnover={avg_turnover:.3f}"
    )
    print(results.tail(5).to_string(index=False))


def cmd_rebalance(args: argparse.Namespace) -> None:
    config = load_config()
    init_db(config.db_path)
    review_summary = "Learning skipped."
    try:
        review_report = review_and_learn(config)
        review_summary = review_report.summary
    except Exception as exc:
        review_summary = f"Learning skipped: {exc}"
    config = load_config()
    symbols = _load_symbols(config)

    ts, orders, signals, decision_context = rebalance_portfolio(config, symbols)
    if orders:
        log_trades(config.db_path, orders)

    log_decision_run(
        config.db_path,
        ts,
        float(decision_context.get("effective_leverage", 0.0)),
        float(decision_context.get("spy_vol", 0.0)),
        json.dumps(decision_context),
    )
    log_decision_logs(
        config.db_path,
        ts,
        [
            (
                signal.symbol,
                signal.side,
                1 if signal.selected else 0,
                float(signal.base_score if signal.base_score is not None else signal.score),
                float(signal.score),
                json.dumps(signal.components or {}, sort_keys=True),
                signal.rationale or None,
            )
            for signal in signals
        ],
    )

    log_signals(
        config.db_path,
        ts,
        [(s.symbol, s.score, s.side) for s in signals],
    )

    ts_pos, positions = snapshot_positions(config)
    log_positions(config.db_path, ts_pos, positions)

    spy_value = fetch_latest_close(config, "SPY")
    ts_eq, equity, cash, port = snapshot_equity(config)
    log_equity(config.db_path, ts_eq, equity, cash, port, spy_value=spy_value)

    print(
        f"Rebalanced at {ts} with {len(orders)} orders. "
        f"Learning summary: {review_summary}"
    )


def cmd_snapshot(args: argparse.Namespace) -> None:
    config = load_config()
    init_db(config.db_path)
    ts_pos, positions = snapshot_positions(config)
    log_positions(config.db_path, ts_pos, positions)

    spy_value = fetch_latest_close(config, "SPY")
    ts_eq, equity, cash, port = snapshot_equity(config)
    log_equity(config.db_path, ts_eq, equity, cash, port, spy_value=spy_value)

    print(f"Snapshot saved at {ts_eq}.")


def cmd_dashboard(args: argparse.Namespace) -> None:
    config = load_config()
    init_db(config.db_path)
    launch_dashboard(config.db_path)


def cmd_dashboard_web(args: argparse.Namespace) -> None:
    config = load_config()
    init_db(config.db_path)
    app = create_app(config.db_path)
    host = os.getenv("DASHBOARD_HOST", "127.0.0.1")
    port = int(os.getenv("DASHBOARD_PORT", "8000"))
    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("uvicorn not installed. Run: pip install -r requirements.txt") from exc
    uvicorn.run(app, host=host, port=port, log_level="info")


def cmd_advisor(args: argparse.Namespace) -> None:
    config = load_config()
    init_db(config.db_path)
    report = generate_advisor_report(config)

    log_advisor_report(
        config.db_path,
        report.ts,
        report.headline,
        report.summary,
        json.dumps(report.suggestions),
        json.dumps(report.metrics),
        json.dumps(report.overrides),
    )

    if config.advisor_auto_apply and report.overrides:
        save_overrides(config.advisor_overrides_path, report.overrides)
        print(f"Advisor applied overrides to {config.advisor_overrides_path}.")
    else:
        print("Advisor report generated (no overrides applied).")


def cmd_review_decisions(args: argparse.Namespace) -> None:
    config = load_config()
    init_db(config.db_path)
    report = review_and_learn(config)
    print(f"{report.headline}: {report.summary}")
    if report.report_path:
        print(f"Saved report to {report.report_path}")


def cmd_strategy_report(args: argparse.Namespace) -> None:
    config = load_config()
    init_db(config.db_path)
    report = generate_strategy_report(config)
    print(f"{report.headline}: {report.summary}")
    print(f"Saved report to {report.report_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Broker Bot - Paper Trading")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-db")
    subparsers.add_parser("train")
    subparsers.add_parser("backtest")
    subparsers.add_parser("rebalance")
    subparsers.add_parser("snapshot")
    subparsers.add_parser("dashboard")
    subparsers.add_parser("dashboard-web")
    subparsers.add_parser("advisor-report")
    subparsers.add_parser("review-decisions")
    subparsers.add_parser("strategy-report")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init-db":
        cmd_init_db(args)
    elif args.command == "train":
        cmd_train(args)
    elif args.command == "backtest":
        cmd_backtest(args)
    elif args.command == "rebalance":
        cmd_rebalance(args)
    elif args.command == "snapshot":
        cmd_snapshot(args)
    elif args.command == "dashboard":
        cmd_dashboard(args)
    elif args.command == "dashboard-web":
        cmd_dashboard_web(args)
    elif args.command == "advisor-report":
        cmd_advisor(args)
    elif args.command == "review-decisions":
        cmd_review_decisions(args)
    elif args.command == "strategy-report":
        cmd_strategy_report(args)


if __name__ == "__main__":
    main()
