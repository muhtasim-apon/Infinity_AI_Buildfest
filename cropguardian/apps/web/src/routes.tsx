// Route table. Pages are lazy-loaded so the first paint on slow 3G is only the scan flow.
// Stub — page components are declared in features/*; not yet implemented.
import { lazy, Suspense } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

const Home = lazy(() => import("./features/scan/HomePage"));
const Scan = lazy(() => import("./features/scan/ScanPage"));
const Result = lazy(() => import("./features/diagnosis/ResultPage"));
const History = lazy(() => import("./features/history/HistoryPage"));
const Alerts = lazy(() => import("./features/alerts/AlertsPage"));
const Review = lazy(() => import("./features/review/ReviewPage"));
const Demo = lazy(() => import("./features/showcase/DemoEntry"));
const Admin = lazy(() => import("./features/admin/AdminPage"));
const Audit = lazy(() => import("./features/audit/AuditPage"));
const Showcase = lazy(() => import("./features/showcase/ShowcasePage"));

export function AppRouter() {
  return (
    <BrowserRouter>
      <Suspense fallback={<p>লোড হচ্ছে…</p>}>
        <Routes>
          <Route path="/" element={<Navigate to="/app" replace />} />
          <Route path="/app" element={<Home />} />
          <Route path="/app/scan" element={<Scan />} />
          <Route path="/app/result/:id" element={<Result />} />
          <Route path="/app/history" element={<History />} />
          <Route path="/app/alerts" element={<Alerts />} />
          <Route path="/app/review" element={<Review />} />
          <Route path="/demo-user" element={<Demo role="user" />} />
          <Route path="/demo-admin" element={<Demo role="admin" />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/audit" element={<Audit />} />
          {(["data", "security", "architecture", "presentation", "pitchdeck"] as const).map((p) => (
            <Route key={p} path={`/${p}`} element={<Showcase page={p} />} />
          ))}
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
