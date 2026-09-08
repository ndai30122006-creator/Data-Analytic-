export const apexDarkTheme = {
  chart: { background: "transparent", foreColor: "#8A8AB3", fontFamily: "JetBrains Mono, monospace", toolbar: { show: false } },
  colors: ["#FF2A6D", "#05D9E8", "#F9F002", "#B967FF", "#FF3131", "#00F0FF"],
  grid: { borderColor: "rgba(255,42,109,0.16)", padding: { top: 12, right: 12, bottom: 0, left: 12 } },
  tooltip: { theme: "dark" as const },
  stroke: { width: 2, curve: "smooth" as const },
};

export function getApexOptions(type: string, overrides: Record<string, unknown> = {}) {
  return { ...apexDarkTheme, ...overrides, _type: type };
}
