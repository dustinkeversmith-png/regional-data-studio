export function zoomBand(zoom: number) {
  if (zoom < 5) return "state";
  if (zoom < 7) return "county";
  if (zoom < 10) return "fire";
  return "local";
}

export function zoomBandLabel(zoom: number) {
  const band = zoomBand(zoom);

  if (band === "state") return "State outline and annual summary";
  if (band === "county") return "County choropleth";
  if (band === "fire") return "Fire perimeters and heatmap";
  return "FIRMS points, hex bins, and satellite context";
}
