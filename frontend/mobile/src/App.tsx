import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import MobileShell from "./layout/MobileShell";
import Login from "./pages/Login";
import Brief from "./pages/Brief";
import Dashboard from "./pages/Dashboard";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<MobileShell />}>
          <Route path="/" element={<Navigate to="/brief" replace />} />
          <Route path="/brief" element={<Brief />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/lineage" element={<div>Lineage — mobile</div>} />
          <Route path="/lab" element={<div>Lab — mobile</div>} />
          <Route path="/settings" element={<div>Settings — mobile</div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
