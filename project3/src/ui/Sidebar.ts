import { MODELING_CAVEAT, YEARS } from "../app/config";
import type { AppState } from "../app/state";
import type { AmocMetric, ChoroplethMetric, FireTimelineMetric } from "../data/schemas";
import { renderLayerToggles } from "./LayerToggles";
import { renderTimeSlider } from "./TimeSlider";

const choroplethMetrics: ChoroplethMetric[] = [
  "fire_count",
  "acres_burned",
  "active_fire_points",
  "mean_frp",
  "fire_density_per_sq_km",
];

const fireMetrics: FireTimelineMetric[] = [
  "monthly_fire_points",
  "monthly_sum_frp",
  "monthly_acres_burned_estimate",
  "rolling_12mo_fire_points",
];

const amocMetrics: AmocMetric[] = ["amoc_transport_sv", "amoc_anomaly_sv", "rolling_12mo_amoc"];

export function renderSidebar(container: HTMLElement, state: AppState, onChange: (next: AppState) => void) {
  container.innerHTML = `
    <h1>Oregon Fire + AMOC Visualization Lab</h1>
    <p>${MODELING_CAVEAT}</p>
    <div id="time-controls"></div>
    <div id="layer-controls"></div>
    <div class="control-group">
      <h2>Metrics</h2>
      ${metricSelect("choroplethMetric", "Choropleth", choroplethMetrics, state.choroplethMetric)}
      ${metricSelect("fireTimelineMetric", "Fire timeline", fireMetrics, state.fireTimelineMetric)}
      ${metricSelect("amocMetric", "AMOC timeline", amocMetrics, state.amocMetric)}
      <label class="toggle-row">
        <span>June-Oct fire season only</span>
        <input id="fire-season" type="checkbox" ${state.fireSeasonOnly ? "checked" : ""} />
      </label>
    </div>
  `;

  renderTimeSlider(container.querySelector<HTMLElement>("#time-controls")!, state, onChange);
  renderLayerToggles(container.querySelector<HTMLElement>("#layer-controls")!, state, onChange);

  container.querySelectorAll<HTMLSelectElement>("[data-metric]").forEach((select) => {
    select.addEventListener("change", () => {
      const key = select.dataset.metric as "choroplethMetric" | "fireTimelineMetric" | "amocMetric";
      onChange({ ...state, [key]: select.value });
    });
  });

  container.querySelector<HTMLInputElement>("#fire-season")!.addEventListener("change", (event) => {
    onChange({ ...state, fireSeasonOnly: (event.currentTarget as HTMLInputElement).checked });
  });
}

function metricSelect(name: string, label: string, values: string[], selected: string) {
  return `
    <label class="metric-row">
      <span>${label}</span>
      <select data-metric="${name}">
        ${values.map((value) => `<option value="${value}" ${value === selected ? "selected" : ""}>${value}</option>`).join("")}
      </select>
    </label>
  `;
}

export function yearLabel(year: number) {
  return YEARS.includes(year) ? String(year) : "2016-2025";
}
