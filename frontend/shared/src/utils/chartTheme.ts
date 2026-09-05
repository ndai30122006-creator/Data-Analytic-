export const echartsDarkTheme = {
  backgroundColor: "transparent",
  textStyle: { color: "#94A3B8", fontFamily: "Inter, sans-serif" },
  color: ["#8B5CF6", "#06B6D4", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"],
  grid: { borderColor: "rgba(255,255,255,0.06)", top: 20, right: 12, bottom: 24, left: 40 },
  categoryAxis: { axisLine: { lineStyle: { color: "rgba(255,255,255,0.08)" } }, axisLabel: { color: "#94A3B8", fontSize: 11 }, splitLine: { show: false } },
  valueAxis: { axisLine: { show: false }, axisLabel: { color: "#94A3B8", fontSize: 11 }, splitLine: { lineStyle: { color: "rgba(255,255,255,0.06)" } } },
  tooltip: { backgroundColor: "rgba(10,10,26,0.95)", borderColor: "rgba(255,255,255,0.08)", textStyle: { color: "#EEF2FF", fontSize: 11 } },
  legend: { textStyle: { color: "#94A3B8", fontSize: 11 } },
};

export function getChartOption(type: string, overrides: Record<string, unknown> = {}) {
  return { ...echartsDarkTheme, ...overrides, _type: type };
}
