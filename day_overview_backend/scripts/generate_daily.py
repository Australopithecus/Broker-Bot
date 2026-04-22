from datetime import date

from app.content import generate_daily_content, write_cache


if __name__ == "__main__":
    today = date.today()
    content = generate_daily_content(today)
    write_cache(content)
    print(f"Generated content for {today.isoformat()}")
