export function renderLegend(container: HTMLElement, metric: string) {
  container.innerHTML = `
    <strong>${metric.replace(/_/g, " ")}</strong>
    <div class="legend-gradient"></div>
    <div class="legend-labels">
      <span>Lower proxy</span>
      <span>Higher proxy</span>
    </div>
  `;
}
