# Free Cloud Deployment

This project is set up to run for free using:

- GitHub Actions for scheduled bot runs
- Streamlit Community Cloud for the dashboard
- GitHub Secrets for API keys

This is the simplest free setup for a paper-trading bot that only needs to run on a schedule rather than continuously all day.

## What This Deployment Does

The GitHub Actions workflow:

1. restores prior bot state from `data/dashboard_snapshot.json`
2. trains the model
3. rebalances configured brokerage-service paper portfolios
4. reviews prior decisions and updates learned weights
5. generates advisor, strategy, and all-model Summary Reports
6. rebuilds `data/dashboard_snapshot.json`
7. commits the updated snapshot, reports, and learned policy back to GitHub

The Streamlit app reads the committed snapshot and shows:

- equity vs SPY
- current positions
- recent trades
- advisor reports
- strategy reports
- all-model Summary Reports
- recent decision rationale

## Before You Start

You need:

- a GitHub account
- one or more brokerage-service paper trading accounts
- an OpenAI API key if you want LLM features enabled

## Step 1: Push The Repo To GitHub

Create a GitHub repository and push this project to it.

Example:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

## Step 2: Add GitHub Repository Secrets

In GitHub:

1. open your repository
2. click `Settings`
3. click `Secrets and variables`
4. click `Actions`
5. click `New repository secret`

Add these secrets:

- `ALPACA_API_KEY`
- `ALPACA_SECRET_KEY`
- `ALPACA_PAPER_URL`
- `ALPACA_DATA_FEED`
- `ALPACA_LLM_API_KEY` and `ALPACA_LLM_SECRET_KEY` if you want to run the LLM Bot in a separate account
- `ALPACA_STAT_ARB_API_KEY` and `ALPACA_STAT_ARB_SECRET_KEY` if you want to run the Stat Arb Bot in a separate account
- `OPENAI_API_KEY`
- `LLM_ENABLED`
- `LLM_MODEL`
- `API_TOKEN`

Suggested values:

- `ALPACA_PAPER_URL=https://paper-api.alpaca.markets`
- `ALPACA_DATA_FEED=iex`
- `LLM_ENABLED=1` if you want LLM overlays, otherwise `0`
- `LLM_MODEL=gpt-5-mini`
- `API_TOKEN` can be any long random string

## Step 3: Enable The Scheduled Workflow

The daily deep workflow file is:

- [.github/workflows/advisor_snapshot.yml](/Users/keithvandusen/Documents/New%20project/.github/workflows/advisor_snapshot.yml)

The lightweight market-hours caretaker workflow file is:

- [.github/workflows/market_caretaker.yml](/Users/keithvandusen/Documents/New%20project/.github/workflows/market_caretaker.yml)

In GitHub:

1. open the `Actions` tab
2. enable workflows if GitHub asks
3. open `Broker Bot Cloud Run`
4. click `Run workflow` once manually to seed the first snapshot and reports

After that, GitHub will keep running the deep workflow after market close and the caretaker workflow around market hours.

## Step 4: Deploy The Dashboard To Streamlit Community Cloud

Go to [Streamlit Community Cloud](https://share.streamlit.io/) and connect your GitHub account.

Create a new app with:

- Repository: your GitHub repo
- Branch: `main`
- Main file path: `streamlit_app.py`

## Step 5: Add Streamlit Secrets

In the Streamlit app settings, add this secret:

```toml
DATA_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/data/dashboard_snapshot.json"
```

Replace `YOUR_USERNAME` and `YOUR_REPO` with your actual GitHub values.

If your repo is private, the raw GitHub URL approach will not work for Streamlit Community Cloud unless you expose the data some other way. For the easiest free setup, a public repo is simplest.

Optional dashboard-triggered cloud runs need four more Streamlit secrets:

```toml
GITHUB_REPOSITORY = "YOUR_USERNAME/YOUR_REPO"
GITHUB_WORKFLOW_ID = "advisor_snapshot.yml"
GITHUB_WORKFLOW_REF = "main"
BROKER_BOT_GITHUB_TOKEN = "github_pat_..."
```

`BROKER_BOT_GITHUB_TOKEN` should be a GitHub fine-grained personal access token for this repository with Actions read/write access. The dashboard also accepts the older `GITHUB_ACTIONS_TOKEN` name, but the broker-specific name is less likely to be confused with GitHub Actions' own built-in token. If you use a classic token, include `repo` and `workflow` scope. The dashboard keeps the token server-side in Streamlit secrets and uses it only to ask GitHub Actions to start the existing workflow.

## Step 6: Verify The First Cloud Run

After the first GitHub Actions run completes:

1. open the repo on GitHub
2. confirm these files exist and were updated:
   - `data/dashboard_snapshot.json`
   - `data/learned_policy.json`
   - `data/reports/...`
3. open the Streamlit app
4. confirm the dashboard loads data

## Recommended Low-Risk Settings

For a first cloud deployment, keep things conservative:

- use paper trading only
- keep `LLM_ENABLED=0` initially if you want fewer moving parts
- run the workflow only once per weekday until you’re comfortable
- inspect the strategy report after each run
- use the dashboard's manual run button only when you would also be comfortable clicking `Run workflow` in GitHub Actions
- keep `CARETAKER_DAILY_DRAWDOWN_LIMIT=0` until you are comfortable with the caretaker closing paper positions automatically

## Important Caveats

- GitHub Actions is scheduled, not always-on.
- Streamlit Community Cloud is a dashboard host, not the trading engine.
- GitHub cron runs in UTC, not Eastern Time.
- Streamlit Community Cloud can sleep when unused.
- This is appropriate for paper trading and periodic rebalancing, not high-frequency trading.

## If You Want To Change The Schedule

Edit the cron lines in:

- [.github/workflows/advisor_snapshot.yml](/Users/keithvandusen/Documents/New%20project/.github/workflows/advisor_snapshot.yml)
- [.github/workflows/market_caretaker.yml](/Users/keithvandusen/Documents/New%20project/.github/workflows/market_caretaker.yml)

Current format:

```yaml
schedule:
  - cron: "15 21 * * 1-5"
```

That means weekdays at `21:15 UTC`.

## If Something Fails

Check these first:

- missing GitHub secrets
- wrong paper URL or credentials
- empty or outdated `data/sp500.csv`
- Streamlit `DATA_URL` pointing to the wrong repo path
- LLM enabled without a valid `OPENAI_API_KEY`

## Recommended Next Improvements

Once this free setup is working well, the best next upgrades are:

- add earnings-aware controls
- add sector/risk caps
- add champion-vs-challenger model comparison
- add alerts for drawdown spikes or zero-trade days
