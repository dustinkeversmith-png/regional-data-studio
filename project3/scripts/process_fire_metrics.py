"""Compute Oregon fire activity metrics from normalized perimeter and FIRMS data."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from pipeline_common import (
    PROCESSED,
    bbox_center,
    int_value,
    number,
    point_in_polygon,
    read_csv,
    read_geojson,
    write_csv,
    years_from_env,
)


MONTHLY_FIELDS = [
    "date",
    "year",
    "month",
    "oregon_fire_count",
    "oregon_active_fire_points",
    "oregon_acres_burned_estimate",
    "mean_frp",
    "max_frp",
    "monthly_fire_points",
    "monthly_sum_frp",
    "monthly_acres_burned_estimate",
]

COUNTY_FIELDS = [
    "county_name",
    "year",
    "fire_count",
    "acres_burned",
    "active_fire_points",
    "mean_frp",
    "fire_density_per_sq_km",
]


def main() -> None:
    start_year, end_year = years_from_env()
    perimeters = read_geojson(PROCESSED / "fire_perimeters_2016_2025.geojson").get("features", [])
    fire_points = read_csv(PROCESSED / "fire_points_2016_2025.csv")
    counties = read_geojson(PROCESSED / "oregon_counties.geojson").get("features", [])

    monthly = build_monthly_metrics(perimeters, fire_points, start_year, end_year)
    county = build_county_metrics(perimeters, fire_points, counties, start_year, end_year)

    write_csv(PROCESSED / "monthly_fire_metrics.csv", monthly, MONTHLY_FIELDS)
    write_csv(PROCESSED / "county_fire_year_summary.csv", county, COUNTY_FIELDS)

    print(f"Wrote {len(monthly)} monthly fire metric rows")
    print(f"Wrote {len(county)} county/year summary rows")


def build_monthly_metrics(
    perimeters: list[dict[str, Any]],
    fire_points: list[dict[str, str]],
    start_year: int,
    end_year: int,
) -> list[dict[str, Any]]:
    monthly_points: dict[tuple[int, int], list[dict[str, str]]] = defaultdict(list)
    for point in fire_points:
        year = int_value(point.get("year"))
        month = int_value(point.get("month"))
        if start_year <= year <= end_year:
            monthly_points[(year, month)].append(point)

    monthly_perimeters: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for perimeter in perimeters:
        props = perimeter.get("properties", {})
        year = int_value(props.get("year"))
        if start_year <= year <= end_year:
            # Perimeters usually have final acreage but not month-resolved growth.
            monthly_perimeters[(year, 8)].append(perimeter)

    rows: list[dict[str, Any]] = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            points = monthly_points.get((year, month), [])
            perims = monthly_perimeters.get((year, month), [])
            frps = [number(point.get("frp")) for point in points if number(point.get("frp")) > 0]
            acres = sum(number(perim.get("properties", {}).get("acres")) for perim in perims)
            point_count = len(points)
            sum_frp = sum(frps)
            rows.append(
                {
                    "date": f"{year:04d}-{month:02d}",
                    "year": year,
                    "month": month,
                    "oregon_fire_count": len(perims),
                    "oregon_active_fire_points": point_count,
                    "oregon_acres_burned_estimate": round(acres, 2),
                    "mean_frp": round(sum_frp / len(frps), 4) if frps else "",
                    "max_frp": round(max(frps), 4) if frps else "",
                    "monthly_fire_points": point_count,
                    "monthly_sum_frp": round(sum_frp, 4),
                    "monthly_acres_burned_estimate": round(acres, 2),
                }
            )

    return rows


def build_county_metrics(
    perimeters: list[dict[str, Any]],
    fire_points: list[dict[str, str]],
    counties: list[dict[str, Any]],
    start_year: int,
    end_year: int,
) -> list[dict[str, Any]]:
    metrics: dict[tuple[str, int], dict[str, Any]] = defaultdict(
        lambda: {"fire_count": 0, "acres_burned": 0.0, "active_fire_points": 0, "frps": []}
    )

    for perimeter in perimeters:
        props = perimeter.get("properties", {})
        year = int_value(props.get("year"))
        if not (start_year <= year <= end_year):
            continue
        center = bbox_center(perimeter)
        county = county_for_point(center, counties) if center else None
        if not county:
            continue
        record = metrics[(county, year)]
        record["fire_count"] += 1
        record["acres_burned"] += number(props.get("acres"))

    for point in fire_points:
        year = int_value(point.get("year"))
        if not (start_year <= year <= end_year):
            continue
        county = county_for_point((number(point.get("longitude")), number(point.get("latitude"))), counties)
        if not county:
            continue
        record = metrics[(county, year)]
        record["active_fire_points"] += 1
        frp = number(point.get("frp"))
        if frp > 0:
            record["frps"].append(frp)

    rows: list[dict[str, Any]] = []
    for county in sorted({feature.get("properties", {}).get("county_name") for feature in counties if feature.get("properties")}):
        if not county:
            continue
        for year in range(start_year, end_year + 1):
            record = metrics[(county, year)]
            frps = record["frps"]
            rows.append(
                {
                    "county_name": county,
                    "year": year,
                    "fire_count": record["fire_count"],
                    "acres_burned": round(record["acres_burned"], 2),
                    "active_fire_points": record["active_fire_points"],
                    "mean_frp": round(sum(frps) / len(frps), 4) if frps else "",
                    "fire_density_per_sq_km": "",
                }
            )
    return rows


def county_for_point(point: tuple[float, float], counties: list[dict[str, Any]]) -> str | None:
    lon, lat = point
    for county in counties:
        if point_in_polygon(lon, lat, county.get("geometry", {})):
            return county.get("properties", {}).get("county_name")
    return None


if __name__ == "__main__":
    main()
