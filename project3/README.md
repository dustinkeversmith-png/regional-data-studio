# Oregon AMOC Fire Visualizer

A standalone Vite + TypeScript visualization lab for exploring Oregon wildfire activity proxies alongside AMOC time-series data. MapLibre provides the Oregon map, deck.gl renders choropleth, FIRMS heatmap, generated hexbin, and perimeter panels, and ECharts renders AMOC/fire proxy comparison panels.

## Serving

Install dependencies:

```bash
npm install
```

Run the development server:

```bash
npm run dev
```

Vite is configured to serve on:

```txt
http://localhost:5173
```

Build and preview production assets:

```bash
npm run build
npm run preview
```

Preview serves on:

```txt
http://localhost:4173
```

## Current Milestone

- LOD zoomable MapLibre map centered on Oregon.
- Separate map panels for overview LOD, county choropleth, FIRMS heatmap, generated hex bins, and fire perimeters.
- Sidebar controls for year, layer toggles, metric selection, and fire-season filtering.
- AMOC vs Oregon fire proxy timeline.
- 10-year correlation summary and lag-analysis panel.
- Actual-data pipeline scripts that overwrite normalized files under `public/data/processed`.

## Data Contract

The app expects these processed files:

```txt
public/data/processed/oregon_counties.geojson
public/data/processed/fire_perimeters_2016_2025.geojson
public/data/processed/fire_points_2016_2025.csv
public/data/processed/county_fire_year_summary.csv
public/data/processed/hex_fire_year_summary.geojson
public/data/processed/amoc_monthly.csv
public/data/processed/fire_amoc_joined_monthly.csv
public/data/processed/fire_amoc_correlation_summary.json
```

## Actual Data Pipeline

The public no-key Oregon source can be fetched directly:

```bash
npm run data:fire
```

NASA FIRMS requires a free API key:

```bash
set FIRMS_MAP_KEY=your_key_here
npm run data:firms
```

AMOC requires a direct CSV export or URL because the official RAPID portal asks for contact details:

```bash
set AMOC_SOURCE_FILE=C:\path\to\rapid_amoc.csv
npm run data:amoc
```

or:

```bash
set AMOC_CSV_URL=https://example.org/amoc.csv
npm run data:amoc
```

After fire and AMOC inputs exist, join the monthly series and recompute correlations:

```bash
npm run data:join
```

Run the complete pipeline when both `FIRMS_MAP_KEY` and AMOC input are configured:

```bash
npm run data:pipeline
```

Useful optional settings:

```txt
START_YEAR=2016
END_YEAR=2025
FIRMS_SOURCES=VIIRS_SNPP_SP,VIIRS_NOAA20_SP
HEX_RADIUS_KM=18
```

## Scientific Caveat

This dashboard is exploratory only. AMOC is an Atlantic-scale ocean circulation indicator, while Oregon wildfire behavior is more directly shaped by Pacific/North American weather, drought, wind, fuels, humidity, topography, and ignition patterns. Annual acres burned, FIRMS detections, and FRP are labeled as fire activity or spread proxies, not true spread velocity unless time-resolved perimeter data is available.
