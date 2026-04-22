from pydantic import BaseModel
from typing import List


class NewsItem(BaseModel):
    headline: str
    summary: str
    source: str


class DailyContent(BaseModel):
    date: str
    news: List[NewsItem]
    icu_trial_summary: str
    historical_fact: str
    generated_at: str
