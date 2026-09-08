export const apexDarkTheme = {
  chart: { background: "transparent", foreColor: "#8B98A9", fontFamily: "Inter, sans-serif", toolbar: { show: false } },
  colors: ["#2DD4BF", "#22D3EE", "#A78BFA", "#FBBF24", "#F87171", "#34D399"],
  grid: { borderColor: "rgba(255,255,255,0.07)", padding: { top: 12, right: 12, bottom: 0, left: 12 } },
  tooltip: { theme: "dark" as const },
  stroke: { width: 2, curve: "smooth" as const },
};

export function getApexOptions(type: string, overrides: Record<string, unknown> = {}) {
  return { ...apexDarkTheme, ...overrides, _type: type };
}
