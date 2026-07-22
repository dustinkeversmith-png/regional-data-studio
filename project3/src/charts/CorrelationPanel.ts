import type { CorrelationSummary } from "../data/schemas";

export function renderCorrelationPanel(element: HTMLElement, correlation: CorrelationSummary) {
  element.innerHTML = `
    <h2>10-year correlation summary</h2>
    <div class="stat-grid">
      <div class="stat"><b>${correlation.pearson.toFixed(2)}</b><span>Pearson</span></div>
      <div class="stat"><b>${correlation.spearman.toFixed(2)}</b><span>Spearman</span></div>
      <div class="stat"><b>${correlation.fire_season_pearson.toFixed(2)}</b><span>Fire season Pearson</span></div>
      <div class="stat"><b>${correlation.best_lag_pearson.toFixed(2)}</b><span>Best lag Pearson</span></div>
    </div>
    <p class="small-copy">${correlation.interpretation}</p>
  `;
}
