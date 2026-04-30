from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient

from .config import configured_bot_names, get_bot_account_config, load_config
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
from .trader import caretaker_portfolio, rebalance_portfolio, snapshot_equity, snapshot_positions
from .universe import load_universe
from .dashboard_tk import launch_dashboard
from .dashboard_web import create_app
from .advisor import generate_advisor_report, save_overrides
from .bots import LLM_BOT_NAME, ML_BOT_NAME
from .llm_bot import generate_llm_bot_status_report, generate_llm_coach_report, rebalance_llm_bot
from .options import generate_options_scaffold_report


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


def _credential_label(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return "missing"
    return f"set, len={len(value)}"


def cmd_doctor(args: argparse.Namespace) -> None:
    config = load_config()
    print("Broker Bot configuration check")
    print(f"ALPACA_API_KEY: {_credential_label(config.alpaca_api_key)}")
    print(f"ALPACA_SECRET_KEY: {_credential_label(config.alpaca_secret_key)}")
    print(f"ALPACA_DATA_FEED: {config.alpaca_data_feed or 'iex'}")
    print(f"ALPACA_LLM_API_KEY: {_credential_label(config.llm_alpaca_api_key)}")
    print(f"ALPACA_LLM_SECRET_KEY: {_credential_label(config.llm_alpaca_secret_key)}")
    print(f"ALPACA_LLM_DATA_FEED: {config.llm_alpaca_data_feed or config.alpaca_data_feed or 'iex'}")
    print("")

    failures = 0
    for bot_name in configured_bot_names(config):
        account = get_bot_account_config(config, bot_name)
        label = account.bot_name.upper()
        print(f"{label} account")
        try:
            trading_account = TradingClient(account.api_key, account.secret_key, paper=True).get_account()
            print(f"  Trading auth: OK status={getattr(trading_account, 'status', 'unknown')}")
        except Exception as exc:
            failures += 1
            print(f"  Trading auth: FAILED {type(exc).__name__}: {exc}")

        try:
            request = StockBarsRequest(
                symbol_or_symbols=["SPY"],
                timeframe=TimeFrame.Day,
                start=datetime.now(timezone.utc) - timedelta(days=10),
                end=datetime.now(timezone.utc),
                feed=account.data_feed or "iex",
            )
            bars = StockHistoricalDataClient(account.api_key, account.secret_key).get_stock_bars(request).df
            print(f"  Market data auth: OK rows={len(bars)} feed={account.data_feed or 'iex'}")
        except Exception as exc:
            failures += 1
            print(f"  Market data auth: FAILED {type(exc).__name__}: {exc}")
        print("")

    if failures:
        print(
            "One or more Alpaca checks failed. For a 401/403, regenerate paper API keys in Alpaca, "
            "update .env, and keep ALPACA_DATA_FEED=iex unless you have SIP access."
        )
        raise SystemExit(1)
    print("All configured Alpaca checks passed.")


def cmd_rebalance(args: argparse.Namespace) -> None:
    _cmd_rebalance_for_bot(ML_BOT_NAME)


def _cmd_rebalance_for_bot(bot_name: str) -> None:
    config = load_config()
    init_db(config.db_path)
    review_summary = "Learning skipped."
    try:
        review_report = review_and_learn(config, bot_name=bot_name)
        review_summary = review_report.summary
    except Exception as exc:
        review_summary = f"Learning skipped: {exc}"
    config = load_config()
    symbols = _load_symbols(config)

    ts, orders, signals, decision_context = rebalance_portfolio(config, symbols, bot_name=bot_name)
    if orders:
        log_trades(config.db_path, orders, bot_name=bot_name)

    log_decision_run(
        config.db_path,
        ts,
        float(decision_context.get("effective_leverage", 0.0)),
        float(decision_context.get("spy_vol", 0.0)),
        json.dumps(decision_context),
        bot_name=bot_name,
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
        bot_name=bot_name,
    )

    log_signals(
        config.db_path,
        ts,
        [(s.symbol, s.score, s.side) for s in signals],
        bot_name=bot_name,
    )

    ts_pos, positions = snapshot_positions(config, bot_name=bot_name)
    log_positions(config.db_path, ts_pos, positions, bot_name=bot_name)

    spy_value = fetch_latest_close(config, "SPY", bot_name=bot_name)
    ts_eq, equity, cash, port = snapshot_equity(config, bot_name=bot_name)
    log_equity(config.db_path, ts_eq, equity, cash, port, spy_value=spy_value, bot_name=bot_name)

    print(
        f"{bot_name.upper()} rebalanced at {ts} with {len(orders)} orders. "
        f"Learning summary: {review_summary}"
    )


def cmd_snapshot(args: argparse.Namespace) -> None:
    _cmd_snapshot_for_bot(ML_BOT_NAME)


def _cmd_snapshot_for_bot(bot_name: str) -> None:
    config = load_config()
    init_db(config.db_path)
    ts_pos, positions = snapshot_positions(config, bot_name=bot_name)
    log_positions(config.db_path, ts_pos, positions, bot_name=bot_name)

    spy_value = fetch_latest_close(config, "SPY", bot_name=bot_name)
    ts_eq, equity, cash, port = snapshot_equity(config, bot_name=bot_name)
    log_equity(config.db_path, ts_eq, equity, cash, port, spy_value=spy_value, bot_name=bot_name)

    print(f"{bot_name.upper()} snapshot saved at {ts_eq}.")


def cmd_caretaker(args: argparse.Namespace) -> None:
    _cmd_caretaker_for_bot(ML_BOT_NAME)


def cmd_caretaker_llm(args: argparse.Namespace) -> None:
    _cmd_caretaker_for_bot(LLM_BOT_NAME)


def cmd_caretaker_all(args: argparse.Namespace) -> None:
    config = load_config()
    for bot_name in configured_bot_names(config):
        _run_caretaker_for_bot(config, bot_name)


def _cmd_caretaker_for_bot(bot_name: str) -> None:
    config = load_config()
    _run_caretaker_for_bot(config, bot_name)


def _run_caretaker_for_bot(config, bot_name: str) -> None:
    init_db(config.db_path)
    ts, orders, summary = caretaker_portfolio(config, bot_name=bot_name)
    if orders:
        log_trades(config.db_path, orders, bot_name=bot_name)

    ts_pos, positions = snapshot_positions(config, bot_name=bot_name)
    log_positions(config.db_path, ts_pos, positions, bot_name=bot_name)

    spy_value = fetch_latest_close(config, "SPY", bot_name=bot_name)
    ts_eq, equity, cash, port = snapshot_equity(config, bot_name=bot_name)
    log_equity(config.db_path, ts_eq, equity, cash, port, spy_value=spy_value, bot_name=bot_name)

    print(
        f"{bot_name.upper()} caretaker checked {summary.get('positions_seen', 0)} positions at {ts}. "
        f"Submitted {summary.get('protection_submitted', 0)} protection orders; "
        f"already protected {summary.get('already_protected', 0)}."
    )
    if summary.get("kill_switch_triggered"):
        print(
            f"{bot_name.upper()} daily drawdown kill switch triggered at "
            f"{float(summary.get('daily_drawdown') or 0.0):.2%}."
        )


def cmd_rebalance_llm(args: argparse.Namespace) -> None:
    config = load_config()
    init_db(config.db_path)
    symbols = _load_symbols(config)
    result = rebalance_llm_bot(config, symbols)
    if result.orders:
        log_trades(config.db_path, result.orders, bot_name=LLM_BOT_NAME)
    log_decision_run(
        config.db_path,
        result.ts,
        float(result.decision_context.get("effective_leverage", 0.0)),
        float(result.decision_context.get("spy_vol", 0.0)),
        json.dumps(result.decision_context),
        bot_name=LLM_BOT_NAME,
    )
    log_decision_logs(
        config.db_path,
        result.ts,
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
            for signal in result.signals
        ],
        bot_name=LLM_BOT_NAME,
    )
    log_signals(
        config.db_path,
        result.ts,
        [(s.symbol, s.score, s.side) for s in result.signals],
        bot_name=LLM_BOT_NAME,
    )
    ts_pos, positions = snapshot_positions(config, bot_name=LLM_BOT_NAME)
    log_positions(config.db_path, ts_pos, positions, bot_name=LLM_BOT_NAME)
    spy_value = fetch_latest_close(config, "SPY", bot_name=LLM_BOT_NAME)
    ts_eq, equity, cash, port = snapshot_equity(config, bot_name=LLM_BOT_NAME)
    log_equity(config.db_path, ts_eq, equity, cash, port, spy_value=spy_value, bot_name=LLM_BOT_NAME)
    print(f"LLM rebalanced at {result.ts} with {len(result.orders)} orders.")


def cmd_snapshot_llm(args: argparse.Namespace) -> None:
    _cmd_snapshot_for_bot(LLM_BOT_NAME)


def cmd_dashboard(args: argparse.Namespace) -> None:
    config = load_config()
    init_db(config.db_path)
    launch_dashboard(config.db_path)


def cmd_dashboard_web(args: argparse.Namespace) -> None:
    config = load_config()
    init_db(config.db_path)
    app = create_app(config.db_path, config=config)
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
        bot_name=ML_BOT_NAME,
    )

    if config.advisor_auto_apply and report.overrides:
        save_overrides(config.advisor_overrides_path, report.overrides)
        print(f"Advisor applied overrides to {config.advisor_overrides_path}.")
    else:
        print("Advisor report generated (no overrides applied).")


def cmd_review_decisions(args: argparse.Namespace) -> None:
    config = load_config()
    init_db(config.db_path)
    report = review_and_learn(config, bot_name=ML_BOT_NAME)
    print(f"{report.headline}: {report.summary}")
    if report.report_path:
        print(f"Saved report to {report.report_path}")


def cmd_review_decisions_llm(args: argparse.Namespace) -> None:
    config = load_config()
    init_db(config.db_path)
    report = generate_llm_coach_report(config)
    print(f"{report['headline']}: {report['summary']}")


def cmd_strategy_report(args: argparse.Namespace) -> None:
    config = load_config()
    init_db(config.db_path)
    report = generate_strategy_report(config, bot_name=ML_BOT_NAME)
    print(f"{report.headline}: {report.summary}")
    print(f"Saved report to {report.report_path}")


def cmd_strategy_report_llm(args: argparse.Namespace) -> None:
    config = load_config()
    init_db(config.db_path)
    print(generate_llm_bot_status_report(config))


def cmd_options_report(args: argparse.Namespace) -> None:
    config = load_config()
    init_db(config.db_path)
    symbols = _load_symbols(config)
    report = generate_options_scaffold_report(config, symbols)
    print(f"{report.headline}: {report.summary}")
    print(f"Saved report to {report.report_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Broker Bot - Paper Trading")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-db")
    subparsers.add_parser("doctor")
    subparsers.add_parser("train")
    subparsers.add_parser("backtest")
    subparsers.add_parser("rebalance")
    subparsers.add_parser("rebalance-llm")
    subparsers.add_parser("snapshot")
    subparsers.add_parser("snapshot-llm")
    subparsers.add_parser("caretaker")
    subparsers.add_parser("caretaker-llm")
    subparsers.add_parser("caretaker-all")
    subparsers.add_parser("dashboard")
    subparsers.add_parser("dashboard-web")
    subparsers.add_parser("advisor-report")
    subparsers.add_parser("review-decisions")
    subparsers.add_parser("review-decisions-llm")
    subparsers.add_parser("strategy-report")
    subparsers.add_parser("strategy-report-llm")
    subparsers.add_parser("options-report")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "init-db":
            cmd_init_db(args)
        elif args.command == "doctor":
            cmd_doctor(args)
        elif args.command == "train":
            cmd_train(args)
        elif args.command == "backtest":
            cmd_backtest(args)
        elif args.command == "rebalance":
            cmd_rebalance(args)
        elif args.command == "rebalance-llm":
            cmd_rebalance_llm(args)
        elif args.command == "snapshot":
            cmd_snapshot(args)
        elif args.command == "snapshot-llm":
            cmd_snapshot_llm(args)
        elif args.command == "caretaker":
            cmd_caretaker(args)
        elif args.command == "caretaker-llm":
            cmd_caretaker_llm(args)
        elif args.command == "caretaker-all":
            cmd_caretaker_all(args)
        elif args.command == "dashboard":
            cmd_dashboard(args)
        elif args.command == "dashboard-web":
            cmd_dashboard_web(args)
        elif args.command == "advisor-report":
            cmd_advisor(args)
        elif args.command == "review-decisions":
            cmd_review_decisions(args)
        elif args.command == "review-decisions-llm":
            cmd_review_decisions_llm(args)
        elif args.command == "strategy-report":
            cmd_strategy_report(args)
        elif args.command == "strategy-report-llm":
            cmd_strategy_report_llm(args)
        elif args.command == "options-report":
            cmd_options_report(args)
    except RuntimeError as exc:
        if os.getenv("BROKER_BOT_DEBUG", "").strip().lower() in {"1", "true", "yes", "y"}:
            raise
        raise SystemExit(f"Error: {exc}") from None


if __name__ == "__main__":
    main()
