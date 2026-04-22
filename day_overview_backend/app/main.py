from datetime import date, datetime
from fastapi import FastAPI, HTTPException, Query

from .content import generate_daily_content, read_cache, write_cache
from .models import DailyContent

app = FastAPI(title="Day Overview Backend")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"}


@app.get("/daily-content", response_model=DailyContent)
async def daily_content(
    day: str = Query(default=None, description="ISO date, e.g. 2026-02-14"),
    force: bool = Query(default=False, description="Regenerate even if cached"),
) -> DailyContent:
    if day:
        try:
            target_day = date.fromisoformat(day)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid date format") from exc
    else:
        target_day = date.today()

    if not force:
        cached = read_cache(target_day)
        if cached:
            return cached

    content = generate_daily_content(target_day)
    write_cache(content)
    return content
