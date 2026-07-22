import type { IControl, Map as MapLibreMap } from "maplibre-gl";
import type { Layer } from "@deck.gl/core";
import { MapboxOverlay } from "@deck.gl/mapbox";
import type { AppState } from "../app/state";
import type { ProcessedData } from "../data/schemas";
import type { LayerToggleState } from "../app/state";
import { resolveLodVisibility } from "./lodSources";
import { createChoroplethLayer } from "../layers/ChoroplethLayer";
import { createCountyBoundaryLayer } from "../layers/OregonBoundaryLayer";
import { createFireHeatmapLayer } from "../layers/FireHeatmapLayer";
import { createFireHexbinLayer } from "../layers/FireHexbinLayer";
import { createFirePerimeterLayer } from "../layers/FirePerimeterLayer";
import { createSatelliteRasterLayer } from "../layers/SatelliteRasterLayer";

export class LayerController {
  private overlay: MapboxOverlay;

  constructor(private map: MapLibreMap) {
    this.overlay = new MapboxOverlay({
      interleaved: false,
      layers: [],
      getTooltip: ({ object }: { object?: any }) => formatTooltip(object),
    });
    this.map.addControl(this.overlay as unknown as IControl);
  }

  update(data: ProcessedData, state: AppState) {
    const zoom = this.map.getZoom();
    const visibility = resolvePanelVisibility(resolveLodVisibility(zoom, state.toggles), state);
    const layers: Layer[] = [
      createSatelliteRasterLayer(data, visibility),
      createChoroplethLayer(data, state, visibility),
      createCountyBoundaryLayer(data, visibility),
      createFirePerimeterLayer(data, state, visibility),
      createFireHeatmapLayer(data, state, visibility),
      createFireHexbinLayer(data, state, visibility),
    ].filter(Boolean) as Layer[];

    this.overlay.setProps({ layers });
  }
}

function resolvePanelVisibility(lodVisibility: LayerToggleState, state: AppState): LayerToggleState {
  if (state.activeMapPanel === "overview") {
    return lodVisibility;
  }

  return {
    choropleth: state.activeMapPanel === "choropleth" && state.toggles.choropleth,
    heatmap: state.activeMapPanel === "heatmap" && state.toggles.heatmap,
    hexbin: state.activeMapPanel === "hexbin" && state.toggles.hexbin,
    firePerimeters: state.activeMapPanel === "perimeters" && state.toggles.firePerimeters,
    satelliteContext: state.activeMapPanel === "heatmap" && state.toggles.satelliteContext,
    countyBoundaries: state.toggles.countyBoundaries,
  };
}

function formatTooltip(object?: any) {
  if (!object) return null;

  if (object.properties?.county_name) {
    return {
      html: `<div class="tooltip"><b>${object.properties.county_name} County</b><br/>Fire count: ${object.properties.fire_count}<br/>Acres: ${Number(object.properties.acres_burned).toLocaleString()}<br/>FIRMS detections: ${Number(object.properties.active_fire_points).toLocaleString()}<br/>Mean FRP: ${object.properties.mean_frp}</div>`,
    };
  }

  if (object.properties?.fire_name || object.properties?.fire_id) {
    return {
      html: `<div class="tooltip"><b>${object.properties.fire_name ?? "Unnamed fire"}</b><br/>Year: ${object.properties.year}<br/>Acres: ${Number(object.properties.acres ?? 0).toLocaleString()}<br/>Source: ${object.properties.source}</div>`,
    };
  }

  if (object.properties?.h3_index) {
    return {
      html: `<div class="tooltip"><b>${object.properties.h3_index}</b><br/>Month: ${object.properties.year}-${String(object.properties.month).padStart(2, "0")}<br/>Fire detections: ${Number(object.properties.fire_point_count).toLocaleString()}<br/>Sum FRP: ${Number(object.properties.sum_frp).toLocaleString()}<br/>Mean brightness: ${object.properties.mean_brightness}</div>`,
    };
  }

  if (object.points) {
    return {
      html: `<div class="tooltip"><b>Hex bin</b><br/>Fire detections: ${object.points.length}<br/>Summed FRP proxy: ${Math.round(object.elevationValue ?? 0).toLocaleString()}</div>`,
    };
  }

  return null;
}
