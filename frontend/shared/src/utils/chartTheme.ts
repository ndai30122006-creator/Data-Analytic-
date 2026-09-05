export const apexDarkTheme = {
  chart: { background: "transparent", foreColor: "#94A3B8", fontFamily: "Inter, sans-serif", toolbar: { show: false } },
  colors: ["#8B5CF6", "#06B6D4", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"],
  grid: { borderColor: "rgba(255,255,255,0.06)", padding: { top: 12, right: 12, bottom: 0, left: 12 } },
  tooltip: { theme: "dark" as const },
  stroke: { width: 2, curve: "smooth" as const },
};

export function getApexOptions(type: string, overrides: Record<string, unknown> = {}) {
  return { ...apexDarkTheme, ...overrides, _type: type };
}
