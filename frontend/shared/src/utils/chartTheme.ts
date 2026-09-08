export const apexDarkTheme = {
  chart: { background: "transparent", foreColor: "#6B8F71", fontFamily: "JetBrains Mono, monospace", toolbar: { show: false } },
  colors: ["#4ADE80", "#86EFAC", "#22C55E", "#FACC15", "#F87171", "#38BDF8"],
  grid: { borderColor: "rgba(74,222,128,0.12)", padding: { top: 12, right: 12, bottom: 0, left: 12 } },
  tooltip: { theme: "dark" as const },
  stroke: { width: 2, curve: "smooth" as const },
};

export function getApexOptions(type: string, overrides: Record<string, unknown> = {}) {
  return { ...apexDarkTheme, ...overrides, _type: type };
}
