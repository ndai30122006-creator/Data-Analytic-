import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import DesktopShell from "./layout/DesktopShell";
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
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<DesktopShell />}>
          <Route path="/" element={<Navigate to="/ingest" replace />} />
          <Route path="/ingest" element={<Ingest />} />
          <Route path="/pipeline" element={<Pipeline />} />
          <Route path="/brief" element={<Brief />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/lab" element={<Lab />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/lineage" element={<Lineage />} />
        </Route>
        <Route path="*" element={<div>Not Found</div>} />
      </Routes>
    </BrowserRouter>
  );
}
