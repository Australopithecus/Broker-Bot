from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import json
import os

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from .bot_blueprint import get_strategy_blueprint
from .bots import ML_BOT_NAME, bot_label, normalize_bot_name
from .config import Config, configured_bot_names
from .dashboard_metrics import WINDOW_OPTIONS, agreement_summary, comparison_table, freshness_status
from .logging_db import (
    read_available_bot_names,
    read_latest_advisor_reports,
    read_latest_equity,
    read_latest_positions,
    read_latest_strategy_reports,
    read_latest_trades,
    read_recent_selected_decisions,
)
from .model_revisions import apply_model_revision, model_revision
from .trader import snapshot_positions_with_protection


def _strategy_report_dicts(rows: list[tuple]) -> list[dict[str, Any]]:
    return [
        {
            "ts": row[0],
            "report_type": row[1],
            "headline": row[2],
            "summary": row[3],
            "body": row[4],
            "metrics": json.loads(row[5]) if row[5] else {},
            "changes": json.loads(row[6]) if row[6] else {},
        }
        for row in rows
    ]


def create_app(db_path: str, config: Config | None = None) -> FastAPI:
    app = FastAPI(title="Broker Bot Dashboard")
    api_token = os.getenv("API_TOKEN", "").strip()
    known_bots = configured_bot_names(config) if config is not None else [ML_BOT_NAME]

    def _check_token(request: Request) -> None:
        if not api_token:
            return
        header_token = request.headers.get("X-API-Token")
        query_token = request.query_params.get("token")
        if header_token == api_token or query_token == api_token:
            return
        raise HTTPException(status_code=401, detail="Unauthorized")

    def _bot_name(request: Request) -> str:
        return normalize_bot_name(request.query_params.get("bot", ML_BOT_NAME))

    @app.get("/api/bots")
    def bots(request: Request) -> JSONResponse:
        _check_token(request)
        discovered = set(known_bots)
        try:
            discovered.update(read_available_bot_names(db_path))
        except Exception:
            pass
        data = []
        for bot_name in sorted(discovered):
            try:
                reports = _strategy_report_dicts(read_latest_strategy_reports(db_path, limit=20, bot_name=bot_name))
            except Exception:
                reports = []
            revision = model_revision(bot_name, reports)
            data.append(
                {
                    "name": bot_name,
                    "label": revision["display_label"],
                    "base_label": revision["base_label"],
                    "revision": revision,
                }
            )
        return JSONResponse({"data": data})

    @app.get("/api/blueprint")
    def blueprint(request: Request) -> JSONResponse:
        _check_token(request)
        return JSONResponse(get_strategy_blueprint())

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return _dashboard_html()

    @app.get("/api/summary")
    def summary(request: Request) -> JSONResponse:
        _check_token(request)
        bot_name = _bot_name(request)
        rows = read_latest_equity(db_path, limit=1, bot_name=bot_name)
        if not rows:
            return JSONResponse(
                {
                    "status": "empty",
                    "message": f"No {bot_label(bot_name)} equity snapshots yet. Run the bot to log data.",
                }
            )
        ts, equity, cash, portfolio, spy_value = rows[0]
        return JSONResponse(
            {
                "status": "ok",
                "bot_name": bot_name,
                "bot_label": bot_label(bot_name),
                "ts": ts,
                "equity": equity,
                "cash": cash,
                "portfolio": portfolio,
                "spy": spy_value,
            }
        )

    @app.get("/api/equity")
    def equity(request: Request) -> JSONResponse:
        _check_token(request)
        bot_name = _bot_name(request)
        try:
            limit = int(request.query_params.get("limit", "1000"))
        except ValueError:
            limit = 1000
        limit = max(1, min(limit, 5000))
        rows = read_latest_equity(db_path, limit=limit, bot_name=bot_name)
        rows = list(reversed(rows))
        data = [
            {
                "ts": row[0],
                "equity": row[1],
                "portfolio_value": row[3],
                "spy": row[4],
            }
            for row in rows
        ]
        return JSONResponse({"data": data})

    @app.get("/api/positions")
    def positions(request: Request) -> JSONResponse:
        _check_token(request)
        bot_name = _bot_name(request)
        data = []
        if config is not None:
            try:
                _, data = snapshot_positions_with_protection(config, bot_name=bot_name)
            except Exception:
                data = []
        if not data:
            rows = read_latest_positions(db_path, limit=200, bot_name=bot_name)
            data = [
                {
                    "symbol": row[0],
                    "qty": row[1],
                    "avg_entry": row[2],
                    "avg_entry_price": row[2],
                    "market_value": row[3],
                    "unreal_pl": row[4],
                    "unrealized_pl": row[4],
                    "protection_mode": "Unknown",
                    "protection_summary": "Snapshot-only mode; no live brokerage-service protection check.",
                    "take_profit_price": None,
                    "stop_price": None,
                    "trailing_stop": None,
                    "open_exit_order_count": 0,
                }
                for row in rows
            ]
        return JSONResponse({"data": data})

    @app.get("/api/trades")
    def trades(request: Request) -> JSONResponse:
        _check_token(request)
        bot_name = _bot_name(request)
        rows = read_latest_trades(db_path, limit=200, bot_name=bot_name)
        data = [
            {
                "ts": row[0],
                "symbol": row[1],
                "side": row[2],
                "qty": row[3],
                "price": row[4],
                "status": row[5],
            }
            for row in rows
        ]
        return JSONResponse({"data": data})

    @app.get("/api/advisor")
    def advisor(request: Request) -> JSONResponse:
        _check_token(request)
        bot_name = _bot_name(request)
        rows = read_latest_advisor_reports(db_path, limit=10, bot_name=bot_name)
        data = []
        for row in rows:
            data.append(
                {
                    "ts": row[0],
                    "headline": row[1],
                    "summary": row[2],
                    "suggestions": json.loads(row[3]) if row[3] else [],
                    "metrics": json.loads(row[4]) if row[4] else {},
                    "overrides": json.loads(row[5]) if row[5] else {},
                }
            )
        return JSONResponse({"data": data})

    @app.get("/api/strategy")
    def strategy(request: Request) -> JSONResponse:
        _check_token(request)
        bot_name = _bot_name(request)
        rows = read_latest_strategy_reports(db_path, limit=80, bot_name=bot_name)
        data = _strategy_report_dicts(rows)
        return JSONResponse({"data": data})

    @app.get("/api/decisions")
    def decisions(request: Request) -> JSONResponse:
        _check_token(request)
        bot_name = _bot_name(request)
        try:
            limit = int(request.query_params.get("limit", "50"))
        except ValueError:
            limit = 50
        limit = max(1, min(limit, 300))
        rows = read_recent_selected_decisions(db_path, limit=limit, bot_name=bot_name)
        data = []
        for row in rows:
            data.append(
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
            )
        return JSONResponse({"data": data})

    @app.get("/api/health")
    def health(request: Request) -> JSONResponse:
        _check_token(request)
        discovered = set(known_bots)
        try:
            discovered.update(read_available_bot_names(db_path))
        except Exception:
            pass
        bots_payload = {}
        latest_ts = None
        for bot_name in sorted(discovered):
            equity_rows = list(reversed(read_latest_equity(db_path, limit=365, bot_name=bot_name)))
            trades_rows = read_latest_trades(db_path, limit=1000, bot_name=bot_name)
            decision_rows = read_recent_selected_decisions(db_path, limit=150, bot_name=bot_name)
            positions_rows = read_latest_positions(db_path, limit=500, bot_name=bot_name)
            strategy_reports = _strategy_report_dicts(read_latest_strategy_reports(db_path, limit=30, bot_name=bot_name))
            payload = {
                "label": bot_label(bot_name),
                "base_label": bot_label(bot_name),
                "equity": [
                    {"ts": row[0], "equity": row[1], "cash": row[2], "portfolio_value": row[3], "spy_value": row[4]}
                    for row in equity_rows
                ],
                "trades": [
                    {"ts": row[0], "symbol": row[1], "side": row[2], "qty": row[3], "price": row[4], "status": row[5]}
                    for row in trades_rows
                ],
                "positions": [
                    {"symbol": row[0], "qty": row[1], "avg_entry": row[2], "market_value": row[3], "unreal_pl": row[4]}
                    for row in positions_rows
                ],
                "strategy_reports": strategy_reports,
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
            payload = apply_model_revision(bot_name, payload)
            bots_payload[bot_name] = payload
            if equity_rows:
                ts = equity_rows[-1][0]
                latest_ts = ts if latest_ts is None or ts > latest_ts else latest_ts
        generated_at = datetime.now(timezone.utc).isoformat()
        return JSONResponse(
            {
                "generated_at": generated_at,
                "freshness": freshness_status(latest_ts),
                "comparison": {
                    key: comparison_table(bots_payload, window_key=key)
                    for key in WINDOW_OPTIONS
                },
                "agreement": agreement_summary(bots_payload),
            }
        )

    return app


def _dashboard_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Broker Bot Dashboard</title>
  <style>
    :root {
      --bg: #0b1020;
      --panel: #111827;
      --panel-soft: #0f172a;
      --border: #1f2937;
      --muted: #9ca3af;
      --text: #e5e7eb;
      --accent: #22d3ee;
      --accent-2: #a78bfa;
      --green: #34d399;
      --red: #f87171;
      --radius: 16px;
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      font-family: "Avenir Next", "Avenir", "Gill Sans", "Helvetica Neue", sans-serif;
      font-size: 14px;
      line-height: 1.45;
      background: radial-gradient(circle at top, #172554, var(--bg));
      color: var(--text);
      min-height: 100vh;
      padding: 0;
    }
    .app-shell {
      width: min(1440px, 100%);
      margin: 0 auto;
      display: grid;
      grid-template-columns: 260px minmax(0, 1fr);
      gap: 18px;
      padding: 18px;
      align-items: start;
    }
    .sidebar {
      position: sticky;
      top: 18px;
      min-height: calc(100vh - 36px);
      background: rgba(15, 23, 42, 0.88);
      border: 1px solid rgba(148, 163, 184, 0.24);
      border-radius: 20px;
      box-shadow: 0 18px 46px rgba(0,0,0,0.28);
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .sidebar h1 {
      margin: 2px 0 4px;
      font-size: 24px;
      letter-spacing: -0.04em;
    }
    .sidebar p {
      margin: 0;
      color: var(--muted);
      font-size: 13px;
    }
    .eyebrow {
      color: var(--accent);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
    }
    .sidebar-block {
      display: grid;
      gap: 6px;
    }
    .control {
      width: 100%;
      padding: 8px 10px;
      border-radius: 10px;
      background: #0b1223;
      color: var(--text);
      border: 1px solid var(--border);
      font: inherit;
    }
    .sidebar-status {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }
    .sidebar-status div {
      border: 1px solid rgba(148, 163, 184, 0.18);
      border-radius: 12px;
      padding: 8px;
      background: rgba(255,255,255,0.03);
    }
    .sidebar-status span {
      display: block;
      color: var(--muted);
      font-size: 10px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }
    .sidebar-status strong {
      display: block;
      margin-top: 2px;
      font-size: 13px;
      color: var(--text);
      word-break: break-word;
    }
    .sidebar-nav {
      display: grid;
      gap: 6px;
    }
    .sidebar-nav a {
      color: var(--text);
      text-decoration: none;
      border: 1px solid transparent;
      border-radius: 11px;
      padding: 8px 10px;
      background: rgba(255,255,255,0.025);
      transition: border-color 120ms ease, background 120ms ease, transform 120ms ease;
    }
    .sidebar-nav a:hover {
      border-color: rgba(34, 211, 238, 0.45);
      background: rgba(34, 211, 238, 0.09);
      transform: translateX(2px);
    }
    .container {
      width: min(1180px, 100%);
      display: grid;
      grid-template-rows: auto auto 1fr;
      gap: 14px;
    }
    header {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    header h1 {
      margin: 0;
      font-size: clamp(24px, 3vw, 32px);
      letter-spacing: -0.03em;
    }
    header p { margin: 0; color: var(--muted); max-width: 760px; }
    section, header { scroll-margin-top: 18px; }

    .summary {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 10px;
    }
    .card {
      background: linear-gradient(145deg, #111827, #0f172a);
      border: 1px solid var(--border);
      padding: 12px 14px;
      border-radius: 14px;
      box-shadow: 0 8px 22px rgba(0,0,0,0.22);
    }
    .card h3 { margin: 0; font-size: 11px; color: var(--muted); letter-spacing: 0.08em; text-transform: uppercase; }
    .card .value { margin-top: 4px; font-size: 18px; font-weight: 650; letter-spacing: -0.02em; }

    .grid {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 12px;
      align-items: stretch;
    }
    .cards { grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }

    .panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .panel h2 { margin: 0; font-size: 16px; color: var(--text); letter-spacing: -0.01em; }
    .panel h3 { margin: 10px 0 4px; font-size: 13px; color: var(--text); }
    .panel p { margin: 0; max-width: 900px; }
    .panel ul { margin: 6px 0 0 18px; padding: 0; }
    .panel li { margin: 3px 0; }
    details { border-top: 1px solid var(--border); padding-top: 8px; }
    summary { cursor: pointer; color: var(--text); font-weight: 650; }

    canvas { width: 100%; height: 240px; }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
    }
    th, td {
      text-align: left;
      padding: 6px 8px;
      border-bottom: 1px solid var(--border);
    }
    th { color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }

    .pill {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 600;
    }
    .buy { background: rgba(52, 211, 153, 0.2); color: var(--green); }
    .sell { background: rgba(248, 113, 113, 0.2); color: var(--red); }

    .muted { color: var(--muted); }
    .decision-rationale {
      max-width: 520px;
      white-space: normal;
      line-height: 1.4;
    }
    .stack {
      display: grid;
      gap: 10px;
    }
    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }
    .inline-controls {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }
    .choice-row {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }
    .choice-row label {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 12px;
      color: var(--muted);
    }

    @media (max-width: 980px) {
      .app-shell { grid-template-columns: 1fr; }
      .sidebar {
        position: relative;
        top: auto;
        min-height: 0;
      }
      .sidebar-nav { grid-template-columns: repeat(auto-fit, minmax(132px, 1fr)); }
      .sidebar-nav a:hover { transform: none; }
      .summary { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="app-shell">
    <aside class="sidebar" aria-label="Dashboard navigation">
      <div>
        <div class="eyebrow">Paper Trading Lab</div>
        <h1>Broker Bot</h1>
        <p>Two competing paper-trading systems, one cleaner cockpit.</p>
      </div>
      <div class="sidebar-block">
        <label class="muted" for="botSelector">Active bot</label>
        <select id="botSelector" class="control"></select>
      </div>
      <div class="sidebar-status">
        <div><span>Bot Behavior Revision</span><strong id="sidebarRevision">--</strong></div>
        <div><span>Data</span><strong id="sidebarFreshness">--</strong></div>
      </div>
      <nav class="sidebar-nav">
        <a href="#overview">Overview</a>
        <a href="#blueprint">Blueprint</a>
        <a href="#performance">Performance</a>
        <a href="#holdings">Holdings</a>
        <a href="#comparison">Comparison</a>
        <a href="#champion">Champion Lab</a>
        <a href="#risk">Risk</a>
        <a href="#positions">Positions</a>
        <a href="#trades">Trades</a>
        <a href="#reports">Reports</a>
        <a href="#decisions">Decisions</a>
      </nav>
    </aside>

    <main class="container">
    <header id="overview">
      <div class="eyebrow">Dashboard Cockpit</div>
      <h1>Broker Bot Dashboard</h1>
      <p>Local paper-trading cockpit • Auto-refreshes every 10s • The chart compares bot performance while the panels explain health, risk, decisions, and reports.</p>
    </header>

    <section class="summary" aria-label="System overview">
      <div class="card"><h3>Data Freshness</h3><div class="value" id="freshness">--</div></div>
      <div class="card"><h3>Source</h3><div class="value">Local API</div></div>
      <div class="card"><h3>Models Seen</h3><div class="value" id="botsSeen">--</div></div>
      <div class="card"><h3>Agreement</h3><div class="value" id="agreementRate">--</div></div>
    </section>

    <section class="panel" id="blueprint">
      <h2>Strategy Blueprint</h2>
      <div id="strategyBlueprintBox" class="muted">Loading strategy revision...</div>
    </section>

    <section class="summary" id="account">
      <div class="card"><h3>Equity</h3><div class="value" id="equity">--</div></div>
      <div class="card"><h3>Cash</h3><div class="value" id="cash">--</div></div>
      <div class="card"><h3>Portfolio</h3><div class="value" id="portfolio">--</div></div>
      <div class="card"><h3>SPY Close</h3><div class="value" id="spy">--</div></div>
      <div class="card"><h3>Alpha 20D</h3><div class="value" id="alpha20">--</div></div>
      <div class="card"><h3>Tracking Error</h3><div class="value" id="trackErr">--</div></div>
      <div class="card"><h3>Window Return</h3><div class="value" id="windowRet">--</div></div>
      <div class="card"><h3>Max Drawdown</h3><div class="value" id="maxDd">--</div></div>
      <div class="card"><h3>Win Rate</h3><div class="value" id="winRate">--</div></div>
      <div class="card"><h3>Gross Exposure</h3><div class="value" id="grossExposure">--</div></div>
    </section>

    <section class="grid" aria-label="Performance and holdings">
      <div class="panel" id="performance">
        <div class="panel-header">
          <h2>Model Performance Comparison</h2>
          <div class="inline-controls">
            <div class="choice-row" id="displaySelector"></div>
            <label class="muted" for="graphModeSelector">Scale
              <select id="graphModeSelector" class="control" style="margin-left: 8px; width: auto;">
                <option value="indexed" selected>Indexed performance</option>
                <option value="actual">Actual holding value</option>
              </select>
            </label>
            <label class="muted" for="rangeSelector">Window
              <select id="rangeSelector" class="control" style="margin-left: 8px; width: auto;">
                <option value="24h">24h</option>
                <option value="7d" selected>7d</option>
                <option value="14d">14d</option>
                <option value="28d">28d</option>
                <option value="90d">90d</option>
                <option value="180d">180d</option>
                <option value="360d">360d</option>
              </select>
            </label>
          </div>
        </div>
        <canvas id="equityChart" width="900" height="240"></canvas>
        <div class="muted" id="equityHint"></div>
      </div>
      <div class="panel" id="holdings">
        <h2>Current Holdings</h2>
        <canvas id="holdingsChart" width="360" height="240"></canvas>
        <div class="muted" id="holdingsHint"></div>
      </div>
    </section>

    <section class="panel" id="comparison">
      <h2>Model Comparison</h2>
      <table>
        <thead>
          <tr>
            <th>Model</th>
            <th>Revision</th>
            <th>Return</th>
            <th>Vs SPY</th>
            <th>Max DD</th>
            <th>Win Rate</th>
            <th>Gross Exp</th>
            <th>Protected</th>
          </tr>
        </thead>
        <tbody id="comparisonBody"></tbody>
      </table>
      <div class="muted" id="comparisonHint"></div>
    </section>

    <section class="panel" id="champion">
      <h2>Champion / Challenger Lab</h2>
      <p class="muted">Champion is the current live policy. Challenger is a stricter shadow policy tested against historical outcomes before we trust it with more influence.</p>
      <div id="championChallengerBox" class="muted">No Champion/Challenger reports yet.</div>
    </section>

    <section class="panel" id="risk">
      <h2>Risk Cockpit</h2>
      <table>
        <thead>
          <tr>
            <th>Metric</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody id="riskBody"></tbody>
      </table>
    </section>

    <section class="panel" id="positions">
      <h2>Positions</h2>
      <table>
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Qty</th>
            <th>Avg</th>
            <th>Value</th>
            <th>Unreal</th>
            <th>Protection</th>
          </tr>
        </thead>
        <tbody id="positionsBody"></tbody>
      </table>
    </section>

    <section class="panel" id="trades">
      <h2>Recent Trades</h2>
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Symbol</th>
            <th>Side</th>
            <th>Qty</th>
            <th>Price</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody id="tradesBody"></tbody>
      </table>
    </section>

    <section class="panel" id="reports">
      <h2>Advisor Reports</h2>
      <div id="advisorReports" class="muted">No reports yet.</div>
    </section>

    <section class="panel">
      <h2>Strategy Reports</h2>
      <div id="strategyReports" class="muted">No reports yet.</div>
    </section>

    <section class="panel" id="decisions">
      <h2>Recent Decisions</h2>
      <div class="inline-controls">
        <label class="muted" for="decisionSymbol">Symbol
          <input id="decisionSymbol" placeholder="All" style="margin-left: 8px; padding: 6px 8px; border-radius: 10px; background: #0f172a; color: #e5e7eb; border: 1px solid #1f2937; width: 110px;">
        </label>
        <label class="muted" for="decisionOutcome">Outcome
          <select id="decisionOutcome" style="margin-left: 8px; padding: 6px 8px; border-radius: 10px; background: #0f172a; color: #e5e7eb; border: 1px solid #1f2937;">
            <option value="">All</option>
            <option value="pending">Pending</option>
            <option value="win">Win</option>
            <option value="loss">Loss</option>
            <option value="flat">Flat</option>
          </select>
        </label>
      </div>
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Symbol</th>
            <th>Side</th>
            <th>Base</th>
            <th>Final</th>
            <th>Outcome</th>
            <th>Rationale</th>
          </tr>
        </thead>
        <tbody id="decisionsBody"></tbody>
      </table>
    </section>
    </main>
  </div>

<script>
const fmt = (num) => {
  if (num === null || num === undefined) return "--";
  return "$" + Number(num).toLocaleString(undefined, { maximumFractionDigits: 2 });
};
const pct = (num) => {
  if (num === null || num === undefined || Number.isNaN(num)) return "--";
  return (num * 100).toFixed(2) + "%";
};
const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
})[char]);
const stdev = (arr) => {
  if (!arr.length || arr.length < 2) return 0;
  const mean = arr.reduce((a, b) => a + b, 0) / arr.length;
  const variance = arr.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / (arr.length - 1);
  return Math.sqrt(variance);
};

const tokenParam = new URLSearchParams(window.location.search).get('token');
const apiHeaders = tokenParam ? { 'X-API-Token': tokenParam } : {};
let currentBot = 'ml';
let currentRange = '7d';
let currentDisplay = 'both';
let currentGraphMode = 'indexed';
let availableBots = [];
let latestPositions = [];
let latestDecisions = [];
const TREND_CUTOFF_MS = Date.UTC(2026, 3, 23);
const RANGE_WINDOWS_MS = {
  '24h': 24 * 60 * 60 * 1000,
  '7d': 7 * 24 * 60 * 60 * 1000,
  '14d': 14 * 24 * 60 * 60 * 1000,
  '28d': 28 * 24 * 60 * 60 * 1000,
  '90d': 90 * 24 * 60 * 60 * 1000,
  '180d': 180 * 24 * 60 * 60 * 1000,
  '360d': 360 * 24 * 60 * 60 * 1000,
};
const apiPathForBot = (path, botName) => {
  const join = path.includes('?') ? '&' : '?';
  return `${path}${join}bot=${encodeURIComponent(botName)}`;
};
const apiPath = (path) => apiPathForBot(path, currentBot);

const filterSeriesToWindow = (clean, cutoffTs) => {
  if (cutoffTs === null) return clean;
  const before = clean.filter(point => point.ts < cutoffTs);
  const after = clean.filter(point => point.ts >= cutoffTs);
  if (!after.length) return clean.slice(-2);
  return before.length ? [before[before.length - 1], ...after] : after;
};

const cleanSeries = (points, valueKey) => {
  return (points || [])
    .map(point => {
      let value = Number(point[valueKey]);
      if (!Number.isFinite(value) && valueKey !== 'equity') {
        value = Number(point.equity);
      }
      return {
        ts: Number(new Date(point.ts)),
        value,
      };
    })
    .filter(point => Number.isFinite(point.ts) && Number.isFinite(point.value))
    .sort((a, b) => a.ts - b.ts);
};

const applyTrendCutoff = (clean) => clean.filter(point => point.ts >= TREND_CUTOFF_MS);

const normalizeSeries = (clean) => {
  if (!clean.length) return [];
  const base = clean[0].value;
  if (!Number.isFinite(base) || base === 0) return [];
  return clean.map(point => ({
    x: point.ts,
    y: (point.value / base) * 100,
    raw: point.value,
  }));
};

const actualSeries = (clean) => clean.map(point => ({
  x: point.ts,
  y: point.value,
  raw: point.value,
}));

const pctChange = (current, prior) => {
  if (!Number.isFinite(current) || !Number.isFinite(prior) || prior === 0) return null;
  return (current / prior) - 1;
};

const maxDrawdown = (values) => {
  if (!values.length) return 0;
  let peak = values[0];
  let maxDd = 0;
  values.forEach(value => {
    peak = Math.max(peak, value);
    if (peak > 0) maxDd = Math.max(maxDd, (peak - value) / peak);
  });
  return maxDd;
};

const nearestY = (points, ts) => {
  const prior = points.filter(point => point.x <= ts);
  if (prior.length) return prior[prior.length - 1].y;
  return points.length ? points[0].y : null;
};

function setMetric(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

const renderDisplaySelector = () => {
  const container = document.getElementById('displaySelector');
  if (!container) return;
  const options = [{ value: 'both', label: 'Both models' }, ...availableBots.map(bot => ({ value: bot.name, label: bot.label }))];
  if (currentDisplay !== 'both' && !availableBots.some(bot => bot.name === currentDisplay)) {
    currentDisplay = 'both';
  }
  container.innerHTML = '';
  options.forEach(option => {
    const label = document.createElement('label');
    const input = document.createElement('input');
    input.type = 'radio';
    input.name = 'displayMode';
    input.value = option.value;
    input.checked = currentDisplay === option.value;
    input.addEventListener('change', async (event) => {
      currentDisplay = event.target.value || 'both';
      await loadEquity();
    });
    label.appendChild(input);
    label.append(` ${option.label}`);
    container.appendChild(label);
  });
};

async function loadBots() {
  const res = await fetch('/api/bots', { headers: apiHeaders });
  const data = await res.json();
  const selector = document.getElementById('botSelector');
  availableBots = data.data || [];
  selector.innerHTML = '';
  availableBots.forEach(item => {
    const option = document.createElement('option');
    option.value = item.name;
    option.textContent = item.label;
    selector.appendChild(option);
  });
  if (!availableBots.some(item => item.name === currentBot) && availableBots.length) {
    currentBot = availableBots[0].name;
  }
  selector.value = currentBot;
  selector.addEventListener('change', async (event) => {
    currentBot = event.target.value || 'ml';
    await refreshAll();
  });
  renderDisplaySelector();
  const rangeSelector = document.getElementById('rangeSelector');
  rangeSelector.value = currentRange;
  rangeSelector.addEventListener('change', async (event) => {
    currentRange = event.target.value || '7d';
    await Promise.all([loadEquity(), loadHealth()]);
  });
  const graphModeSelector = document.getElementById('graphModeSelector');
  graphModeSelector.value = currentGraphMode;
  graphModeSelector.addEventListener('change', async (event) => {
    currentGraphMode = event.target.value || 'indexed';
    await loadEquity();
  });
  document.getElementById('decisionSymbol')?.addEventListener('input', loadDecisions);
  document.getElementById('decisionOutcome')?.addEventListener('change', loadDecisions);
}

async function loadSummary() {
  const res = await fetch(apiPath('/api/summary'), { headers: apiHeaders });
  const data = await res.json();
  if (data.status !== 'ok') {
    document.getElementById('equity').textContent = '--';
    document.getElementById('cash').textContent = '--';
    document.getElementById('portfolio').textContent = '--';
    document.getElementById('spy').textContent = '--';
    return;
  }
  document.getElementById('equity').textContent = fmt(data.equity);
  document.getElementById('cash').textContent = fmt(data.cash);
  document.getElementById('portfolio').textContent = fmt(data.portfolio);
  document.getElementById('spy').textContent = data.spy ? fmt(data.spy) : '--';
}

async function loadHealth() {
  try {
    const res = await fetch('/api/health', { headers: apiHeaders });
    const data = await res.json();
    const fresh = data.freshness || {};
    setMetric('freshness', fresh.status ? `${fresh.status}` : '--');
    setMetric('sidebarFreshness', fresh.status ? `${fresh.status}` : '--');
    setMetric('botsSeen', String(availableBots.length || 0));
    const agreement = data.agreement || {};
    setMetric('agreementRate', agreement.agreement_rate === null || agreement.agreement_rate === undefined ? '--' : pct(agreement.agreement_rate));

    const rows = ((data.comparison || {})[currentRange] || []);
    const body = document.getElementById('comparisonBody');
    body.innerHTML = '';
    rows.forEach(row => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${row.label || row.bot}</td>
        <td>${[row.behavior_revision, row.revision_name || row.revision_label].filter(Boolean).join(' / ') || '--'}</td>
        <td>${pct(row.window_return)}</td>
        <td>${pct(row.window_alpha)}</td>
        <td>${pct(row.max_drawdown)}</td>
        <td>${pct(row.win_rate)}</td>
        <td>${pct(row.gross_exposure_pct)}</td>
        <td>${pct(row.protection_rate)}</td>
      `;
      body.appendChild(tr);
    });
    const agreements = (agreement.agreements || []).slice(0, 6).join(', ') || 'none';
    const disagreements = (agreement.disagreements || []).slice(0, 6).join(', ') || 'none';
    document.getElementById('comparisonHint').textContent = `Overlap: ${agreement.overlap || 0} • Agreements: ${agreements} • Disagreements: ${disagreements}`;
  } catch (_) {
    setMetric('freshness', '--');
    setMetric('sidebarFreshness', '--');
    setMetric('botsSeen', String(availableBots.length || 0));
  }
}

function renderRisk() {
  const totalValue = latestPositions.reduce((sum, row) => sum + Math.abs(Number(row.market_value || 0)), 0);
  const longValue = latestPositions
    .filter(row => Number(row.market_value || 0) > 0)
    .reduce((sum, row) => sum + Number(row.market_value || 0), 0);
  const shortValue = latestPositions
    .filter(row => Number(row.market_value || 0) < 0)
    .reduce((sum, row) => sum + Math.abs(Number(row.market_value || 0)), 0);
  const protectedCount = latestPositions.filter(row => {
    const mode = String(row.protection_mode || '').toLowerCase();
    return mode && mode !== 'none' && mode !== 'unknown';
  }).length;
  const evaluated = latestDecisions.filter(row => row.signed_return !== null && row.signed_return !== undefined);
  const wins = evaluated.filter(row => Number(row.signed_return) > 0).length;
  document.getElementById('grossExposure').textContent = fmt(totalValue);
  document.getElementById('winRate').textContent = evaluated.length ? pct(wins / evaluated.length) : '--';

  const rows = [
    ['Gross exposure', fmt(totalValue)],
    ['Long exposure', fmt(longValue)],
    ['Short exposure', fmt(shortValue)],
    ['Largest position', fmt(Math.max(0, ...latestPositions.map(row => Math.abs(Number(row.market_value || 0)))))],
    ['Protected positions', `${protectedCount}/${latestPositions.length}`],
    ['Evaluated decisions', String(evaluated.length)],
  ];
  const body = document.getElementById('riskBody');
  body.innerHTML = '';
  rows.forEach(([name, value]) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${name}</td><td>${value}</td>`;
    body.appendChild(tr);
  });
}

async function loadEquity() {
  const botList = availableBots.length ? availableBots : [{ name: currentBot, label: currentBot.toUpperCase() }];
  const botCurves = await Promise.all(botList.map(async (bot, index) => {
    const res = await fetch(apiPathForBot('/api/equity', bot.name), { headers: apiHeaders });
    const data = await res.json();
    return {
      ...bot,
      index,
      points: data.data || [],
    };
  }));

  const visibleCurves = currentDisplay === 'both'
    ? botCurves
    : botCurves.filter(bot => bot.name === currentDisplay);
  const selectedCurve = visibleCurves.find(bot => bot.name === currentBot)
    || visibleCurves[0]
    || botCurves.find(bot => bot.name === currentBot)
    || botCurves[0];
  const valueKey = currentGraphMode === 'actual' ? 'portfolio_value' : 'equity';
  const allTimestamps = botCurves.flatMap(bot => applyTrendCutoff(cleanSeries(bot.points, valueKey)).map(point => point.ts));
  const latestTs = allTimestamps.length ? Math.max(...allTimestamps) : null;
  const windowMs = RANGE_WINDOWS_MS[currentRange] || RANGE_WINDOWS_MS['90d'];
  const cutoffTs = latestTs === null ? null : latestTs - windowMs;
  const secondaryPalette = [
    { color: '#34d399', label: 'Green' },
    { color: '#f59e0b', label: 'Amber' },
    { color: '#f472b6', label: 'Pink' },
    { color: '#60a5fa', label: 'Blue' },
  ];
  let paletteIndex = 0;
  const omittedBots = [];
  const equitySeries = visibleCurves.map(bot => {
    const cleaned = applyTrendCutoff(cleanSeries(bot.points, valueKey));
    const filtered = filterSeriesToWindow(cleaned, cutoffTs);
    const chartPoints = currentGraphMode === 'actual' ? actualSeries(filtered) : normalizeSeries(filtered);
    if (cleaned.length >= 2 && filtered.length < 2) {
      omittedBots.push(bot.label);
    }
    if (bot.name === currentBot) {
      return {
        ...bot,
        normalized: chartPoints,
        color: '#22d3ee',
        colorLabel: 'Cyan',
        lineWidth: 3,
      };
    }
    const palette = secondaryPalette[paletteIndex % secondaryPalette.length];
    paletteIndex += 1;
    return {
      ...bot,
      normalized: chartPoints,
      color: palette.color,
      colorLabel: palette.label,
      lineWidth: 2,
    };
  }).filter(bot => bot.normalized.length >= 2);

  const selectedSpyClean = selectedCurve ? applyTrendCutoff(cleanSeries(selectedCurve.points, 'spy')) : [];
  const selectedSpyFiltered = filterSeriesToWindow(selectedSpyClean, cutoffTs);
  const spySeries = currentGraphMode === 'indexed' ? normalizeSeries(selectedSpyFiltered) : [];
  const canvas = document.getElementById('equityChart');
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  if (!equitySeries.length) {
    ctx.fillStyle = '#94a3b8';
    ctx.font = '14px Helvetica';
    ctx.fillText(`No equity history available for ${currentRange}.`, 20, 30);
    document.getElementById('equityHint').textContent = '';
    document.getElementById('alpha20').textContent = '--';
    document.getElementById('trackErr').textContent = '--';
    document.getElementById('windowRet').textContent = '--';
    document.getElementById('maxDd').textContent = '--';
    return;
  }

  const allLines = equitySeries.map(bot => ({
    label: bot.label,
    color: bot.color,
    colorLabel: bot.colorLabel,
    lineWidth: bot.lineWidth,
    points: bot.normalized,
  }));
  if (currentGraphMode === 'indexed' && spySeries.length >= 2) {
    allLines.push({
      label: `${selectedCurve.label} SPY`,
      color: '#a78bfa',
      colorLabel: 'Purple dashed',
      lineWidth: 2,
      dash: [6, 6],
      points: spySeries,
    });
  }

  const xValues = allLines.flatMap(line => line.points.map(point => point.x));
  const yValues = allLines.flatMap(line => line.points.map(point => point.y));
  const min = Math.min(...yValues);
  const max = Math.max(...yValues);
  const xMin = cutoffTs === null ? Math.min(...xValues) : cutoffTs;
  const xMax = latestTs === null ? Math.max(...xValues) : latestTs;
  const pad = 20;
  const yPad = Math.max((max - min) * 0.08, 0.4);
  const scaleX = (value) => pad + (canvas.width - pad * 2) * ((value - xMin) / (xMax - xMin || 1));
  const scaleY = (value) => canvas.height - pad - (canvas.height - pad * 2) * ((value - (min - yPad)) / ((max - min) + yPad * 2 || 1));
  const selectedClean = selectedCurve ? applyTrendCutoff(cleanSeries(selectedCurve.points, valueKey)) : [];
  const selectedFiltered = filterSeriesToWindow(selectedClean, cutoffTs);
  if (selectedFiltered.length >= 2) {
    const ret = pctChange(selectedFiltered[selectedFiltered.length - 1].value, selectedFiltered[0].value);
    document.getElementById('windowRet').textContent = pct(ret);
    document.getElementById('maxDd').textContent = pct(maxDrawdown(selectedFiltered.map(point => point.value)));
  } else {
    document.getElementById('windowRet').textContent = '--';
    document.getElementById('maxDd').textContent = '--';
  }

  ctx.strokeStyle = 'rgba(148, 163, 184, 0.18)';
  ctx.lineWidth = 1;
  for (let i = 0; i < 4; i++) {
    const y = pad + ((canvas.height - pad * 2) * i) / 3;
    ctx.beginPath();
    ctx.moveTo(pad, y);
    ctx.lineTo(canvas.width - pad, y);
    ctx.stroke();
  }

  allLines.forEach(line => {
    ctx.save();
    ctx.strokeStyle = line.color;
    ctx.lineWidth = line.lineWidth || 2;
    ctx.setLineDash(line.dash || []);
    ctx.beginPath();
    line.points.forEach((point, index) => {
      const x = scaleX(point.x);
      const y = scaleY(point.y);
      if (index === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
    ctx.restore();
  });

  const tradePayloads = await Promise.all(visibleCurves.map(async bot => {
    try {
      const res = await fetch(apiPathForBot('/api/trades', bot.name), { headers: apiHeaders });
      const data = await res.json();
      return { bot, rows: data.data || [] };
    } catch (_) {
      return { bot, rows: [] };
    }
  }));
  const botLineByName = Object.fromEntries(equitySeries.map(bot => [bot.name, bot.normalized]));
  let markerCount = 0;
  tradePayloads.forEach(({ bot, rows }) => {
    const points = botLineByName[bot.name] || [];
    rows.forEach(row => {
      const ts = Number(new Date(row.ts));
      if (!Number.isFinite(ts) || ts < xMin || ts > xMax) return;
      const yValue = nearestY(points, ts);
      if (yValue === null) return;
      const x = scaleX(ts);
      const y = scaleY(yValue);
      const isBuy = String(row.side || '').toLowerCase() === 'buy';
      ctx.fillStyle = isBuy ? '#34d399' : '#f87171';
      ctx.beginPath();
      if (isBuy) {
        ctx.moveTo(x, y - 7);
        ctx.lineTo(x - 6, y + 6);
        ctx.lineTo(x + 6, y + 6);
      } else {
        ctx.moveTo(x, y + 7);
        ctx.lineTo(x - 6, y - 6);
        ctx.lineTo(x + 6, y - 6);
      }
      ctx.closePath();
      ctx.fill();
      markerCount += 1;
    });
  });

  const legend = allLines.map(line => `${line.colorLabel}: ${line.label}`).join(' • ');
  const omittedText = omittedBots.length ? ` • No data in window: ${omittedBots.join(', ')}` : '';
  const xStartLabel = new Date(xMin).toLocaleString();
  const xEndLabel = new Date(xMax).toLocaleString();
  const markerText = markerCount ? ` • Trade markers: ${markerCount}` : '';
  const modeText = currentGraphMode === 'actual'
    ? 'Actual holding value in dollars; SPY is omitted because it is a price, not an account value'
    : 'Normalized to 100 at the start of the selected window';
  const rangeText = currentGraphMode === 'actual'
    ? `${fmt(min)} to ${fmt(max)}`
    : `${min.toFixed(1)} to ${max.toFixed(1)}`;
  document.getElementById('equityHint').textContent = `${currentRange} window (${xStartLabel} to ${xEndLabel}) • ${modeText} • Trend data starts Apr 23, 2026 • Range: ${rangeText} • ${legend}${omittedText}${markerText}`;

  // Alpha + tracking error (20D) if we have SPY values
  const aligned = (selectedCurve?.points || [])
    .map(point => ({
      equity: Number(point.equity),
      spy: Number(point.spy),
      ts: Number(new Date(point.ts)),
    }))
    .filter(point => Number.isFinite(point.ts) && Number.isFinite(point.equity) && Number.isFinite(point.spy))
    .sort((a, b) => a.ts - b.ts);
  if (aligned.length >= 21) {
    const window = aligned.slice(-21);
    const botRet = (window[window.length - 1].equity / window[0].equity) - 1;
    const spyRet = (window[window.length - 1].spy / window[0].spy) - 1;
    const alpha = botRet - spyRet;
    const diffs = [];
    for (let i = 1; i < window.length; i++) {
      const br = (window[i].equity / window[i - 1].equity) - 1;
      const sr = (window[i].spy / window[i - 1].spy) - 1;
      diffs.push(br - sr);
    }
    const te = stdev(diffs);
    document.getElementById('alpha20').textContent = pct(alpha);
    document.getElementById('trackErr').textContent = pct(te);
  } else {
    document.getElementById('alpha20').textContent = '--';
    document.getElementById('trackErr').textContent = '--';
  }
}

function drawHoldingsChart(rows) {
  const canvas = document.getElementById('holdingsChart');
  const hint = document.getElementById('holdingsHint');
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const entries = (rows || [])
    .map(row => ({
      symbol: row.symbol || 'Unknown',
      value: Math.abs(Number(row.market_value || 0)),
      side: Number(row.market_value || 0) < 0 ? 'Short' : 'Long',
    }))
    .filter(row => Number.isFinite(row.value) && row.value > 0)
    .sort((a, b) => b.value - a.value);

  if (!entries.length) {
    ctx.fillStyle = '#94a3b8';
    ctx.font = '14px Helvetica';
    ctx.fillText('No current holdings.', 20, 30);
    hint.textContent = '';
    return;
  }

  const total = entries.reduce((sum, row) => sum + row.value, 0);
  const palette = ['#22d3ee', '#34d399', '#f59e0b', '#f472b6', '#60a5fa', '#f87171', '#c084fc', '#facc15'];
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;
  const outer = Math.min(canvas.width, canvas.height) * 0.38;
  const inner = outer * 0.55;
  let start = -Math.PI / 2;

  entries.forEach((entry, index) => {
    const angle = (entry.value / total) * Math.PI * 2;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, outer, start, start + angle);
    ctx.closePath();
    ctx.fillStyle = palette[index % palette.length];
    ctx.fill();
    start += angle;
  });

  ctx.beginPath();
  ctx.arc(cx, cy, inner, 0, Math.PI * 2);
  ctx.fillStyle = '#111827';
  ctx.fill();

  ctx.fillStyle = '#e5e7eb';
  ctx.textAlign = 'center';
  ctx.font = 'bold 16px Helvetica';
  ctx.fillText(currentBot.toUpperCase(), cx, cy - 8);
  ctx.font = '12px Helvetica';
  ctx.fillStyle = '#9ca3af';
  ctx.fillText(fmt(total), cx, cy + 14);
  ctx.textAlign = 'left';

  const summary = entries
    .slice(0, 5)
    .map(entry => `${entry.symbol}: ${fmt(entry.value)}`)
    .join(' • ');
  const longCount = entries.filter(entry => entry.side === 'Long').length;
  const shortCount = entries.filter(entry => entry.side === 'Short').length;
  hint.textContent = `Top holdings • ${summary} • Long: ${longCount} • Short: ${shortCount}`;
}

async function loadPositions() {
  const res = await fetch(apiPath('/api/positions'), { headers: apiHeaders });
  const data = await res.json();
  const rows = data.data || [];
  latestPositions = rows;
  const body = document.getElementById('positionsBody');
  body.innerHTML = '';
  rows.forEach(row => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${row.symbol}</td>
      <td>${Number(row.qty).toFixed(2)}</td>
      <td>${fmt(row.avg_entry)}</td>
      <td>${fmt(row.market_value)}</td>
      <td>${fmt(row.unreal_pl)}</td>
      <td>${row.protection_mode || 'None'}<br /><span class="muted">${row.protection_summary || ''}</span></td>
    `;
    body.appendChild(tr);
  });
  drawHoldingsChart(rows);
  renderRisk();
}

async function loadTrades() {
  const res = await fetch(apiPath('/api/trades'), { headers: apiHeaders });
  const data = await res.json();
  const body = document.getElementById('tradesBody');
  body.innerHTML = '';
  (data.data || []).forEach(row => {
    const tr = document.createElement('tr');
    const sideClass = row.side === 'buy' ? 'buy' : 'sell';
    tr.innerHTML = `
      <td>${row.ts}</td>
      <td>${row.symbol}</td>
      <td><span class="pill ${sideClass}">${row.side}</span></td>
      <td>${Number(row.qty).toFixed(2)}</td>
      <td>${fmt(row.price)}</td>
      <td>${row.status || ''}</td>
    `;
    body.appendChild(tr);
  });
}

async function loadAdvisor() {
  const res = await fetch(apiPath('/api/advisor'), { headers: apiHeaders });
  const data = await res.json();
  const reports = data.data || [];
  const container = document.getElementById('advisorReports');
  if (!reports.length) {
    container.textContent = 'No reports yet.';
    return;
  }
  container.innerHTML = '';
  reports.slice(0, 5).forEach(report => {
    const div = document.createElement('div');
    div.className = 'card';
    div.style.marginBottom = '10px';
    const suggestions = (report.suggestions || []).map(s => `• ${s}`).join('<br />');
    const overrideKeys = report.overrides ? Object.keys(report.overrides) : [];
    const overrides = overrideKeys.length
      ? `Overrides: ${overrideKeys.map(k => `${k}=${report.overrides[k]}`).join(', ')}`
      : '';
    div.innerHTML = `
      <strong>${report.headline}</strong> <span class="muted">(${report.ts})</span><br />
      ${report.summary}<br />
      <span class="muted">${suggestions}</span><br />
      <span class="muted">${overrides}</span>
    `;
    container.appendChild(div);
  });
}

function renderComponents(components) {
  const entries = Object.entries(components || {})
    .filter(([, value]) => Math.abs(Number(value || 0)) >= 0.0001)
    .sort((a, b) => Math.abs(Number(b[1])) - Math.abs(Number(a[1])));
  if (!entries.length) return '';
  return entries.map(([key, value]) => `${key.replace('_adjustment', '')}: ${Number(value).toFixed(4)}`).join(' • ');
}

function renderTakeaways(body) {
  const items = String(body || '')
    .split('\\n')
    .map(line => line.trim())
    .filter(line => line.startsWith('- ') && line.length > 10)
    .slice(0, 5)
    .map(line => `<li>${line.slice(2)}</li>`)
    .join('');
  return items ? `<ul class="muted">${items}</ul>` : '';
}

async function loadStrategyBlueprint() {
  const res = await fetch('/api/blueprint', { headers: apiHeaders });
  const blueprint = await res.json();
  const container = document.getElementById('strategyBlueprintBox');
  const models = Array.isArray(blueprint.models) ? blueprint.models : [];
  const shared = Array.isArray(blueprint.shared_layers) ? blueprint.shared_layers : [];
  const safety = Array.isArray(blueprint.current_safety_posture) ? blueprint.current_safety_posture : [];
  const changelog = Array.isArray(blueprint.changelog) ? blueprint.changelog : [];
  setMetric('sidebarRevision', blueprint.revision || '--');
  const modelCards = models.map(model => `
    <details style="margin-top: 8px;">
      <summary>${esc(model.name)} - ${esc(model.role)}</summary>
      <p style="margin-top: 6px;">${esc(model.description)}</p>
      <ul>${(model.strategies || []).map(item => `<li>${esc(item)}</li>`).join('')}</ul>
    </details>
  `).join('');
  const changes = changelog.map((entry, index) => `
    <details ${index === 0 ? 'open' : ''} style="margin-top: 10px;">
      <summary><strong>Revision ${esc(entry.revision)}</strong> (${esc(entry.date)}) - ${esc(entry.title)}</summary>
      ${Array.isArray(entry.models) && entry.models.length ? `<p class="muted">Models changed: ${entry.models.map(esc).join(', ')}</p>` : ''}
      <ul>${(entry.changes || []).map(item => `<li>${esc(item)}</li>`).join('')}</ul>
    </details>
  `).join('');
  container.innerHTML = `
    <div class="grid cards">
      <div class="card"><h3>Bot Behavior Revision</h3><div class="value">${esc(blueprint.revision || '--')}</div></div>
      <div class="card"><h3>Updated</h3><div class="value">${esc(blueprint.revision_date || '--')}</div></div>
      <div class="card"><h3>Models</h3><div class="value">${models.length}</div></div>
      <div class="card"><h3>Behavior Changes</h3><div class="value">${changelog.length}</div></div>
    </div>
    <p>${esc(blueprint.summary || '')}</p>
    <details>
      <summary>Models and strategies</summary>
      ${modelCards || '<p class="muted">No model description available.</p>'}
    </details>
    <details>
      <summary>Shared strategy layers</summary>
      <ul>${shared.map(item => `<li>${esc(item)}</li>`).join('')}</ul>
    </details>
    <details>
      <summary>Current safety posture</summary>
      <ul>${safety.map(item => `<li>${esc(item)}</li>`).join('')}</ul>
    </details>
    <details>
      <summary>Bot behavior revision history</summary>
      ${changes || '<p class="muted">No changelog entries available.</p>'}
    </details>
  `;
}

function compactPct(num) {
  if (num === null || num === undefined || Number.isNaN(Number(num))) return '--';
  return `${(Number(num) * 100).toFixed(2)}%`;
}

async function loadChampionChallenger() {
  const res = await fetch(apiPath('/api/strategy'), { headers: apiHeaders });
  const data = await res.json();
  const reports = (data.data || []).filter(report => report.report_type === 'champion_challenger');
  const container = document.getElementById('championChallengerBox');
  if (!reports.length) {
    container.textContent = 'No Champion/Challenger reports yet. The next cloud report run will populate this panel.';
    return;
  }
  const latest = reports[0];
  const metrics = latest.metrics || {};
  const changes = latest.changes || {};
  const implemented = Array.isArray(changes.implemented_changes) ? changes.implemented_changes : [];
  const rows = reports.slice(0, 10).map(report => {
    const m = report.metrics || {};
    const c = report.changes || {};
    return `
      <tr>
        <td>${report.ts || ''}</td>
        <td>${compactPct(m.champion_avg_signed_return)}</td>
        <td>${compactPct(m.challenger_avg_signed_return)}</td>
        <td>${Number(m.champion_samples || 0).toFixed(0)} / ${Number(m.challenger_samples || 0).toFixed(0)}</td>
        <td>${compactPct(m.excluded_avg_signed_return)}</td>
        <td>${c.verdict || report.summary || ''}</td>
      </tr>
    `;
  }).join('');
  const historicalDetails = reports.slice(0, 6).map((report, index) => `
    <details ${index === 0 ? 'open' : ''} style="margin-top: 10px;">
      <summary><strong>${report.ts || 'Report'}</strong> - ${report.summary || ''}</summary>
      <div class="muted" style="white-space: pre-wrap; margin-top: 8px;">${(report.body || '').slice(0, 2600)}</div>
    </details>
  `).join('');
  container.innerHTML = `
    <div class="grid cards">
      <div class="card"><h3>Champion Avg</h3><div class="value">${compactPct(metrics.champion_avg_signed_return)}</div></div>
      <div class="card"><h3>Challenger Avg</h3><div class="value">${compactPct(metrics.challenger_avg_signed_return)}</div></div>
      <div class="card"><h3>Champion Samples</h3><div class="value">${Number(metrics.champion_samples || 0).toFixed(0)}</div></div>
      <div class="card"><h3>Challenger Samples</h3><div class="value">${Number(metrics.challenger_samples || 0).toFixed(0)}</div></div>
    </div>
    <p><strong>Models being tested</strong></p>
    <p>${changes.champion_description || 'Champion: current selected-decision policy.'}</p>
    <p>${changes.challenger_description || 'Challenger: stricter confidence-gated shadow policy.'}</p>
    ${implemented.length ? `<p><strong>Changes implemented</strong></p><ul>${implemented.map(item => `<li>${item}</li>`).join('')}</ul>` : ''}
    <table style="margin-top: 10px;">
      <thead>
        <tr>
          <th>Time</th>
          <th>Champion Avg</th>
          <th>Challenger Avg</th>
          <th>Samples</th>
          <th>Excluded Avg</th>
          <th>Verdict</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
    ${historicalDetails}
  `;
}

async function loadStrategy() {
  const res = await fetch(apiPath('/api/strategy'), { headers: apiHeaders });
  const data = await res.json();
  const reports = data.data || [];
  const container = document.getElementById('strategyReports');
  if (!reports.length) {
    container.textContent = 'No strategy reports yet.';
    return;
  }
  container.innerHTML = '';
  const featuredTypes = new Set(['model_eval', 'watchlist', 'skeptic', 'attribution', 'champion_challenger', 'options_scaffold']);
  reports.filter(report => featuredTypes.has(report.report_type)).slice(0, 3).forEach(report => {
    const div = document.createElement('div');
    div.className = 'card';
    div.style.marginBottom = '10px';
    div.innerHTML = `
      <strong>${report.headline}</strong> <span class="muted">(${report.ts})</span><br />
      ${report.summary}<br />
      <span class="muted">Type: ${report.report_type}</span><br />
      ${renderTakeaways(report.body)}
      <div class="muted" style="white-space: pre-wrap; margin-top: 8px;">${(report.body || '').slice(0, 1600)}</div>
    `;
    container.appendChild(div);
  });
  reports.filter(report => !featuredTypes.has(report.report_type)).slice(0, 4).forEach(report => {
    const div = document.createElement('div');
    div.className = 'card';
    div.style.marginBottom = '10px';
    const changes = report.changes ? Object.keys(report.changes) : [];
    div.innerHTML = `
      <strong>${report.headline}</strong> <span class="muted">(${report.ts})</span><br />
      ${report.summary}<br />
      ${renderTakeaways(report.body)}
      <span class="muted">Type: ${report.report_type}${changes.length ? ` • Changes: ${changes.join(', ')}` : ''}</span>
    `;
    container.appendChild(div);
  });
}

async function loadDecisions() {
  const res = await fetch(apiPath('/api/decisions?limit=40'), { headers: apiHeaders });
  const data = await res.json();
  latestDecisions = data.data || [];
  const body = document.getElementById('decisionsBody');
  body.innerHTML = '';
  const symbolFilter = String(document.getElementById('decisionSymbol')?.value || '').trim().toUpperCase();
  const outcomeFilter = String(document.getElementById('decisionOutcome')?.value || '').trim().toLowerCase();
  latestDecisions
    .filter(row => !symbolFilter || String(row.symbol || '').toUpperCase().includes(symbolFilter))
    .filter(row => !outcomeFilter || String(row.outcome_label || 'pending').toLowerCase() === outcomeFilter)
    .forEach(row => {
    const tr = document.createElement('tr');
    const sideClass = row.side === 'LONG' ? 'buy' : 'sell';
    const outcome = row.outcome_label ? `${row.outcome_label}${row.signed_return !== null && row.signed_return !== undefined ? ` (${pct(row.signed_return)})` : ''}` : '--';
    const extras = renderComponents(row.components);
    tr.innerHTML = `
      <td>${row.ts}</td>
      <td>${row.symbol}</td>
      <td><span class="pill ${sideClass}">${row.side}</span></td>
      <td>${pct(row.base_score)}</td>
      <td>${pct(row.final_score)}</td>
      <td>${outcome}</td>
      <td class="decision-rationale">${row.rationale || ''}${extras ? `<div class="muted">${extras}</div>` : ''}</td>
    `;
    body.appendChild(tr);
  });
  renderRisk();
}

async function refreshAll() {
  await Promise.all([loadSummary(), loadHealth(), loadStrategyBlueprint(), loadEquity(), loadPositions(), loadTrades(), loadAdvisor(), loadChampionChallenger(), loadStrategy(), loadDecisions()]);
}

loadBots().then(refreshAll);
setInterval(refreshAll, 10000);
</script>
</body>
</html>"""
