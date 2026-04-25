# Broker Bot (Paper Trading)

A Python-based paper-trading project for Alpaca paper accounts with two named bots:

- `ML Bot`: the original machine-learning ensemble bot
- `LLM Bot`: a second bot that uses a network of LLM roles for stock selection, analysis, trading, and coaching

Each bot keeps its own paper-account history, reports, and dashboard sections so you can compare them side by side.

**Disclaimer:** This project is for educational purposes only and is not financial advice.

Deployment guide:
[DEPLOY.md](/Users/keithvandusen/Documents/New%20project/DEPLOY.md)

## Quick Start

1. Create a virtual environment and install deps:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.bot.txt
```

2. Copy environment variables:

```bash
python3 scripts/setup_env.py
```

3. Update `data/sp500.csv` with the full S&P 500 list when ready.

## Architecture

`ML Bot` is the original bounded ensemble:

- Base model: a small supervised ensemble predicts short-horizon returns from momentum, volatility, and market context features. It includes Random Forest, Extra Trees, gradient boosting, and a linear challenger.
- Market overlays: Alpaca snapshots, market movers, most-active symbols, and recent news headlines can nudge the base prediction up or down.
- Optional LLM overlay: an LLM can review the strongest candidates and add a small explainable adjustment, but only within tight limits.
- Memory: the bot scores symbols partly by how well its past decisions on those symbols have worked.
- Learning loop: mature decisions are evaluated after the prediction horizon passes, component weights are adjusted within bounds, and the learned policy is saved in `data/learned_policy.json`.

`LLM Bot` is a multi-role decision system:

- `Stock Selector`: chooses the watchlist
- `Analyst`: writes daily memos for each watchlist stock, including catalysts, contrary evidence, time horizon, and confidence
- `Trader`: reads the analyst memos plus coach guidance and makes today’s long/short decisions with structured conviction and expected upside/downside
- `Coach`: reviews mature outcomes and writes the next feedback report for the trader, avoiding behavior changes based on one-off results

Both bots use the same downstream execution/risk controls once they produce trade ideas, but they can run against separate Alpaca paper accounts.

Reporting: markdown reports are written to `data/reports/` and also stored in the SQLite database for downstream dashboards/snapshots.

## Commands

Train the model on one year of data:

```bash
python3 -m broker_bot.cli train
```

Run a backtest (in-sample, for quick feedback):

```bash
python3 -m broker_bot.cli backtest
```

The backtest now evaluates an ensemble-aware proxy of the live system, including:

- the base Random Forest
- technical overlays
- snapshot-style price/volume overlays
- screener-style mover/activity overlays
- event/news proxies from abnormal move and volume behavior
- rolling symbol memory
- a bounded discretionary/LLM-style conviction proxy

Rebalance the paper portfolio using the latest signals:

```bash
python3 -m broker_bot.cli rebalance
```

Rebalance the separate LLM bot paper account:

```bash
python3 -m broker_bot.cli rebalance-llm
```

Review mature past decisions, score what worked, and update learned component weights:

```bash
python3 -m broker_bot.cli review-decisions
```

Generate a strategy report explaining recent decisions, lessons, and proposed changes:

```bash
python3 -m broker_bot.cli strategy-report
```

Refresh the LLM bot reporting/coaching loop:

```bash
python3 -m broker_bot.cli review-decisions-llm
python3 -m broker_bot.cli strategy-report-llm
```

Generate a paper-only options scaffold report that turns the strongest stock ideas into defined-risk vertical spread candidates:

```bash
python3 -m broker_bot.cli options-report
```

Snapshot account + positions (no trades):

```bash
python3 -m broker_bot.cli snapshot
```

Snapshot the LLM bot account:

```bash
python3 -m broker_bot.cli snapshot-llm
```

Launch the desktop dashboard (Tkinter):

```bash
python3 -m broker_bot.cli dashboard
```

Launch the local web dashboard (recommended for macOS Tk issues). The equity chart overlays SPY for comparison and shows 20D alpha/tracking error:

```bash
python3 -m broker_bot.cli dashboard-web
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. If `API_TOKEN` is set, open with:
`http://127.0.0.1:8000/?token=YOUR_TOKEN`

You can override the host/port with env vars:

```bash
DASHBOARD_HOST=0.0.0.0 DASHBOARD_PORT=8000 python3 -m broker_bot.cli dashboard-web
```

### Streamlit (GitHub + Community Cloud)

You can deploy the UI via Streamlit Community Cloud using `streamlit_app.py`. The Streamlit app uses `requirements.txt` (minimal).

1. Push the repo to GitHub.
2. In Streamlit Community Cloud, select:
   - **Repository**: your repo
   - **Branch**: `main`
   - **Main file**: `streamlit_app.py`
3. Add the following **Secrets** (not in the repo):
   - If using the API approach: `API_BASE_URL` and `API_TOKEN`
   - If using GitHub snapshots (no API): `DATA_URL` pointing to the raw JSON, for example:
     `https://raw.githubusercontent.com/<user>/<repo>/main/data/dashboard_snapshot.json`

The Streamlit app calls your bot API endpoints and shows:
Equity vs SPY, positions, trades, analyst/trader/coach reports, strategy-report snapshots, and recent decision rationale for both bots in separate sections.

### GitHub Actions (Full Scheduled Cloud Run)

This workflow runs on a schedule and performs the full paper-trading cloud loop:

- restore prior state from the committed snapshot
- train the model
- rebalance the paper account
- review past decisions and update learned weights
- generate advisor and strategy reports
- rebuild `data/dashboard_snapshot.json`
- commit updated snapshot/report/policy files back to GitHub

Workflow file: `.github/workflows/advisor_snapshot.yml`

**Secrets to add in GitHub**:
- `ALPACA_API_KEY`
- `ALPACA_SECRET_KEY`
- `ALPACA_PAPER_URL` (optional, defaults to paper endpoint)
- `ALPACA_DATA_FEED` (optional)
- `ALPACA_LLM_API_KEY` and `ALPACA_LLM_SECRET_KEY` for the second paper account used by the LLM bot
- `ALPACA_LLM_PAPER_URL` and `ALPACA_LLM_DATA_FEED` (optional)
- `OPENAI_API_KEY` (if `LLM_ENABLED=1`)
- `LLM_ENABLED` (`1` to enable LLM advisor)
- `LLM_MODEL` (e.g. `gpt-5-mini`)
- `API_TOKEN`

**Schedule note**: The cron is set for **21:15 UTC** (4:15pm ET in winter). During daylight saving time it will run at 5:15pm ET unless you update the schedule.

Manual commands used by the workflow:

```bash
python3 -m broker_bot.cli train
python3 -m broker_bot.cli rebalance
python3 -m broker_bot.cli snapshot
python3 -m broker_bot.cli review-decisions
python3 -m broker_bot.cli advisor-report
python3 -m broker_bot.cli strategy-report
python3 -m broker_bot.cli rebalance-llm
python3 -m broker_bot.cli snapshot-llm
python3 -m broker_bot.cli review-decisions-llm
python3 -m broker_bot.cli options-report
python3 scripts/build_snapshot.py
```

### LLM Advisor And LLM Research Overlay

The bot can optionally use an LLM in two places:

- Advisor mode: explainability plus small parameter suggestions.
- Research overlay: candidate review for the strongest long/short names, again with small bounded return adjustments.

Set these in `.env` (or use secrets in CI):

```bash
OPENAI_API_KEY=your_key_here
LLM_ENABLED=1
LLM_MODEL=gpt-5-mini
```

LLM outputs are sanitized and clamped to conservative bounds before applying overrides or score adjustments.

## Notes

- The bot uses long/short signals with inverse-volatility sizing and an SPY regime filter (reduces leverage in bear regimes).
- The base model is a Random Forest regressor on momentum/volatility features with market context.
- The live signal stack can blend in Alpaca snapshots, market movers, most-active names, recent Alpaca news headlines, symbol memory, and optional LLM watchlist judgments.
- The new LLM bot keeps its own watchlist, analyst daily reports, trader daily reports, and coach reports.
- The backtest uses walk-forward retraining, weekly rebalancing, and transaction cost estimates for realism.
- The backtest now better matches the live ensemble by simulating bounded overlay components offline from historical price/volume structure.
- Advisor overrides are stored in `data/advisor_overrides.json` and applied at startup when enabled.
- Learned ensemble weights are stored in `data/learned_policy.json` and are intentionally kept bounded.
- Reports are written to `data/reports/`.
- The dashboard APIs/UI now expose recent selected decisions, component contributions, and later outcomes.
- Optional sector exposure critiques use `data/sector_map.csv` (set via `SECTOR_MAP_PATH`).

### Risk & Liquidity Controls

- `MIN_PRICE` and `MIN_DOLLAR_VOL` filter illiquid or low-priced symbols.
- `VOL_TARGET` + `VOL_WINDOW` scales leverage down in high-volatility regimes.
- `MAX_DRAWDOWN`, `MIN_LEVERAGE`, and `DRAWDOWN_WINDOW` apply drawdown guardrails.
- `MAX_SECTOR_EXPOSURE_PCT` caps total absolute exposure in one mapped sector.
- `MAX_CORRELATED_EXPOSURE_PCT`, `CORRELATION_THRESHOLD`, and `CORRELATION_WINDOW` cap clusters of highly correlated positions.
- `TECHNICAL_WEIGHT`, `SNAPSHOT_WEIGHT`, `SCREENER_WEIGHT`, `NEWS_WEIGHT`, `MEMORY_WEIGHT`, and `LLM_WEIGHT` set the ensemble blend before learned-policy updates.
- `EXECUTION_ORDER_MODE=simple` keeps the old behavior: market orders are submitted only when the bot runs.
- `EXECUTION_ORDER_MODE=bracket` tells Alpaca to hold server-side take-profit and stop-loss exits for fresh entries using `BRACKET_TAKE_PROFIT_PCT` and `BRACKET_STOP_LOSS_PCT`.
- `ADAPTIVE_EXITS_ENABLED=1` makes bracket exits volatility-aware using `STOP_LOSS_VOL_MULTIPLE`, `TAKE_PROFIT_REWARD_MULTIPLE`, `MIN_STOP_LOSS_PCT`, and `MAX_STOP_LOSS_PCT`.
- `TRAILING_STOP_ENABLED=1` adds Alpaca-side trailing-stop protection for positions that remain after rebalance. Use either `TRAILING_STOP_PERCENT` or `TRAILING_STOP_PRICE`.
- Advanced Alpaca order types are handled conservatively in this project: if a bracket order is rejected, the bot falls back to a simple market order, and trailing stops are only attached when the position size is compatible with whole-share handling.
- `ALPACA_LLM_API_KEY`, `ALPACA_LLM_SECRET_KEY`, `ALPACA_LLM_PAPER_URL`, and `ALPACA_LLM_DATA_FEED` configure the second paper account used by the LLM bot.
- The local dashboard and Streamlit snapshot now show broker-side protection summaries per position so you can see whether exits are resting at Alpaca.
- The dashboard is multi-bot aware: ML and LLM equity, positions, trades, decisions, and reports are stored separately and displayed separately.
- `OPTIONS_MIN_DTE`, `OPTIONS_MAX_DTE`, `OPTIONS_IDEA_LIMIT`, and `OPTIONS_SPREAD_WIDTH_PCT` control the paper-only options scaffold report.
- The current options scaffold intentionally stays conservative: it suggests bull call debit spreads for bullish ideas and bear put debit spreads for bearish ideas, using recent option contract close prices as rough planning inputs rather than live spread-aware execution logic.
- `OPTIONS_MIN_REWARD_RISK` and `OPTIONS_MAX_DEBIT_PCT_OF_WIDTH` filter out weak vertical-spread structures before they appear in the scaffold report.
- Backtest-only reliability simulation:
  - `MISS_REBALANCE_PROB` simulates skipped rebalances (e.g., CI delays/failures).
  - `REBALANCE_DELAY_DAYS` delays a missed rebalance by N days.

### Reliability Impact Estimator

Compare baseline performance vs missed-rebalance scenarios:

```bash
python3 scripts/compare_reliability.py --miss-prob 0.05 --delay-days 1 --seeds 1 2 3 4 5
```
