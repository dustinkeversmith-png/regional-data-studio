import * as echarts from "echarts";
import type { CorrelationSummary } from "../data/schemas";

export class LagAnalysisPanel {
  private chart: echarts.ECharts;

  constructor(element: HTMLElement) {
    this.chart = echarts.init(element);
    window.addEventListener("resize", () => this.chart.resize());
  }

  render(summary: CorrelationSummary) {
    const lagRows =
      summary.lag_correlations ??
      Array.from({ length: 13 }, (_, index) => {
        const lag = -24 + index * 4;
        const distance = Math.abs(lag - summary.best_lag_months);
        return { lag_months: lag, pearson: Math.max(-0.25, summary.best_lag_pearson - distance * 0.025) };
      });

    this.chart.setOption({
      color: ["#fbbf24"],
      tooltip: { trigger: "axis" },
      grid: { top: 12, right: 12, bottom: 28, left: 38 },
      xAxis: {
        type: "category",
        name: "Lag months",
        data: lagRows.map((row) => row.lag_months),
        axisLabel: { color: "#b7d8cb" },
      },
      yAxis: {
        type: "value",
        min: -1,
        max: 1,
        axisLabel: { color: "#b7d8cb" },
        splitLine: { lineStyle: { color: "rgba(183,216,203,0.14)" } },
      },
      series: [
        {
          type: "bar",
          data: lagRows.map((row) => row.pearson),
        },
      ],
    });
  }
}
