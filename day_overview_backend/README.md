# Day Overview Backend (MVP)

This service generates the daily non‑personal content (news, ICU trial summary, historical fact) and exposes a single endpoint the iPhone app can call each morning.

## What it does
- `GET /daily-content` returns a JSON payload for a given day (cached on disk).
- If no cached file exists, it generates one and saves it in `cache/`.

## Quick Start
1. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the API:

```bash
uvicorn app.main:app --reload --port 8001
```

3. Test it in a browser or curl:

```bash
curl "http://127.0.0.1:8001/daily-content"
```

## Configuration

### News feeds
- Set `NEWS_FEEDS` to a comma‑separated list of RSS/Atom URLs, or edit `data/news_feeds.json`.
- The default list is AP (US + World) and Reuters (US + World).
- If no feeds are configured, the API returns a placeholder news item.

### ICU trials and historical facts
- Edit `data/icu_trials.json` and `data/historical_facts.json`.
- These files ship with placeholders so we can avoid accidental medical inaccuracies.
- When you are ready, I can populate them from verified sources.

## Daily pre‑generation (optional)
If you want a daily pre‑generation step (e.g., at 4:30 a.m.), run:

```bash
python3 scripts/generate_daily.py
```

You can schedule that with cron or any scheduler.
