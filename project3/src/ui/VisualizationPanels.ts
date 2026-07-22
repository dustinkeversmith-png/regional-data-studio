import type { AppState, MapPanel } from "../app/state";

const PANELS: Array<{ id: MapPanel; label: string; description: string }> = [
  {
    id: "overview",
    label: "Overview LOD",
    description: "Combined LOD map: zoom controls whether counties, perimeters, heatmap, and hex bins are visible.",
  },
  {
    id: "choropleth",
    label: "Choropleth",
    description: "County burden view using the selected county metric and normalized county summaries.",
  },
  {
    id: "heatmap",
    label: "FIRMS Heatmap",
    description: "Satellite active-fire intensity view. FRP is used as the default weight when available.",
  },
  {
    id: "hexbin",
    label: "Hexbin",
    description: "Spatial aggregation view for active-fire detections without relying on county boundaries.",
  },
  {
    id: "perimeters",
    label: "Perimeters",
    description: "Fire perimeter polygons filtered to the selected year.",
  },
];

export function renderVisualizationPanels(
  container: HTMLElement,
  state: AppState,
  onChange: (next: AppState) => void,
) {
  const active = PANELS.find((panel) => panel.id === state.activeMapPanel) ?? PANELS[0];

  container.innerHTML = `
    <strong>Map panel</strong>
    <div class="panel-tabs">
      ${PANELS.map(
        (panel) => `
          <button class="panel-tab ${panel.id === state.activeMapPanel ? "active" : ""}" data-panel="${panel.id}">
            ${panel.label}
          </button>
        `,
      ).join("")}
    </div>
    <p class="small-copy">${active.description}</p>
  `;

  container.querySelectorAll<HTMLButtonElement>("[data-panel]").forEach((button) => {
    button.addEventListener("click", () => {
      onChange({ ...state, activeMapPanel: button.dataset.panel as MapPanel });
    });
  });
}
