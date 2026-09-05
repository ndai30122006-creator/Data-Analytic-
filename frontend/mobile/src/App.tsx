import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ErrorBoundary } from "@app/shared/src/components/ErrorBoundary";
import MobileShell from "./layout/MobileShell";
import Login from "./pages/Login";
import Brief from "./pages/Brief";
import Dashboard from "./pages/Dashboard";
import Lineage from "./pages/Lineage";
import Lab from "./pages/Lab";
import Settings from "./pages/Settings";
import Ingest from "./pages/Ingest";
import Pipeline from "./pages/Pipeline";

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route element={<MobileShell />}>
            <Route path="/" element={<Navigate to="/brief" replace />} />
            <Route path="/brief" element={<Brief />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/lineage" element={<Lineage />} />
            <Route path="/lab" element={<Lab />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/ingest" element={<Ingest />} />
            <Route path="/pipeline" element={<Pipeline />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
