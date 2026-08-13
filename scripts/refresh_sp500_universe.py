#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


RAW_SOURCE_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies?action=raw"
SOURCE_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
VALID_GICS_SECTORS = {
    "Communication Services",
    "Consumer Discretionary",
    "Consumer Staples",
    "Energy",
    "Financials",
    "Health Care",
    "Industrials",
    "Information Technology",
    "Materials",
    "Real Estate",
    "Utilities",
}


def _fetch_raw_components_table() -> str:
    request = Request(RAW_SOURCE_URL, headers={"User-Agent": "broker-bot-universe-refresh/1.0"})
    text = urlopen(request, timeout=20).read().decode("utf-8")
    start = text.index('id="constituents"')
    end = text.index("\n|}", start)
    return text[start:end]


def _split_wikitable_cells(row_chunk: str) -> list[str]:
    cells = []
    for value in re.split(r"\|\|", row_chunk):
        value = value.strip()
        if not value or value.startswith("{|") or value.startswith("!") or value.startswith("|-"):
            continue
        cells.append(value)
    return cells


def parse_components(raw_table: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for chunk in raw_table.split("\n|-"):
        cells = _split_wikitable_cells(chunk)
        if len(cells) < 2:
            continue
        symbol_match = re.search(r"\{\{(?:NyseSymbol|NasdaqSymbol|BZX link)\|([^}|<]+)", cells[0])
        if not symbol_match:
            continue
        symbol = symbol_match.group(1).strip().upper()
        sector = ""
        for raw_cell in cells[1:]:
            candidate = re.sub(r"<[^>]+>", "", raw_cell).strip()
            if candidate in VALID_GICS_SECTORS:
                sector = candidate
                break
        if not sector:
            raise RuntimeError(f"Could not find valid GICS sector for {symbol}.")
        rows.append((symbol, sector))

    clean: list[tuple[str, str]] = []
    seen: set[str] = set()
    for symbol, sector in sorted(rows):
        if symbol in seen:
            continue
        seen.add(symbol)
        clean.append((symbol, sector))
    if len(clean) < 500:
        raise RuntimeError(f"Parsed only {len(clean)} symbols; refusing to overwrite universe files.")
    return clean


def write_universe(rows: list[tuple[str, str]], data_dir: Path) -> None:
    data_dir.mkdir(exist_ok=True)
    with (data_dir / "sp500.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["symbol"])
        for symbol, _ in rows:
            writer.writerow([symbol])

    with (data_dir / "sector_map.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["symbol", "sector"])
        writer.writerows(rows)

    (data_dir / "universe_metadata.json").write_text(
        json.dumps(
            {
                "source": SOURCE_URL,
                "raw_source": RAW_SOURCE_URL,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "symbol_count": len(rows),
                "fields": ["Symbol", "GICS Sector"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    rows = parse_components(_fetch_raw_components_table())
    write_universe(rows, Path("data"))
    print(f"Wrote {len(rows)} S&P 500 symbols to data/sp500.csv and data/sector_map.csv.")


if __name__ == "__main__":
    main()
