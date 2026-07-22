"""Normalize AMOC monthly observations.

RAPID's official portal asks for an email address before serving files, so this
script supports direct CSV/file inputs instead of scraping the gated form.

Environment:
- AMOC_CSV_URL: optional direct CSV URL
- AMOC_SOURCE_FILE: optional local CSV path

Accepted columns are intentionally flexible: date/year/month plus one of
amoc_transport_sv, transport, amoc, moc, rapid_amoc, or value.
"""

from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path

from pipeline_common import PROCESSED, ensure_dirs, fetch_text, get_env, number, write_csv, years_from_env


FIELDS = ["date", "year", "month", "amoc_transport_sv", "amoc_anomaly_sv", "source"]
VALUE_COLUMNS = ["amoc_transport_sv", "transport", "amoc", "moc", "rapid_amoc", "value"]


def main() -> None:
    ensure_dirs()
    start_year, end_year = years_from_env()
    text = load_source_text()
    rows = normalize_rows(list(csv.DictReader(StringIO(text))), start_year, end_year)
    if not rows:
        raise SystemExit("No AMOC rows were parsed. Check AMOC_CSV_URL or AMOC_SOURCE_FILE columns.")
    write_csv(PROCESSED / "amoc_monthly.csv", rows, FIELDS)
    print(f"Wrote {len(rows)} AMOC monthly rows")


def load_source_text() -> str:
    source_file = get_env("AMOC_SOURCE_FILE")
    if source_file:
        return Path(source_file).read_text(encoding="utf-8")

    source_url = get_env("AMOC_CSV_URL")
    if source_url:
        return fetch_text(source_url)

    raise SystemExit(
        "Set AMOC_CSV_URL or AMOC_SOURCE_FILE. Official RAPID data is available from "
        "https://rapid.ac.uk/data/data-download after entering contact details."
    )


def normalize_rows(rows: list[dict[str, str]], start_year: int, end_year: int) -> list[dict[str, str | int | float]]:
    parsed: list[dict[str, str | int | float]] = []
    values: list[float] = []

    for row in rows:
        date_value = row.get("date") or row.get("Date") or row.get("time") or row.get("Time")
        year = int(number(row.get("year") or row.get("Year") or (date_value or "")[:4], -1))
        month = int(number(row.get("month") or row.get("Month") or (date_value or "")[5:7], 1))
        if year < start_year or year > end_year:
            continue

        value = first_number(row, VALUE_COLUMNS)
        if value is None:
            continue

        values.append(value)
        parsed.append(
            {
                "date": f"{year:04d}-{month:02d}",
                "year": year,
                "month": month,
                "amoc_transport_sv": round(value, 4),
                "amoc_anomaly_sv": 0,
                "source": row.get("source") or row.get("Source") or "RAPID",
            }
        )

    mean = sum(values) / len(values) if values else 0
    for row in parsed:
        row["amoc_anomaly_sv"] = round(float(row["amoc_transport_sv"]) - mean, 4)

    return parsed


def first_number(row: dict[str, str], columns: list[str]) -> float | None:
    lower = {key.lower(): value for key, value in row.items()}
    for column in columns:
        if column.lower() in lower:
            value = number(lower[column.lower()], float("nan"))
            if value == value:
                return value
    return None


if __name__ == "__main__":
    main()
