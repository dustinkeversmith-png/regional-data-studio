import maplibregl from "maplibre-gl";
import { MAP_STYLE, OREGON_VIEW } from "../app/config";

export function createMap(container: HTMLElement) {
  const map = new maplibregl.Map({
    container,
    style: MAP_STYLE,
    center: [OREGON_VIEW.longitude, OREGON_VIEW.latitude],
    zoom: OREGON_VIEW.zoom,
    pitch: OREGON_VIEW.pitch,
    bearing: OREGON_VIEW.bearing,
    attributionControl: { compact: true },
  });

  map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "bottom-right");

  return map;
}
