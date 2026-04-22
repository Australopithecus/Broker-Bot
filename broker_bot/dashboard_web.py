from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
import json
import os

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from .bots import ML_BOT_NAME, bot_label, normalize_bot_name
from .config import Config, configured_bot_names
from .logging_db import (
    read_available_bot_names,
    read_latest_advisor_reports,
    read_latest_equity,
    read_latest_positions,
    read_latest_strategy_reports,
    read_latest_trades,
    read_recent_selected_decisions,
)
from .trader import snapshot_positions_with_protection


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
        data = [{"name": bot_name, "label": bot_label(bot_name)} for bot_name in sorted(discovered)]
        return JSONResponse({"data": data})

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
                    "protection_summary": "Snapshot-only mode; no live Alpaca protection check.",
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
        rows = read_latest_strategy_reports(db_path, limit=20, bot_name=bot_name)
        data = []
        for row in rows:
            data.append(
                {
                    "ts": row[0],
                    "report_type": row[1],
                    "headline": row[2],
                    "summary": row[3],
                    "body": row[4],
                    "metrics": json.loads(row[5]) if row[5] else {},
                    "changes": json.loads(row[6]) if row[6] else {},
                }
            )
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
      --muted: #9ca3af;
      --text: #e5e7eb;
      --accent: #22d3ee;
      --accent-2: #a78bfa;
      --green: #34d399;
      --red: #f87171;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Avenir", "Gill Sans", "Helvetica Neue", sans-serif;
      background: radial-gradient(circle at top, #172554, var(--bg));
      color: var(--text);
      min-height: 100vh;
      display: flex;
      align-items: stretch;
      justify-content: center;
      padding: 24px;
    }
    .container {
      width: min(1100px, 100%);
      display: grid;
      grid-template-rows: auto auto 1fr;
      gap: 20px;
    }
    header {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    header h1 {
      margin: 0;
      font-size: 28px;
      letter-spacing: 0.5px;
    }
    header p { margin: 0; color: var(--muted); }

    .summary {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
    }
    .card {
      background: linear-gradient(145deg, #111827, #0f172a);
      border: 1px solid #1f2937;
      padding: 14px 16px;
      border-radius: 14px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .card h3 { margin: 0; font-size: 12px; color: var(--muted); letter-spacing: 0.8px; text-transform: uppercase; }
    .card .value { margin-top: 6px; font-size: 20px; font-weight: 600; }

    .grid {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 16px;
      align-items: stretch;
    }

    .panel {
      background: var(--panel);
      border: 1px solid #1f2937;
      border-radius: 18px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .panel h2 { margin: 0; font-size: 16px; color: var(--text); }

    canvas { width: 100%; height: 240px; }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
    }
    th, td {
      text-align: left;
      padding: 6px 8px;
      border-bottom: 1px solid #1f2937;
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

    @media (max-width: 900px) {
      .summary { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Broker Bot Dashboard</h1>
      <p>Local paper-trading monitor • Auto-refreshes every 10s • Selector controls the detail panels, while the main chart compares all bots together.</p>
      <label class="muted" for="botSelector">Bot</label>
      <select id="botSelector" style="width: 180px; padding: 6px 8px; border-radius: 10px; background: #0f172a; color: #e5e7eb; border: 1px solid #1f2937;"></select>
    </header>

    <section class="summary">
      <div class="card"><h3>Equity</h3><div class="value" id="equity">--</div></div>
      <div class="card"><h3>Cash</h3><div class="value" id="cash">--</div></div>
      <div class="card"><h3>Portfolio</h3><div class="value" id="portfolio">--</div></div>
      <div class="card"><h3>SPY Close</h3><div class="value" id="spy">--</div></div>
      <div class="card"><h3>Alpha 20D</h3><div class="value" id="alpha20">--</div></div>
      <div class="card"><h3>Tracking Error</h3><div class="value" id="trackErr">--</div></div>
    </section>

    <section class="grid">
      <div class="panel">
        <h2>Bot Performance Comparison</h2>
        <canvas id="equityChart" width="900" height="240"></canvas>
        <div class="muted" id="equityHint"></div>
      </div>
      <div class="panel">
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
      </div>
    </section>

    <section class="panel">
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

    <section class="panel">
      <h2>Advisor Reports</h2>
      <div id="advisorReports" class="muted">No reports yet.</div>
    </section>

    <section class="panel">
      <h2>Strategy Reports</h2>
      <div id="strategyReports" class="muted">No reports yet.</div>
    </section>

    <section class="panel">
      <h2>Recent Decisions</h2>
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
const stdev = (arr) => {
  if (!arr.length || arr.length < 2) return 0;
  const mean = arr.reduce((a, b) => a + b, 0) / arr.length;
  const variance = arr.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / (arr.length - 1);
  return Math.sqrt(variance);
};

const tokenParam = new URLSearchParams(window.location.search).get('token');
const apiHeaders = tokenParam ? { 'X-API-Token': tokenParam } : {};
let currentBot = 'ml';
let availableBots = [];
const apiPathForBot = (path, botName) => {
  const join = path.includes('?') ? '&' : '?';
  return `${path}${join}bot=${encodeURIComponent(botName)}`;
};
const apiPath = (path) => apiPathForBot(path, currentBot);

const normalizeSeries = (points, valueKey) => {
  const clean = (points || [])
    .map(point => ({
      ts: Number(new Date(point.ts)),
      value: Number(point[valueKey]),
    }))
    .filter(point => Number.isFinite(point.ts) && Number.isFinite(point.value))
    .sort((a, b) => a.ts - b.ts);
  if (!clean.length) return [];
  const base = clean[0].value;
  if (!Number.isFinite(base) || base === 0) return [];
  return clean.map(point => ({
    x: point.ts,
    y: (point.value / base) * 100,
    raw: point.value,
  }));
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

  const selectedCurve = botCurves.find(bot => bot.name === currentBot) || botCurves[0];
  const secondaryPalette = [
    { color: '#34d399', label: 'Green' },
    { color: '#f59e0b', label: 'Amber' },
    { color: '#f472b6', label: 'Pink' },
    { color: '#60a5fa', label: 'Blue' },
  ];
  let paletteIndex = 0;
  const equitySeries = botCurves.map(bot => {
    const normalized = normalizeSeries(bot.points, 'equity');
    if (bot.name === currentBot) {
      return {
        ...bot,
        normalized,
        color: '#22d3ee',
        colorLabel: 'Cyan',
        lineWidth: 3,
      };
    }
    const palette = secondaryPalette[paletteIndex % secondaryPalette.length];
    paletteIndex += 1;
    return {
      ...bot,
      normalized,
      color: palette.color,
      colorLabel: palette.label,
      lineWidth: 2,
    };
  }).filter(bot => bot.normalized.length >= 2);

  const spySeries = selectedCurve ? normalizeSeries(selectedCurve.points, 'spy') : [];
  const canvas = document.getElementById('equityChart');
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  if (!equitySeries.length) {
    ctx.fillStyle = '#94a3b8';
    ctx.font = '14px Helvetica';
    ctx.fillText('No equity history yet.', 20, 30);
    document.getElementById('equityHint').textContent = '';
    document.getElementById('alpha20').textContent = '--';
    document.getElementById('trackErr').textContent = '--';
    return;
  }

  const allLines = equitySeries.map(bot => ({
    label: bot.label,
    color: bot.color,
    colorLabel: bot.colorLabel,
    lineWidth: bot.lineWidth,
    points: bot.normalized,
  }));
  if (spySeries.length >= 2) {
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
  const xMin = Math.min(...xValues);
  const xMax = Math.max(...xValues);
  const pad = 20;
  const yPad = Math.max((max - min) * 0.12, 2);
  const scaleX = (value) => pad + (canvas.width - pad * 2) * ((value - xMin) / (xMax - xMin || 1));
  const scaleY = (value) => canvas.height - pad - (canvas.height - pad * 2) * ((value - (min - yPad)) / ((max - min) + yPad * 2 || 1));

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

  const legend = allLines.map(line => `${line.colorLabel}: ${line.label}`).join(' • ');
  document.getElementById('equityHint').textContent = `Normalized to 100 at each bot's first snapshot • Range: ${min.toFixed(1)} to ${max.toFixed(1)} • ${legend}`;

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

async function loadPositions() {
  const res = await fetch(apiPath('/api/positions'), { headers: apiHeaders });
  const data = await res.json();
  const body = document.getElementById('positionsBody');
  body.innerHTML = '';
  (data.data || []).forEach(row => {
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
  const featuredTypes = new Set(['watchlist', 'options_scaffold']);
  reports.filter(report => featuredTypes.has(report.report_type)).slice(0, 2).forEach(report => {
    const div = document.createElement('div');
    div.className = 'card';
    div.style.marginBottom = '10px';
    div.innerHTML = `
      <strong>${report.headline}</strong> <span class="muted">(${report.ts})</span><br />
      ${report.summary}<br />
      <span class="muted">Type: ${report.report_type}</span><br />
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
      <span class="muted">Type: ${report.report_type}${changes.length ? ` • Changes: ${changes.join(', ')}` : ''}</span>
    `;
    container.appendChild(div);
  });
}

async function loadDecisions() {
  const res = await fetch(apiPath('/api/decisions?limit=40'), { headers: apiHeaders });
  const data = await res.json();
  const body = document.getElementById('decisionsBody');
  body.innerHTML = '';
  (data.data || []).forEach(row => {
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
}

async function refreshAll() {
  await Promise.all([loadSummary(), loadEquity(), loadPositions(), loadTrades(), loadAdvisor(), loadStrategy(), loadDecisions()]);
}

loadBots().then(refreshAll);
setInterval(refreshAll, 10000);
</script>
</body>
</html>"""
