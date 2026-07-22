import { GeoJsonLayer } from "@deck.gl/layers";
import type { AppState, LayerToggleState } from "../app/state";
import type { ProcessedData } from "../data/schemas";

export function createFirePerimeterLayer(
  data: ProcessedData,
  state: AppState,
  visibility: LayerToggleState,
) {
  if (!visibility.firePerimeters) {
    return null;
  }

  const perimeters = data.perimeters.features.filter(
    (feature) => feature.properties.year === state.selectedYear,
  );

  return new GeoJsonLayer({
    id: "fire-perimeters",
    data: perimeters,
    filled: true,
    stroked: true,
    pickable: true,
    getFillColor: [248, 113, 22, 90],
    getLineColor: [255, 247, 237, 220],
    getLineWidth: 700,
    lineWidthMinPixels: 1,
  });
}
