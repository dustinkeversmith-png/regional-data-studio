import type { Map as MapLibreMap } from "maplibre-gl";
import { AmocFireTimeline } from "../charts/AmocFireTimeline";
import { LagAnalysisPanel } from "../charts/LagAnalysisPanel";
import { renderCorrelationPanel } from "../charts/CorrelationPanel";
import { renderYearSummaryPanel } from "../charts/YearSummaryPanel";
import { loadProcessedData } from "../data/loaders";
import type { ProcessedData } from "../data/schemas";
import { createMap } from "../map/createMap";
import { LayerController } from "../map/layerController";
import { zoomBandLabel } from "../map/baseLayers";
import { renderLegend } from "../ui/Legend";
import { renderSidebar } from "../ui/Sidebar";
import { renderVisualizationPanels } from "../ui/VisualizationPanels";
import { defaultState, type AppState } from "./state";

export class App {
  private state: AppState = defaultState;
  private data: ProcessedData | null = null;
  private map: MapLibreMap | null = null;
  private layerController: LayerController | null = null;
  private timeline: AmocFireTimeline | null = null;
  private lagPanel: LagAnalysisPanel | null = null;

  constructor(private root: HTMLElement) {}

  async start() {
    this.root.innerHTML = `
      <main class="app-shell">
        <div id="map" class="map-host"></div>
        <aside id="sidebar" class="sidebar panel"></aside>
        <section id="lod-card" class="layer-card panel"></section>
        <section id="map-panels" class="map-panels panel"></section>
        <section id="legend" class="legend panel"></section>
        <section class="chart-dock">
          <div class="chart-panel panel">
            <h2>AMOC vs Oregon fire activity proxies</h2>
            <div id="timeline" class="chart"></div>
          </div>
          <div id="correlation" class="chart-panel panel"></div>
          <div class="chart-panel panel">
            <h2>Lag scan (-24 to +24 months)</h2>
            <div id="lag-chart" class="chart"></div>
          </div>
        </section>
      </main>
    `;

    this.data = await loadProcessedData();
    this.map = createMap(this.element("#map"));
    this.layerController = new LayerController(this.map);
    this.timeline = new AmocFireTimeline(this.element("#timeline"));
    this.lagPanel = new LagAnalysisPanel(this.element("#lag-chart"));

    this.map.on("load", () => this.render());
    this.map.on("zoomend", () => this.render());
    this.render();
  }

  private render() {
    if (!this.data) {
      return;
    }

    renderSidebar(this.element("#sidebar"), this.state, (next) => {
      this.state = next;
      this.render();
    });
    renderVisualizationPanels(this.element("#map-panels"), this.state, (next) => {
      this.state = next;
      this.render();
    });
    renderLegend(this.element("#legend"), this.state.choroplethMetric);
    renderCorrelationPanel(this.element("#correlation"), this.data.correlation);
    renderYearSummaryPanel(this.element("#lod-card"), this.data.fireAmocRows, this.state.selectedYear);

    if (this.map) {
      this.element("#lod-card").insertAdjacentHTML(
        "beforeend",
        `<p class="small-copy">LOD: ${zoomBandLabel(this.map.getZoom())}</p>`,
      );
    }

    this.timeline?.render(this.data.fireAmocRows, this.state);
    this.lagPanel?.render(this.data.correlation);
    this.layerController?.update(this.data, this.state);
  }

  private element<T extends HTMLElement = HTMLElement>(selector: string): T {
    const element = this.root.querySelector<T>(selector);
    if (!element) {
      throw new Error(`Missing element ${selector}`);
    }

    return element;
  }
}
