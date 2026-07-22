import * as echarts from "echarts";
import type { AppState } from "../app/state";
import type { FireAmocMonthlyRow } from "../data/schemas";
import { chartSeries } from "../data/transforms";

export class AmocFireTimeline {
  private chart: echarts.ECharts;

  constructor(element: HTMLElement) {
    this.chart = echarts.init(element);
    window.addEventListener("resize", () => this.chart.resize());
  }

  render(rows: FireAmocMonthlyRow[], state: AppState) {
    const series = chartSeries(rows, state.fireTimelineMetric, state.amocMetric);

    this.chart.setOption({
      color: ["#f97316", "#38bdf8"],
      tooltip: { trigger: "axis" },
      grid: { top: 20, right: 42, bottom: 28, left: 48 },
      xAxis: {
        type: "category",
        data: series.dates,
        axisLabel: { color: "#b7d8cb", hideOverlap: true },
      },
      yAxis: [
        {
          type: "value",
          name: "Fire proxy",
          nameTextStyle: { color: "#f97316" },
          axisLabel: { color: "#b7d8cb" },
          splitLine: { lineStyle: { color: "rgba(183,216,203,0.14)" } },
        },
        {
          type: "value",
          name: "AMOC",
          nameTextStyle: { color: "#38bdf8" },
          axisLabel: { color: "#b7d8cb" },
          splitLine: { show: false },
        },
      ],
      dataZoom: [{ type: "inside" }, { type: "slider", height: 14, bottom: 4 }],
      series: [
        {
          name: state.fireTimelineMetric,
          type: "line",
          smooth: true,
          data: series.fire,
          yAxisIndex: 0,
          showSymbol: false,
        },
        {
          name: state.amocMetric,
          type: "line",
          smooth: true,
          data: series.amoc,
          yAxisIndex: 1,
          showSymbol: false,
        },
      ],
    });
  }
}
