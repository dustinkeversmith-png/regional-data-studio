import { GeoJsonLayer } from "@deck.gl/layers";
import type { AppState, LayerToggleState } from "../app/state";
import type { ProcessedData } from "../data/schemas";
import { countyColor } from "../data/transforms";

export function createChoroplethLayer(
  data: ProcessedData,
  state: AppState,
  visibility: LayerToggleState,
) {
  if (!visibility.choropleth) {
    return null;
  }

  return new GeoJsonLayer({
    id: "county-choropleth",
    data: data.counties.features,
    filled: true,
    stroked: true,
    pickable: true,
    getFillColor: (feature) => countyColor(feature as never, state.choroplethMetric),
    getLineColor: [214, 255, 236, 155],
    getLineWidth: 900,
    lineWidthMinPixels: 1,
    autoHighlight: true,
    highlightColor: [255, 255, 255, 70],
  });
}
