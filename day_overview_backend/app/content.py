import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional
from html import unescape

import feedparser
from .models import DailyContent, NewsItem

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CACHE_DIR = ROOT / "cache"


def _load_json(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _clean_text(text: str) -> str:
    if not text:
        return ""
    text = unescape(text)
    # Remove simple HTML tags without pulling in a full parser
    while "<" in text and ">" in text:
        start = text.find("<")
        end = text.find(">", start)
        if end == -1:
            break
        text = text[:start] + text[end + 1 :]
    return " ".join(text.split())


def _pick_by_date(items: List[Dict], day: date) -> Optional[Dict]:
    if not items:
        return None
    idx = day.toordinal() % len(items)
    return items[idx]


def _pick_trial_by_date(trials: List[Dict], day: date) -> Optional[Dict]:
    if not trials:
        return None

    landmark = [t for t in trials if t.get("category") == "landmark"]
    recent = [t for t in trials if t.get("category") == "recent"]

    if landmark and recent:
        pool = landmark if day.toordinal() % 2 == 0 else recent
    else:
        pool = trials

    idx = day.toordinal() % len(pool)
    return pool[idx]


def _icu_summary(trial: Optional[Dict]) -> str:
    if not trial:
        return (
            "No ICU trial data is configured. Add items to data/icu_trials.json "
            "to enable this section."
        )

    if trial.get("summary"):
        return trial["summary"]

    name = trial.get("name", "Unknown trial")
    year = trial.get("year", "")
    question = trial.get("question", "")
    population = trial.get("population", "")
    primary = trial.get("primary_outcome", "")

    parts = [f"{name} ({year})."]
    if question:
        parts.append(f"Clinical question: {question}.")
    if population:
        parts.append(f"Population: {population}.")
    if primary:
        parts.append(f"Primary outcome: {primary}.")

    return " ".join([p for p in parts if p])


def _historical_fact(fact: Optional[Dict]) -> str:
    if not fact:
        return (
            "No historical facts are configured. Add items to data/historical_facts.json "
            "to enable this section."
        )

    if fact.get("fact"):
        return fact["fact"]

    title = fact.get("title", "Historical fact")
    year = fact.get("year", "")
    detail = fact.get("detail", "")
    if year:
        return f"{year}: {title}. {detail}".strip()
    return f"{title}. {detail}".strip()


def _news_sources() -> List[str]:
    env_sources = os.getenv("NEWS_FEEDS", "")
    if env_sources:
        return [s.strip() for s in env_sources.split(",") if s.strip()]

    # Optional JSON file with feeds
    feeds_path = DATA_DIR / "news_feeds.json"
    feeds = _load_json(feeds_path)
    return [f for f in feeds if isinstance(f, str)]


def _fetch_news(limit: int = 5) -> List[NewsItem]:
    sources = _news_sources()
    if not sources:
        return [
            NewsItem(
                headline="No news sources configured",
                summary="Set NEWS_FEEDS or data/news_feeds.json to enable this section.",
                source="system",
            )
        ]

    items: List[NewsItem] = []
    for url in sources:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if len(items) >= limit:
                    break
                headline = _clean_text(entry.get("title", "Untitled"))
                summary = _clean_text(entry.get("summary", ""))
                source = _clean_text(feed.feed.get("title", "unknown"))
                if headline:
                    items.append(
                        NewsItem(headline=headline, summary=summary, source=source)
                    )
        except Exception:
            continue

        if len(items) >= limit:
            break

    if not items:
        return [
            NewsItem(
                headline="News feeds unavailable",
                summary="Could not fetch news. Check feed URLs and network access.",
                source="system",
            )
        ]

    return items


def generate_daily_content(day: date) -> DailyContent:
    trials = _load_json(DATA_DIR / "icu_trials.json")
    facts = _load_json(DATA_DIR / "historical_facts.json")

    trial = _pick_trial_by_date(trials, day)
    fact = _pick_by_date(facts, day)

    return DailyContent(
        date=day.isoformat(),
        news=_fetch_news(limit=5),
        icu_trial_summary=_icu_summary(trial),
        historical_fact=_historical_fact(fact),
        generated_at=datetime.utcnow().isoformat() + "Z",
    )


def read_cache(day: date) -> Optional[DailyContent]:
    path = CACHE_DIR / f"{day.isoformat()}.json"
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return DailyContent(**data)


def write_cache(content: DailyContent) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{content.date}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(content.dict(), f, indent=2)
