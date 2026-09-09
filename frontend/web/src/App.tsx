import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ErrorBoundary } from "@app/shared/src/components/ErrorBoundary";
import { RequireAuth } from "@app/shared/src/features/auth/RequireAuth";
import DesktopShell from "./layout/DesktopShell";
import Overview from "./pages/Overview";
import Login from "./pages/Login";
import Settings from "./pages/Settings";
import Ingest from "./pages/Ingest";
import Pipeline from "./pages/Pipeline";
import Brief from "./pages/Brief";
import Dashboard from "./pages/Dashboard";
import Lab from "./pages/Lab";
import Lineage from "./pages/Lineage";

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route element={<RequireAuth><DesktopShell /></RequireAuth>}>
            <Route path="/" element={<Overview />} />
            <Route path="/ingest" element={<Ingest />} />
            <Route path="/pipeline" element={<Pipeline />} />
            <Route path="/brief" element={<Brief />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/lab" element={<Lab />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/lineage" element={<Lineage />} />
          </Route>
          <Route path="*" element={<div style={{ maxWidth: 480, margin: "12vh auto", textAlign: "center", fontFamily: "var(--font-mono)" }}><div style={{ fontSize: 44, fontWeight: 800, color: "var(--accent)" }}>404</div><div style={{ color: "var(--text-muted)", fontSize: 13 }}>$ command not found — <a href="/">về Overview</a></div></div>} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
