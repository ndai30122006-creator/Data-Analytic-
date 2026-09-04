import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/ingest" replace />} />
        <Route path="/ingest" element={<div>Ingest — web</div>} />
        <Route path="/pipeline" element={<div>Pipeline — web</div>} />
        <Route path="/brief" element={<div>Brief — web</div>} />
        <Route path="/dashboard" element={<div>Dashboard — web</div>} />
        <Route path="/lab" element={<div>Lab — web</div>} />
        <Route path="/settings" element={<div>Settings — web</div>} />
        <Route path="/lineage" element={<div>Lineage — web</div>} />
        <Route path="*" element={<div>Not Found</div>} />
      </Routes>
    </BrowserRouter>
  );
}
