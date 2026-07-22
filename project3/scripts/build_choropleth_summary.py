"""Join county summary metrics into Oregon county GeoJSON."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from pipeline_common import PROCESSED, number, read_csv, read_geojson, write_geojson


def main() -> None:
    counties = read_geojson(PROCESSED / "oregon_counties.geojson")
    summary = read_csv(PROCESSED / "county_fire_year_summary.csv")
    aggregates = aggregate_summary(summary)

    for feature in counties.get("features", []):
        county = feature.get("properties", {}).get("county_name")
        aggregate = aggregates.get(county, empty_aggregate())
        feature["properties"] = {
            **feature.get("properties", {}),
            "fire_count": int(aggregate["fire_count"]),
            "acres_burned": round(aggregate["acres_burned"], 2),
            "active_fire_points": int(aggregate["active_fire_points"]),
            "mean_frp": round(aggregate["frp_sum"] / aggregate["frp_count"], 4) if aggregate["frp_count"] else 0,
            "fire_density_per_sq_km": round(aggregate["active_fire_points"] / 1000, 4),
        }

    write_geojson(PROCESSED / "oregon_counties.geojson", counties)
    print(f"Updated {len(counties.get('features', []))} choropleth county features")


def aggregate_summary(rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    aggregates: dict[str, dict[str, Any]] = defaultdict(empty_aggregate)
    for row in rows:
        county = row.get("county_name")
        if not county:
            continue
        aggregate = aggregates[county]
        aggregate["fire_count"] += number(row.get("fire_count"))
        aggregate["acres_burned"] += number(row.get("acres_burned"))
        aggregate["active_fire_points"] += number(row.get("active_fire_points"))
        frp = number(row.get("mean_frp"))
        if frp > 0:
            aggregate["frp_sum"] += frp
            aggregate["frp_count"] += 1
    return aggregates


def empty_aggregate() -> dict[str, Any]:
    return {
        "fire_count": 0,
        "acres_burned": 0.0,
        "active_fire_points": 0,
        "frp_sum": 0.0,
        "frp_count": 0,
    }


if __name__ == "__main__":
    main()
