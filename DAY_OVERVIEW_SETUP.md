# Day Overview - End-to-End Setup (MVP)

This connects the backend to the iPhone app and gets your first daily overview working.

## 1) Start the backend
From `/Users/keithvandusen/Documents/New project/day_overview_backend`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

If you visit `http://127.0.0.1:8001/daily-content` you should see JSON.

## 2) Configure news sources (optional but recommended)
`day_overview_backend/data/news_feeds.json` is now prefilled with AP and Reuters RSS feeds.
You can add or swap sources as you like. If the list is empty, the backend returns a placeholder news item.

## 3) Populate ICU trials and historical facts
The backend ships with placeholders to avoid accidental medical inaccuracies.
When you’re ready, I can populate those lists from verified sources.

Files:
- `day_overview_backend/data/icu_trials.json`
- `day_overview_backend/data/historical_facts.json`

## 4) Wire the app to the backend
In `day_overview_ios/DayOverview/AppConfig.swift`, set:
- `backendBaseURL` to your backend host.

If the backend runs on your Mac and you run the app on your iPhone, you’ll need your Mac’s local IP address instead of `127.0.0.1`.

## 4b) Weather default location
The app uses your current location if you grant permission. If not, it falls back to default coordinates set to Durham, NC (ZIP 27701) in `day_overview_ios/DayOverview/AppConfig.swift`.

## 5) Build the app in Xcode
Open the full project:
- `day_overview_ios/DayOverview.xcodeproj`

Then follow the steps in:
- `day_overview_ios/README.md`

## 6) Morning routine at 5:00 a.m.
The app schedules a background refresh, but iOS does not guarantee exact execution time.
If you open the app around 5:00 a.m., it will always generate a fresh overview.
