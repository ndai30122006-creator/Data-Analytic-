import React from "react";
import ReactApexChart from "react-apexcharts";
import type { ApexOptions } from "apexcharts";
import { apexDarkTheme } from "../utils/chartTheme";

export function Chart({ type, height = 180, options }: { type: string; height?: number; options?: ApexOptions }) {
  const base = getMockApexOptions(type);
  const merged = { ...base, ...(options || {}) } as ApexOptions;
  const series = (merged.series as any) || base.series;
  // ApexCharts expects options without series
  const { series: _, ...opts } = merged as any;
  return <ReactApexChart options={opts as ApexOptions} series={series as any} type={apexType(type)} height={height} />;
}

function apexType(t: string): "bar" | "area" | "line" | "scatter" | "radialBar" {
  if (t === "kpi") return "radialBar";
  if (t === "hist" || t === "bar") return "bar";
  if (t === "box") return "bar";
  if (t === "line") return "line";
  if (t === "scatter") return "scatter";
  return "bar";
}

function getMockApexOptions(type: string): ApexOptions {
  const common: ApexOptions = {
    chart: { ...apexDarkTheme.chart, toolbar: { show: false } },
    colors: apexDarkTheme.colors,
    grid: { borderColor: apexDarkTheme.grid.borderColor, padding: apexDarkTheme.grid.padding },
    tooltip: { theme: apexDarkTheme.tooltip.theme },
    xaxis: { labels: { style: { colors: "#94A3B8", fontSize: "11px" } }, axisBorder: { show: false }, axisTicks: { show: false } } as any,
    yaxis: { labels: { style: { colors: "#94A3B8", fontSize: "11px" } } } as any,
  };
  switch (type) {
    case "kpi":
      return {
        ...common,
        chart: { ...common.chart, type: "radialBar" },
        plotOptions: { radialBar: { dataLabels: { value: { color: "#EEF2FF", fontSize: "16px" } }, track: { background: "rgba(255,255,255,0.06)" } } } as any,
        series: [72],
        labels: ["KPI"],
      } as ApexOptions;
    case "bar":
      return { ...common, chart: { type: "bar" }, plotOptions: { bar: { borderRadius: 6, columnWidth: "45%" } } as any, xaxis: { categories: ["A", "B", "C"] } as any, series: [{ name: "count", data: [12, 19, 7] }] } as ApexOptions;
    case "hist":
      return { ...common, chart: { type: "bar" }, xaxis: { categories: ["0-10", "10-20", "20-30"] } as any, series: [{ name: "freq", data: [5, 12, 8] }] } as ApexOptions;
    case "box":
      return { ...common, chart: { type: "boxPlot" as any }, xaxis: { categories: ["G1", "G2"] } as any, series: [{ type: "boxPlot", data: [{ x: "G1", y: [1, 2, 3, 4, 5] }, { x: "G2", y: [2, 3, 4, 5, 6] }] } as any] } as ApexOptions;
    case "line":
      return { ...common, chart: { type: "line" }, stroke: { curve: "smooth", width: 2, colors: ["#8B5CF6"] } as any, xaxis: { categories: ["T1", "T2", "T3", "T4"] } as any, series: [{ name: "trend", data: [5, 9, 6, 12] }] } as ApexOptions;
    case "scatter":
      return { ...common, chart: { type: "scatter", zoom: { enabled: false } as any }, series: [{ name: "points", data: [[10, 20], [20, 30], [30, 15]] }] } as ApexOptions;
    default:
      return common;
  }
}

export function mockOption(type: string) {
  return getMockApexOptions(type);
}
