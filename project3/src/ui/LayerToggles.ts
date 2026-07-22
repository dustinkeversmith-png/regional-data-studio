import type { AppState, LayerToggleState } from "../app/state";

const LABELS: Record<keyof LayerToggleState, string> = {
  choropleth: "County choropleth",
  heatmap: "FIRMS heatmap",
  hexbin: "Hexagonal binning",
  firePerimeters: "Fire perimeters",
  satelliteContext: "Satellite context",
  countyBoundaries: "County boundaries",
};

export function renderLayerToggles(
  container: HTMLElement,
  state: AppState,
  onChange: (next: AppState) => void,
) {
  container.innerHTML = `
    <div class="control-group">
      <h2>Map layers</h2>
      ${Object.entries(LABELS)
        .map(
          ([key, label]) => `
          <label class="toggle-row">
            <span>${label}</span>
            <input type="checkbox" data-layer="${key}" ${state.toggles[key as keyof LayerToggleState] ? "checked" : ""} />
          </label>
        `,
        )
        .join("")}
    </div>
  `;

  container.querySelectorAll<HTMLInputElement>("[data-layer]").forEach((input) => {
    input.addEventListener("change", () => {
      const key = input.dataset.layer as keyof LayerToggleState;
      onChange({
        ...state,
        toggles: {
          ...state.toggles,
          [key]: input.checked,
        },
      });
    });
  });
}
