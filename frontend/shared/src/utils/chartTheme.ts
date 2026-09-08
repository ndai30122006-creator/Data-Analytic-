export const apexDarkTheme = {
  chart: { background: "transparent", foreColor: "#5F8A80", fontFamily: "JetBrains Mono, monospace", toolbar: { show: false } },
  colors: ["#2DD4BF", "#5EEAD4", "#14B8A6", "#FACC15", "#F87171", "#38BDF8"],
  grid: { borderColor: "rgba(45,212,191,0.12)", padding: { top: 12, right: 12, bottom: 0, left: 12 } },
  tooltip: { theme: "dark" as const },
  stroke: { width: 2, curve: "smooth" as const },
};

export function getApexOptions(type: string, overrides: Record<string, unknown> = {}) {
  return { ...apexDarkTheme, ...overrides, _type: type };
}
