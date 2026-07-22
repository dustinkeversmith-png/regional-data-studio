import type { FireTimelineMetric, ChoroplethMetric, AmocMetric } from "../data/schemas";

export type LayerToggleState = {
  choropleth: boolean;
  heatmap: boolean;
  hexbin: boolean;
  firePerimeters: boolean;
  satelliteContext: boolean;
  countyBoundaries: boolean;
};

export type MapPanel = "overview" | "choropleth" | "heatmap" | "hexbin" | "perimeters";

export type AppState = {
  selectedYear: number;
  fireSeasonOnly: boolean;
  activeMapPanel: MapPanel;
  choroplethMetric: ChoroplethMetric;
  fireTimelineMetric: FireTimelineMetric;
  amocMetric: AmocMetric;
  toggles: LayerToggleState;
};

export const defaultState: AppState = {
  selectedYear: 2021,
  fireSeasonOnly: true,
  activeMapPanel: "overview",
  choroplethMetric: "acres_burned",
  fireTimelineMetric: "monthly_fire_points",
  amocMetric: "amoc_anomaly_sv",
  toggles: {
    choropleth: true,
    heatmap: true,
    hexbin: true,
    firePerimeters: true,
    satelliteContext: false,
    countyBoundaries: true,
  },
};
