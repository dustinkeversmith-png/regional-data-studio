import { HeatmapLayer } from "@deck.gl/aggregation-layers";
import type { AppState, LayerToggleState } from "../app/state";
import type { FirePoint, ProcessedData } from "../data/schemas";
import { filterFirePoints } from "../data/transforms";

export function createFireHeatmapLayer(
  data: ProcessedData,
  state: AppState,
  visibility: LayerToggleState,
) {
  if (!visibility.heatmap) {
    return null;
  }

  const points = filterFirePoints(data.firePoints, state.selectedYear, state.fireSeasonOnly);

  return new HeatmapLayer<FirePoint>({
    id: "firms-heatmap",
    data: points,
    getPosition: (point) => [point.longitude, point.latitude],
    getWeight: (point) => point.frp ?? 1,
    radiusPixels: 58,
    intensity: 1.2,
    threshold: 0.04,
  });
}
