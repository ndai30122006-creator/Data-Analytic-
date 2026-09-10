import { useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { TopBar } from "../components/layout/TopBar";
import { NavRail } from "../components/layout/NavRail";
import CommandPalette from "../components/CommandPalette";
import StatusBar from "../components/StatusBar";

export default function DesktopShell() {
  const loc = useLocation();
  const navgo = useNavigate();
  const [collapsed, setCollapsed] = useState(() => localStorage.getItem("nav_collapsed") === "1");

  const toggle = () => {
    setCollapsed((c) => {
      localStorage.setItem("nav_collapsed", c ? "0" : "1");
      return !c;
    });
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh", background: "transparent", position: "relative", zIndex: 1 }}>
      <div className="orb orb-a" />
      <div className="orb orb-b" />
      <TopBar onSearch={() => window.dispatchEvent(new Event("open-palette"))} onLogout={() => navgo("/login")} />
      <div style={{ display: "flex", flex: 1, minHeight: 0 }}>
        <NavRail collapsed={collapsed} onToggle={toggle} />
        <main key={loc.pathname} className="page-enter" style={{ flex: 1, minWidth: 0, padding: 28, maxWidth: 1280, margin: "0 auto", width: "100%" }}>
          <Outlet />
        </main>
      </div>
      <StatusBar />
      <CommandPalette />
    </div>
  );
}
