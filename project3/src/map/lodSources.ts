import type { LayerToggleState } from "../app/state";
import { zoomBand } from "./baseLayers";

export function resolveLodVisibility(zoom: number, toggles: LayerToggleState): LayerToggleState {
  const band = zoomBand(zoom);

  return {
    choropleth: toggles.choropleth && (band === "county" || band === "state"),
    heatmap: toggles.heatmap && (band === "fire" || band === "local"),
    hexbin: toggles.hexbin && band === "local",
    firePerimeters: toggles.firePerimeters && (band === "fire" || band === "local"),
    satelliteContext: toggles.satelliteContext && band === "local",
    countyBoundaries: toggles.countyBoundaries,
  };
}
