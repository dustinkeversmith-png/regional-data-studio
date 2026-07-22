"""Fetch actual Oregon fire perimeters and county boundaries.

Primary perimeter source:
NIFC InterAgencyFirePerimeterHistory_All_Years_View FeatureServer.

County source:
US Census cartographic county boundaries filtered to Oregon.
"""

from __future__ import annotations

from typing import Any

from pipeline_common import (
    OREGON_BBOX,
    PROCESSED,
    bbox,
    ensure_dirs,
    fetch_json,
    int_value,
    number,
    write_geojson,
    years_from_env,
)


NIFC_PERIMETER_URL = (
    "https://services3.arcgis.com/T4QMspbfLg3qTGWY/ArcGIS/rest/services/"
    "InterAgencyFirePerimeterHistory_All_Years_View/FeatureServer/0/query"
)
CENSUS_COUNTIES_URL = "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip"
CENSUS_COUNTIES_GEOJSON_URL = (
    "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
)


def main() -> None:
    ensure_dirs()
    start_year, end_year = years_from_env()
    perimeters = fetch_perimeters(start_year, end_year)
    counties = fetch_counties()

    write_geojson(PROCESSED / "fire_perimeters_2016_2025.geojson", perimeters)
    write_geojson(PROCESSED / "oregon_counties.geojson", counties)

    print(f"Wrote {len(perimeters['features'])} fire perimeters for {start_year}-{end_year}")
    print(f"Wrote {len(counties['features'])} Oregon county features")


def fetch_perimeters(start_year: int, end_year: int) -> dict[str, Any]:
    all_features: list[dict[str, Any]] = []
    offset = 0
    page_size = 2000
    west, south, east, north = OREGON_BBOX

    while True:
        payload = fetch_json(
            NIFC_PERIMETER_URL,
            {
                "f": "geojson",
                "where": f"FIRE_YEAR_INT >= {start_year} AND FIRE_YEAR_INT <= {end_year}",
                "outFields": "*",
                "returnGeometry": "true",
                "outSR": "4326",
                "geometry": f"{west},{south},{east},{north}",
                "geometryType": "esriGeometryEnvelope",
                "spatialRel": "esriSpatialRelIntersects",
                "resultRecordCount": page_size,
                "resultOffset": offset,
            },
        )
        features = payload.get("features", [])
        all_features.extend(normalize_perimeter(feature) for feature in features if bbox(feature))
        if len(features) < page_size:
            break
        offset += page_size

    return {"type": "FeatureCollection", "features": all_features}


def normalize_perimeter(feature: dict[str, Any]) -> dict[str, Any]:
    props = feature.get("properties", {})
    year = int_value(props.get("FIRE_YEAR_INT") or props.get("FIRE_YEAR"))
    acres = number(
        props.get("GIS_ACRES")
        or props.get("ACRES")
        or props.get("FIRE_SIZE")
        or props.get("CalculatedAcres"),
        0,
    )
    fire_id = (
        props.get("UNQE_FIRE_ID")
        or props.get("IRWINID")
        or props.get("OBJECTID")
        or f"{props.get('INCIDENT', 'fire')}-{year}"
    )

    return {
        "type": "Feature",
        "geometry": feature.get("geometry"),
        "properties": {
            "fire_id": str(fire_id),
            "fire_name": props.get("INCIDENT") or props.get("FIRE_NAME") or props.get("IncidentName"),
            "year": year,
            "start_date": props.get("START_DATE") or props.get("ALARM_DATE") or props.get("DISCOVERY_DATE"),
            "end_date": props.get("END_DATE") or props.get("CONT_DATE") or props.get("OUT_DATE"),
            "acres": round(acres, 2) if acres else None,
            "source": "NIFC InterAgencyFirePerimeterHistory",
        },
    }


def fetch_counties() -> dict[str, Any]:
    payload = fetch_json(CENSUS_COUNTIES_GEOJSON_URL)
    features = []

    for feature in payload.get("features", []):
        props = feature.get("properties", {})
        if str(props.get("STATE") or props.get("STATEFP")) != "41":
            continue
        features.append(
            {
                "type": "Feature",
                "geometry": feature.get("geometry"),
                "properties": {
                    "county_name": props.get("NAME"),
                    "fire_count": 0,
                    "acres_burned": 0,
                    "active_fire_points": 0,
                    "mean_frp": 0,
                    "fire_density_per_sq_km": 0,
                },
            }
        )

    return {"type": "FeatureCollection", "features": features}


if __name__ == "__main__":
    main()
