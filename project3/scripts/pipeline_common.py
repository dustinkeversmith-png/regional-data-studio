"""Shared utilities for the Oregon fire + AMOC data pipeline."""

from __future__ import annotations

import csv
import json
import math
import os
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "public" / "data" / "processed"
RAW = ROOT / "public" / "data" / "raw"
OREGON_BBOX = (-124.7035, 41.9918, -116.4635, 46.292)


def ensure_dirs() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)


def get_env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name, default)
    if value is None:
        return None
    value = value.strip()
    return value or None


def years_from_env(default_start: int = 2016, default_end: int = 2025) -> tuple[int, int]:
    start = int(get_env("START_YEAR", str(default_start)) or default_start)
    end = int(get_env("END_YEAR", str(default_end)) or default_end)
    if end < start:
        raise ValueError("END_YEAR must be greater than or equal to START_YEAR")
    return start, end


def fetch_json(url: str, params: dict[str, Any] | None = None, retries: int = 3) -> Any:
    if params:
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}{urlencode(params)}"

    for attempt in range(retries):
        try:
            request = Request(url, headers={"User-Agent": "oregon-amoc-fire-visualizer/0.1"})
            with urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))

    raise RuntimeError("unreachable")


def fetch_text(url: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            request = Request(url, headers={"User-Agent": "oregon-amoc-fire-visualizer/0.1"})
            with urlopen(request, timeout=120) as response:
                return response.read().decode("utf-8")
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))

    raise RuntimeError("unreachable")


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    ensure_dirs()
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def read_geojson(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"type": "FeatureCollection", "features": []}
    return json.loads(path.read_text(encoding="utf-8"))


def write_geojson(path: Path, data: dict[str, Any]) -> None:
    ensure_dirs()
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def number(value: Any, fallback: float = 0.0) -> float:
    if value is None or value == "":
        return fallback
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return fallback
    if math.isnan(parsed) or math.isinf(parsed):
        return fallback
    return parsed


def int_value(value: Any, fallback: int = 0) -> int:
    return int(round(number(value, fallback)))


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value[:19], fmt).date()
        except ValueError:
            continue
    return None


def date_windows(start_year: int, end_year: int, step_days: int = 10) -> Iterable[tuple[date, int]]:
    current = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    while current <= end:
        window_end = min(current + timedelta(days=step_days - 1), end)
        yield current, (window_end - current).days + 1
        current = window_end + timedelta(days=1)


def bbox(feature: dict[str, Any]) -> tuple[float, float, float, float] | None:
    coords: list[tuple[float, float]] = []

    def walk(value: Any) -> None:
      if isinstance(value, list) and len(value) >= 2 and all(isinstance(v, (int, float)) for v in value[:2]):
          coords.append((float(value[0]), float(value[1])))
      elif isinstance(value, list):
          for child in value:
              walk(child)

    geometry = feature.get("geometry") or {}
    walk(geometry.get("coordinates"))
    if not coords:
        return None
    xs = [coord[0] for coord in coords]
    ys = [coord[1] for coord in coords]
    return min(xs), min(ys), max(xs), max(ys)


def bbox_center(feature: dict[str, Any]) -> tuple[float, float] | None:
    bounds = bbox(feature)
    if bounds is None:
        return None
    west, south, east, north = bounds
    return (west + east) / 2, (south + north) / 2


def point_in_ring(lon: float, lat: float, ring: list[list[float]]) -> bool:
    inside = False
    j = len(ring) - 1
    for i, point in enumerate(ring):
        xi, yi = point[0], point[1]
        xj, yj = ring[j][0], ring[j][1]
        intersects = (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi
        if intersects:
            inside = not inside
        j = i
    return inside


def point_in_polygon(lon: float, lat: float, geometry: dict[str, Any]) -> bool:
    if geometry.get("type") == "Polygon":
        polygons = [geometry.get("coordinates", [])]
    elif geometry.get("type") == "MultiPolygon":
        polygons = geometry.get("coordinates", [])
    else:
        return False

    for polygon in polygons:
        if not polygon:
            continue
        if point_in_ring(lon, lat, polygon[0]) and not any(point_in_ring(lon, lat, hole) for hole in polygon[1:]):
            return True
    return False
