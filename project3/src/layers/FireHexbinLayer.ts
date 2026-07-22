import { GeoJsonLayer } from "@deck.gl/layers";
import type { AppState, LayerToggleState } from "../app/state";
import type { HexFireFeature, ProcessedData } from "../data/schemas";

export function createFireHexbinLayer(
  data: ProcessedData,
  state: AppState,
  visibility: LayerToggleState,
) {
  if (!visibility.hexbin) {
    return null;
  }

  const hexes = data.hexes.features.filter((feature) => {
    const inSeason = !state.fireSeasonOnly || (feature.properties.month >= 6 && feature.properties.month <= 10);
    return feature.properties.year === state.selectedYear && inSeason;
  });

  return new GeoJsonLayer({
    id: "fire-hexbin-precomputed",
    data: hexes,
    filled: true,
    stroked: true,
    pickable: true,
    getFillColor: (feature) => hexColor((feature as HexFireFeature).properties.sum_frp),
    getLineColor: [255, 247, 237, 170],
    getLineWidth: 450,
    lineWidthMinPixels: 0.7,
  });
}

function hexColor(sumFrp: number): [number, number, number, number] {
  if (sumFrp > 8000) return [185, 28, 28, 175];
  if (sumFrp > 3500) return [249, 115, 22, 160];
  if (sumFrp > 1000) return [250, 204, 21, 145];
  return [20, 184, 166, 125];
}
