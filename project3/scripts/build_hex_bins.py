"""Aggregate FIRMS detections into reproducible hex-bin GeoJSON.

This uses a lightweight lon/lat hex grid so it has no Python dependency beyond
the standard library. The frontend can still render live deck.gl HexagonLayer,
while this file gives the pipeline a stable precomputed hex product.
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

from pipeline_common import PROCESSED, get_env, number, read_csv, write_geojson, years_from_env


def main() -> None:
    start_year, end_year = years_from_env()
    radius_km = float(get_env("HEX_RADIUS_KM", "18") or 18)
    points = read_csv(PROCESSED / "fire_points_2016_2025.csv")
    features = build_hex_features(points, start_year, end_year, radius_km)
    write_geojson(PROCESSED / "hex_fire_year_summary.geojson", {"type": "FeatureCollection", "features": features})
    print(f"Wrote {len(features)} hex-bin features")


def build_hex_features(
    points: list[dict[str, str]],
    start_year: int,
    end_year: int,
    radius_km: float,
) -> list[dict[str, Any]]:
    bins: dict[tuple[int, int, int, int], dict[str, Any]] = defaultdict(
        lambda: {"count": 0, "sum_frp": 0.0, "brightness_sum": 0.0, "brightness_count": 0}
    )

    for point in points:
        year = int(number(point.get("year")))
        month = int(number(point.get("month")))
        if not (start_year <= year <= end_year):
            continue
        lon = number(point.get("longitude"))
        lat = number(point.get("latitude"))
        q, r = hex_cell(lon, lat, radius_km)
        record = bins[(year, month, q, r)]
        record["count"] += 1
        record["sum_frp"] += number(point.get("frp"))
        brightness = number(point.get("brightness"))
        if brightness > 0:
            record["brightness_sum"] += brightness
            record["brightness_count"] += 1

    features: list[dict[str, Any]] = []
    for (year, month, q, r), record in sorted(bins.items()):
        center_lon, center_lat = hex_center(q, r, radius_km)
        mean_brightness = (
            record["brightness_sum"] / record["brightness_count"] if record["brightness_count"] else 0
        )
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "h3_index": f"hex_{radius_km:g}km_{q}_{r}",
                    "year": year,
                    "month": month,
                    "fire_point_count": record["count"],
                    "sum_frp": round(record["sum_frp"], 4),
                    "mean_brightness": round(mean_brightness, 4),
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [hex_polygon(center_lon, center_lat, radius_km)],
                },
            }
        )

    return features


def hex_cell(lon: float, lat: float, radius_km: float) -> tuple[int, int]:
    x = lon_to_km(lon, lat)
    y = lat_to_km(lat)
    q = (math.sqrt(3) / 3 * x - 1 / 3 * y) / radius_km
    r = (2 / 3 * y) / radius_km
    return cube_round(q, r)


def hex_center(q: int, r: int, radius_km: float) -> tuple[float, float]:
    x = radius_km * math.sqrt(3) * (q + r / 2)
    y = radius_km * 1.5 * r
    lat = y / 111.32
    lon = x / (111.32 * math.cos(math.radians(max(min(lat, 89), -89))))
    return lon, lat


def cube_round(q: float, r: float) -> tuple[int, int]:
    x = q
    z = r
    y = -x - z
    rx, ry, rz = round(x), round(y), round(z)
    x_diff, y_diff, z_diff = abs(rx - x), abs(ry - y), abs(rz - z)
    if x_diff > y_diff and x_diff > z_diff:
        rx = -ry - rz
    elif y_diff > z_diff:
        ry = -rx - rz
    else:
        rz = -rx - ry
    return int(rx), int(rz)


def hex_polygon(lon: float, lat: float, radius_km: float) -> list[list[float]]:
    coords: list[list[float]] = []
    for index in range(6):
        angle = math.radians(60 * index - 30)
        dx = radius_km * math.cos(angle)
        dy = radius_km * math.sin(angle)
        coords.append([lon + km_to_lon(dx, lat), lat + dy / 111.32])
    coords.append(coords[0])
    return coords


def lon_to_km(lon: float, lat: float) -> float:
    return lon * 111.32 * math.cos(math.radians(max(min(lat, 89), -89)))


def lat_to_km(lat: float) -> float:
    return lat * 111.32


def km_to_lon(km: float, lat: float) -> float:
    return km / (111.32 * math.cos(math.radians(max(min(lat, 89), -89))))


if __name__ == "__main__":
    main()
