import type { FireAmocMonthlyRow } from "../data/schemas";
import { formatNumber } from "../ui/Tooltip";

export function renderYearSummaryPanel(element: HTMLElement, rows: FireAmocMonthlyRow[], selectedYear: number) {
  const yearRows = rows.filter((row) => row.year === selectedYear);
  const firePoints = yearRows.reduce((sum, row) => sum + row.monthly_fire_points, 0);
  const acres = yearRows.reduce((sum, row) => sum + row.monthly_acres_burned_estimate, 0);
  const meanAmoc =
    yearRows.reduce((sum, row) => sum + row.amoc_anomaly_sv, 0) / Math.max(1, yearRows.length);

  element.innerHTML = `
    <h2>${selectedYear} fire proxy summary</h2>
    <div class="stat-grid">
      <div class="stat"><b>${formatNumber(firePoints)}</b><span>FIRMS detections</span></div>
      <div class="stat"><b>${formatNumber(Math.round(acres))}</b><span>Acres proxy</span></div>
      <div class="stat"><b>${meanAmoc.toFixed(2)}</b><span>Mean AMOC anomaly Sv</span></div>
      <div class="stat"><b>Jun-Oct</b><span>Default season filter</span></div>
    </div>
  `;
}
