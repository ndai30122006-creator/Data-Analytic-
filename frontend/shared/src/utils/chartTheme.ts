export const apexDarkTheme = {
  chart: { background: "transparent", foreColor: "#6b7280", fontFamily: "JetBrains Mono, monospace", toolbar: { show: false } },
  colors: ["#00ff88", "#ff00ff", "#00d4ff", "#F9F002", "#ff3366", "#00e67a"],
  grid: { borderColor: "#2a2a3a", padding: { top: 12, right: 12, bottom: 0, left: 12 } },
  tooltip: { theme: "dark" as const },
  stroke: { width: 2, curve: "smooth" as const },
};

export function getApexOptions(type: string, overrides: Record<string, unknown> = {}) {
  return { ...apexDarkTheme, ...overrides, _type: type };
}
