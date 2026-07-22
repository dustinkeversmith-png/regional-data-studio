import { GeoJsonLayer } from "@deck.gl/layers";
import type { LayerToggleState } from "../app/state";
import type { CountyFeature, ProcessedData } from "../data/schemas";

export function createCountyBoundaryLayer(data: ProcessedData, visibility: LayerToggleState) {
  if (!visibility.countyBoundaries) {
    return null;
  }

  return new GeoJsonLayer<CountyFeature>({
    id: "oregon-county-boundaries",
    data: data.counties.features,
    filled: false,
    stroked: true,
    pickable: false,
    getLineColor: [209, 250, 229, 210],
    getLineWidth: 450,
    lineWidthMinPixels: 0.8,
  });
}
