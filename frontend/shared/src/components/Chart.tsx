import { useEffect, useRef } from "react";
import * as echarts from "echarts";
import { echartsDarkTheme } from "../utils/chartTheme";

export function Chart({ option, height = 180 }: { option: echarts.EChartsOption; height?: number }) {
  const ref = useRef<HTMLDivElement>(null);
  const chartRef = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!ref.current) return;
    if (!chartRef.current) {
      chartRef.current = echarts.init(ref.current, undefined, { renderer: "canvas" });
    }
    const merged = {
      ...option,
      backgroundColor: echartsDarkTheme.backgroundColor,
      textStyle: echartsDarkTheme.textStyle as any,
      color: echartsDarkTheme.color,
    } as echarts.EChartsOption;
    chartRef.current.setOption(merged as any, true);

    const ro = new ResizeObserver(() => chartRef.current?.resize());
    ro.observe(ref.current);
    return () => {
      ro.disconnect();
      chartRef.current?.dispose();
      chartRef.current = null;
    };
  }, [option]);

  return <div ref={ref} style={{ height, width: "100%" }} />;
}

export function mockOption(type: string): echarts.EChartsOption {
  const base = { grid: echartsDarkTheme.grid, tooltip: echartsDarkTheme.tooltip } as any;
  switch (type) {
    case "kpi":
      return { ...base, xAxis: { show: false }, yAxis: { show: false }, series: [{ type: "gauge", data: [{ value: 72 }], detail: { formatter: "{value}%" } }] };
    case "bar":
      return { ...base, xAxis: { type: "category", data: ["A", "B", "C"], ...echartsDarkTheme.categoryAxis as any }, yAxis: { type: "value", ...echartsDarkTheme.valueAxis as any }, series: [{ type: "bar", data: [12, 19, 7], itemStyle: { color: "#8B5CF6" } }] };
    case "hist":
      return { ...base, xAxis: { type: "category", data: ["0-10", "10-20", "20-30"], ...echartsDarkTheme.categoryAxis as any }, yAxis: { type: "value", ...echartsDarkTheme.valueAxis as any }, series: [{ type: "bar", data: [5, 12, 8] }] };
    case "box":
      return { ...base, xAxis: { type: "category", data: ["G1", "G2"], ...echartsDarkTheme.categoryAxis as any }, yAxis: { type: "value", ...echartsDarkTheme.valueAxis as any }, series: [{ type: "boxplot", data: [[[1, 2, 3, 4, 5], [2, 3, 4, 5, 6]]] }] };
    case "line":
      return { ...base, xAxis: { type: "category", data: ["T1", "T2", "T3", "T4"], ...echartsDarkTheme.categoryAxis as any }, yAxis: { type: "value", ...echartsDarkTheme.valueAxis as any }, series: [{ type: "line", data: [5, 9, 6, 12], smooth: true, lineStyle: { color: "#8B5CF6" } }] };
    case "scatter":
      return { ...base, xAxis: { type: "value", ...echartsDarkTheme.valueAxis as any }, yAxis: { type: "value", ...echartsDarkTheme.valueAxis as any }, series: [{ type: "scatter", data: [[10, 20], [20, 30], [30, 15]] }] };
    default:
      return base;
  }
}
