import { GeoJsonLayer } from "@deck.gl/layers";
import type { LayerToggleState } from "../app/state";
import type { ProcessedData } from "../data/schemas";

export function createSatelliteRasterLayer(data: ProcessedData, visibility: LayerToggleState) {
  if (!visibility.satelliteContext) {
    return null;
  }

  return new GeoJsonLayer({
    id: "satellite-context-placeholder",
    data: data.perimeters.features,
    filled: true,
    stroked: false,
    pickable: false,
    getFillColor: [22, 163, 74, 38],
  });
}
