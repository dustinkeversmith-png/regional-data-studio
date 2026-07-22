"""Fetch NASA FIRMS active-fire detections for Oregon.

Requires a free FIRMS MAP_KEY:
https://firms.modaps.eosdis.nasa.gov/api/map_key/

Environment:
- FIRMS_MAP_KEY: required
- FIRMS_SOURCES: comma-separated sources, default VIIRS_SNPP_SP,VIIRS_NOAA20_SP
- START_YEAR / END_YEAR: default 2016 / 2025
"""

from __future__ import annotations

import csv
from io import StringIO

from pipeline_common import OREGON_BBOX, PROCESSED, date_windows, ensure_dirs, fetch_text, get_env, write_csv, years_from_env


FIELDS = [
    "latitude",
    "longitude",
    "acq_date",
    "acq_time",
    "year",
    "month",
    "brightness",
    "frp",
    "confidence",
    "satellite",
    "instrument",
]


def main() -> None:
    ensure_dirs()
    map_key = get_env("FIRMS_MAP_KEY")
    if not map_key:
        raise SystemExit(
            "FIRMS_MAP_KEY is required for actual FIRMS data. Create a free MAP_KEY at "
            "https://firms.modaps.eosdis.nasa.gov/api/map_key/ and rerun."
        )

    start_year, end_year = years_from_env()
    sources = (get_env("FIRMS_SOURCES", "VIIRS_SNPP_SP,VIIRS_NOAA20_SP") or "").split(",")
    rows: list[dict[str, str]] = []

    for source in [source.strip() for source in sources if source.strip()]:
        rows.extend(fetch_source(map_key, source, start_year, end_year))

    rows = dedupe(rows)
    write_csv(PROCESSED / "fire_points_2016_2025.csv", rows, FIELDS)
    print(f"Wrote {len(rows)} FIRMS detections")


def fetch_source(map_key: str, source: str, start_year: int, end_year: int) -> list[dict[str, str]]:
    west, south, east, north = OREGON_BBOX
    bbox = f"{west},{south},{east},{north}"
    rows: list[dict[str, str]] = []

    for start_date, days in date_windows(start_year, end_year, step_days=10):
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{map_key}/{source}/{bbox}/{days}/{start_date.isoformat()}"
        text = fetch_text(url)
        parsed = csv.DictReader(StringIO(text))
        for row in parsed:
            normalized = normalize_row(row)
            if normalized:
                rows.append(normalized)
        print(f"{source} {start_date.isoformat()} +{days}d: {len(rows)} cumulative rows")

    return rows


def normalize_row(row: dict[str, str]) -> dict[str, str] | None:
    acq_date = row.get("acq_date") or row.get("ACQ_DATE")
    if not acq_date or "Invalid" in acq_date:
        return None
    year, month = acq_date.split("-")[:2]
    instrument = row.get("instrument") or row.get("type") or row.get("source") or "VIIRS"

    return {
        "latitude": row.get("latitude", ""),
        "longitude": row.get("longitude", ""),
        "acq_date": acq_date,
        "acq_time": row.get("acq_time", ""),
        "year": year,
        "month": str(int(month)),
        "brightness": row.get("bright_ti4") or row.get("brightness") or row.get("bright_t31") or "",
        "frp": row.get("frp", ""),
        "confidence": row.get("confidence", ""),
        "satellite": row.get("satellite", ""),
        "instrument": instrument,
    }


def dedupe(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[tuple[str, str, str, str, str]] = set()
    output: list[dict[str, str]] = []
    for row in rows:
        key = (row["latitude"], row["longitude"], row["acq_date"], row["acq_time"], row["instrument"])
        if key in seen:
            continue
        seen.add(key)
        output.append(row)
    return output


if __name__ == "__main__":
    main()
