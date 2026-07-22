## 1-paragraph explanation

Build a standalone Oregon wildfire + AMOC visualization lab that loads Oregon GIS fire history, satellite fire detections, county/region boundaries, and optional Sentinel/Landsat raster tiles into a zoomable LOD map, then compares the last 10 years of Oregon fire spread metrics against AMOC-related time-series indicators. The important caveat is that this should be framed as an exploratory correlation dashboard, not a causal model: AMOC is Atlantic-scale ocean circulation, while Oregon fire spread is driven more directly by Pacific/North American weather, fuels, drought, wind, humidity, topography, and ignition patterns. Use the AMOC data as a climate-index comparison layer, then compute lagged correlations, rolling averages, and seasonal summaries to see whether any pattern is worth deeper research.

---

# Cursor Agent Build Plan: Oregon Fire + AMOC Visualization Lab

## Goal

Create a standalone web visualization app with:

1. **LOD zoomable Oregon map**
2. **Satellite / GIS wildfire data**
3. **Choropleth map**
4. **Heatmap**
5. **Hexagonal binning**
6. **AMOC + fire spread time-series comparison**
7. **Last 10 years correlation / lag analysis**

Recommended stack:

```txt
frontend: Vite + TypeScript
map: MapLibre GL JS
deck.gl: HexagonLayer, HeatmapLayer, GeoJsonLayer
charts: Apache ECharts or Observable Plot
processing: Python scripts or Node geospatial pipeline
data format: GeoJSON / PMTiles / Parquet / CSV
```

---

## Data sources to use

### Oregon wildfire data

Use these first:

* **Oregon Fire Perimeter History 2000–2024**, which aggregates interagency fire perimeter history and WFIGS 2024 perimeters. ([Oregon Explorer][1])
* **ODF Fire Occurrence GIS data**, because Oregon Department of Forestry explicitly provides downloadable GIS fire occurrence data and fire history dashboards. ([Oregon][2])
* **ODF Fire History Maps & Charts 2000–2025**, useful for validating annual acres burned totals. ([Oregon Data][3])
* Optional: **BLM OR Fire Poly**, which includes fire history polygons for BLM fires 10 acres or larger across Oregon and Washington. ([Data.gov][4])

### Satellite fire / raster data

Use these for satellite-backed layers:

* **NASA FIRMS MODIS / VIIRS active fire data**, which provides satellite observations of active fires and thermal anomalies, including near-real-time and downloadable products. ([NASA FIRMS][5])
* **FIRMS active fire downloads** for MODIS, VIIRS, and Landsat active fire products. ([NASA FIRMS][6])
* **Landsat Collection 2 Level-2**, which includes surface reflectance and surface temperature products useful for burned area, vegetation, and heat context. ([USGS][7])
* **Earth Search STAC API**, a free STAC catalog for public geospatial datasets on AWS, including Sentinel/Landsat-style access patterns. ([GitHub][8])

### AMOC data

Use:

* **RAPID/MOCHA/WBTS AMOC observations at 26°N**, the standard directly observed AMOC transport time series. ([Rapid][9])
* **RAPID data download portal**, which provides AMOC transports and profile datasets. ([Rapid][10])
* **NOAA Physical Sciences Laboratory climate indices**, as a fallback/comparison source for related climate indices if direct AMOC data is inconvenient. ([NOAA Physical Sciences Laboratory][11])

---

# Project structure

```txt
oregon-amoc-fire-visualizer/
│
├── package.json
├── vite.config.ts
├── index.html
├── README.md
│
├── public/
│   ├── data/
│   │   ├── processed/
│   │   │   ├── oregon_counties.geojson
│   │   │   ├── fire_perimeters_2016_2025.geojson
│   │   │   ├── fire_points_2016_2025.parquet
│   │   │   ├── county_fire_year_summary.csv
│   │   │   ├── hex_fire_year_summary.geojson
│   │   │   ├── amoc_monthly.csv
│   │   │   └── fire_amoc_joined_monthly.csv
│   │   └── tiles/
│   │       ├── fire_perimeters.pmtiles
│   │       └── satellite_context.pmtiles
│
├── scripts/
│   ├── fetch_oregon_fire_data.py
│   ├── fetch_firms_satellite_fire.py
│   ├── fetch_amoc_data.py
│   ├── process_fire_metrics.py
│   ├── build_hex_bins.py
│   ├── build_choropleth_summary.py
│   ├── join_fire_amoc_timeseries.py
│   └── build_pmtiles.sh
│
└── src/
    ├── main.ts
    ├── app/
    │   ├── App.ts
    │   ├── state.ts
    │   └── config.ts
    │
    ├── map/
    │   ├── createMap.ts
    │   ├── baseLayers.ts
    │   ├── lodSources.ts
    │   └── layerController.ts
    │
    ├── layers/
    │   ├── ChoroplethLayer.ts
    │   ├── FireHeatmapLayer.ts
    │   ├── FireHexbinLayer.ts
    │   ├── FirePerimeterLayer.ts
    │   ├── SatelliteRasterLayer.ts
    │   └── OregonBoundaryLayer.ts
    │
    ├── charts/
    │   ├── AmocFireTimeline.ts
    │   ├── CorrelationPanel.ts
    │   ├── LagAnalysisPanel.ts
    │   └── YearSummaryPanel.ts
    │
    ├── data/
    │   ├── loaders.ts
    │   ├── schemas.ts
    │   └── transforms.ts
    │
    └── ui/
        ├── Sidebar.ts
        ├── LayerToggles.ts
        ├── TimeSlider.ts
        ├── Legend.ts
        └── Tooltip.ts
```

---

# Implementation phases for Cursor

## Phase 1: Scaffold the standalone app

Tell Cursor:

```txt
Create a Vite + TypeScript app called oregon-amoc-fire-visualizer.

Install:
- maplibre-gl
- deck.gl
- @deck.gl/layers
- @deck.gl/mapbox
- d3
- echarts
- apache-arrow or parquet-wasm if using parquet
- h3-js or d3-hexbin

Create a single-page layout:
- full-screen map
- left sidebar
- bottom time-series chart panel
- top-right layer toggles
- bottom-left legend
```

The initial UI should have these toggles:

```ts
type LayerToggleState = {
  choropleth: boolean;
  heatmap: boolean;
  hexbin: boolean;
  firePerimeters: boolean;
  satelliteContext: boolean;
  countyBoundaries: boolean;
};
```

---

## Phase 2: Build the LOD zoomable map

Use MapLibre for the base map and deck.gl for data overlays.

LOD behavior:

```txt
zoom 0–5:
  show Oregon state outline and annual fire summary only

zoom 5–7:
  show county choropleth by acres burned / fire count

zoom 7–10:
  show fire perimeter polygons and heatmap

zoom 10+:
  show FIRMS active fire points, hex bins, satellite context tiles
```

Cursor task:

```txt
Implement createMap.ts with MapLibre centered on Oregon.

Initial view:
longitude: -120.5542
latitude: 43.8041
zoom: 5.7

Add a layerController that listens to zoom changes and updates which layers are visible.
```

---

## Phase 3: Data ingestion scripts

Create Python scripts that output normalized files into:

```txt
public/data/processed/
```

### Fire perimeter schema

```ts
type FirePerimeterFeature = {
  type: "Feature";
  geometry: Polygon | MultiPolygon;
  properties: {
    fire_id: string;
    fire_name: string | null;
    year: number;
    start_date: string | null;
    end_date: string | null;
    acres: number | null;
    source: string;
  };
};
```

### FIRMS satellite point schema

```ts
type FirePoint = {
  latitude: number;
  longitude: number;
  acq_date: string;
  acq_time?: string;
  year: number;
  month: number;
  brightness?: number;
  frp?: number;
  confidence?: string | number;
  satellite?: string;
  instrument?: "MODIS" | "VIIRS" | "Landsat" | string;
};
```

### AMOC schema

```ts
type AmocMonthlyRow = {
  date: string;
  year: number;
  month: number;
  amoc_transport_sv: number;
  amoc_anomaly_sv?: number;
  source: "RAPID" | "NOAA_PSL" | "derived";
};
```

### Joined fire-AMOC schema

```ts
type FireAmocMonthlyRow = {
  date: string;
  year: number;
  month: number;

  amoc_transport_sv: number;
  amoc_anomaly_sv?: number;

  oregon_fire_count: number;
  oregon_active_fire_points: number;
  oregon_acres_burned_estimate: number;
  mean_frp: number | null;
  max_frp: number | null;

  rolling_3mo_fire_points: number;
  rolling_12mo_fire_points: number;
  rolling_12mo_amoc: number;
};
```

---

## Phase 4: Build core fire metrics

Cursor should implement:

```txt
process_fire_metrics.py
```

It should compute:

```txt
annual_fire_count
annual_acres_burned
monthly_fire_point_count
monthly_mean_frp
monthly_max_frp
county_fire_count
county_acres_burned
fire_spread_proxy
```

For “fire spread,” avoid pretending we know exact daily spread unless the perimeter dataset has time-stepped perimeters. Use proxies:

```txt
spread_proxy_1 = annual acres burned
spread_proxy_2 = monthly active fire detections
spread_proxy_3 = fire radiative power sum
spread_proxy_4 = perimeter area / duration when start/end dates exist
```

Important note for Cursor:

```txt
Do not label annual acres burned as true spread velocity.
Use “spread proxy” unless time-resolved fire perimeters are available.
```

---

## Phase 5: Choropleth map

Purpose:

```txt
Show fire burden by Oregon county or ecological region.
```

Layer input:

```txt
county_fire_year_summary.csv
oregon_counties.geojson
```

Join key:

```txt
county_name
```

Metrics selectable in UI:

```ts
type ChoroplethMetric =
  | "fire_count"
  | "acres_burned"
  | "active_fire_points"
  | "mean_frp"
  | "fire_density_per_sq_km";
```

Cursor task:

```txt
Create ChoroplethLayer.ts using deck.gl GeoJsonLayer.
Color counties by selected metric.
Add tooltip with county, year, fire_count, acres_burned, active_fire_points, mean_frp.
Add legend bins.
```

---

## Phase 6: Heatmap

Purpose:

```txt
Show intensity of satellite-detected fire activity.
```

Layer input:

```txt
fire_points_2016_2025.parquet or fire_points_2016_2025.csv
```

Heatmap weight options:

```ts
type HeatmapWeight =
  | "point_count"
  | "brightness"
  | "frp"
  | "confidence_weighted";
```

Cursor task:

```txt
Create FireHeatmapLayer.ts using deck.gl HeatmapLayer.
Filter points by selected year/month range.
Use FRP as default weight when available.
Fallback to 1 per point.
```

---

## Phase 7: Hexagonal binning

Purpose:

```txt
Show spatial aggregation of fire detections without relying on county boundaries.
```

Two valid implementation options:

### Option A: deck.gl HexagonLayer

Best for frontend-only experiments.

```txt
Use deck.gl HexagonLayer.
Radius changes by zoom.
Elevation = active fire count or summed FRP.
Color = active fire count or summed FRP.
```

### Option B: H3 precomputed bins

Best for stable reproducible analysis.

```txt
Use h3-js or Python h3.
Convert each fire point to H3 cell.
Aggregate by year/month/resolution.
Export hex_fire_year_summary.geojson.
```

Recommended H3 resolutions:

```txt
state overview: H3 res 4
regional: H3 res 5
local: H3 res 6 or 7
```

Cursor task:

```txt
Create build_hex_bins.py that aggregates FIRMS points into H3 cells.
Output hex_fire_year_summary.geojson with:
- h3_index
- year
- month
- fire_point_count
- sum_frp
- mean_brightness
```

---

## Phase 8: AMOC + fire spread timeline

Create a chart with:

```txt
x-axis: month/year
left y-axis: Oregon fire metric
right y-axis: AMOC transport / anomaly
```

User-selectable fire metrics:

```ts
type FireTimelineMetric =
  | "monthly_fire_points"
  | "monthly_sum_frp"
  | "monthly_acres_burned_estimate"
  | "rolling_12mo_fire_points";
```

User-selectable AMOC metrics:

```ts
type AmocMetric =
  | "amoc_transport_sv"
  | "amoc_anomaly_sv"
  | "rolling_12mo_amoc";
```

Cursor task:

```txt
Create AmocFireTimeline.ts using ECharts.
Plot AMOC line and Oregon fire metric line.
Add brushing to filter the map by selected time range.
Add 3-month and 12-month rolling-average toggles.
```

---

## Phase 9: Last 10 years relation analysis

Create:

```txt
CorrelationPanel.ts
LagAnalysisPanel.ts
```

Metrics to compute:

```txt
Pearson correlation
Spearman correlation
lagged Pearson correlation
lagged Spearman correlation
cross-correlation from -24 to +24 months
seasonal correlation for fire season months only
```

Recommended Oregon fire season filter:

```txt
June–October
```

Cursor task:

```txt
Implement join_fire_amoc_timeseries.py.

For years 2016–2025:
- join monthly Oregon fire metrics to monthly AMOC metrics
- compute rolling 3-month and 12-month means
- compute correlations
- compute lag correlations from -24 to +24 months
- output fire_amoc_joined_monthly.csv
- output fire_amoc_correlation_summary.json
```

Use this interpretation text in the UI:

```txt
This panel measures exploratory statistical relationships between AMOC time-series changes and Oregon wildfire activity proxies. It does not prove AMOC causes Oregon fire spread. Strong apparent correlations should be checked against drought, temperature, wind, precipitation, ENSO, PDO, fuel moisture, and ignition variables.
```

---

# Suggested visualization behavior

## Sidebar controls

```txt
Time range:
- year slider
- month range
- fire season only toggle

Map layers:
- choropleth
- heatmap
- hexbin
- fire perimeters
- satellite context
- county boundaries

Metrics:
- acres burned
- fire count
- active fire detections
- FRP
- brightness
- AMOC transport
- AMOC anomaly
```

## Tooltips

For counties:

```txt
County: Jackson
Year: 2021
Fire count: 42
Acres burned: 18,230
FIRMS detections: 1,244
Mean FRP: 37.2
```

For hex bins:

```txt
H3 cell: 85283473fffffff
Month: 2021-08
Fire detections: 84
Sum FRP: 2,943
Mean brightness: 328.5 K
```

For fire perimeter:

```txt
Fire: Bootleg Fire
Year: 2021
Acres: 413,000
Source: Interagency perimeter history
```

---

# Cursor instructions: exact task prompt

You can paste this into Cursor:

```txt
Build a standalone Vite + TypeScript web app called oregon-amoc-fire-visualizer.

The app visualizes Oregon wildfire activity and compares it to AMOC time-series data.

Use MapLibre GL JS for the base map and deck.gl for overlays.

Implement these map layers:
1. Choropleth map by Oregon county or region.
2. Heatmap from satellite active fire points.
3. Hexagonal binning from satellite active fire points.
4. Fire perimeter polygons.
5. Optional satellite/raster context layer.

Implement these chart panels:
1. AMOC vs Oregon fire metric timeline.
2. Last 10 years correlation summary.
3. Lag analysis from -24 to +24 months.

Use normalized data files from public/data/processed:
- oregon_counties.geojson
- fire_perimeters_2016_2025.geojson
- fire_points_2016_2025.csv or parquet
- county_fire_year_summary.csv
- hex_fire_year_summary.geojson
- amoc_monthly.csv
- fire_amoc_joined_monthly.csv
- fire_amoc_correlation_summary.json

Create scripts in /scripts:
- fetch_oregon_fire_data.py
- fetch_firms_satellite_fire.py
- fetch_amoc_data.py
- process_fire_metrics.py
- build_hex_bins.py
- build_choropleth_summary.py
- join_fire_amoc_timeseries.py

Important modeling rule:
Do not claim AMOC causes Oregon fire spread. Label annual acres burned, FIRMS detections, and FRP as fire spread proxies unless time-resolved perimeter evolution data exists.

LOD map behavior:
- zoom 0–5: Oregon outline and annual summary only
- zoom 5–7: county choropleth
- zoom 7–10: fire perimeters and heatmap
- zoom 10+: FIRMS points, hex bins, satellite context

Use clean modular files:
src/map
src/layers
src/charts
src/data
src/ui

Add README explaining data sources, how to run scripts, how to run the app, and the scientific caveat.
```

---

# Recommended first milestone

Have Cursor build a **mock-data version first**:

```txt
Milestone 1:
- MapLibre Oregon map
- mock county GeoJSON choropleth
- mock FIRMS points
- mock hexbin layer
- mock AMOC/fire timeline
- mock correlation panel
```

Then replace mock data with real data in Milestone 2. This prevents the project from getting blocked by data access, API keys, or geospatial cleanup.

[1]: https://hub.oregonexplorer.info/maps/848594cad4554eb9a1965e744d707494?utm_source=chatgpt.com "Oregon Fire Perimeter History (2000-2024)"
[2]: https://www.oregon.gov/odf/fire/pages/firestats.aspx?utm_source=chatgpt.com "Oregon Department of Forestry : Information & statistics : Fire"
[3]: https://data.oregon.gov/stories/s/ODF-and-Oregon-Fire-History-Maps-Charts/fyph-mr4s/?utm_source=chatgpt.com "ODF and Oregon Fire History Maps & Charts"
[4]: https://catalog.data.gov/dataset/?tags=perimeter&utm_source=chatgpt.com "perimeter - Dataset - Catalog - Data.gov"
[5]: https://firms.modaps.eosdis.nasa.gov/?utm_source=chatgpt.com "NASA | LANCE | FIRMS"
[6]: https://firms.modaps.eosdis.nasa.gov/active_fire/?utm_source=chatgpt.com "LANCE | FIRMS - Active Fire Data"
[7]: https://www.usgs.gov/landsat-missions/landsat-collection-2?utm_source=chatgpt.com "Landsat Collection 2 | U.S. Geological Survey"
[8]: https://github.com/Element84/earth-search?utm_source=chatgpt.com "Earth Search STAC API"
[9]: https://rapid.ac.uk/?utm_source=chatgpt.com "Rapid |"
[10]: https://rapid.ac.uk/data/data-download?utm_source=chatgpt.com "Data Download"
[11]: https://psl.noaa.gov/data/climateindices/list/?utm_source=chatgpt.com "Climate Indices: Monthly Atmospheric and Ocean Time Series"
