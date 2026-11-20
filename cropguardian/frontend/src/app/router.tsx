import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { RedirectIfSignedIn, RequireSession } from './guards'
import {
  AcceptInvitePage,
  ForgotPage,
  LoginPage,
  RegisterPage,
  ResetPage,
  SetupTotpPage,
  TotpPage,
  VerifyOtpPage,
} from './pages/auth'
import { ForbiddenPage, NotFoundPage } from './pages/errors'
import { DemoPickerPage, EntryPage, SessionsPage } from './pages/home'
import { Shell } from './ui'

// The admin area is a separate chunk: a farmer or reviewer never even requests this file.
const AdminHome = lazy(() => import('./pages/AdminHome'))
// Farmer app, reviewer console and Trust Centre are route chunks too (initial JS budget, spec 15.8).
const farmer = () => import('./pages/farmer')
const FarmerLayout = lazy(() => farmer().then((m) => ({ default: m.FarmerLayout })))
const FarmerHomePage = lazy(() => farmer().then((m) => ({ default: m.FarmerHomePage })))
const ScanPage = lazy(() => farmer().then((m) => ({ default: m.ScanPage })))
const ResultPage = lazy(() => farmer().then((m) => ({ default: m.ResultPage })))
const HistoryPage = lazy(() => farmer().then((m) => ({ default: m.HistoryPage })))
const AlertsPage = lazy(() => farmer().then((m) => ({ default: m.AlertsPage })))
const MorePage = lazy(() => farmer().then((m) => ({ default: m.MorePage })))
const ReviewerAlertsPage = lazy(() =>
  import('./pages/review').then((m) => ({ default: m.ReviewerAlertsPage })),
)
const TrustPage = lazy(() => import('./pages/trust').then((m) => ({ default: m.TrustPage })))

const wait = <p role="status">…</p>

export function AppRoutes() {
  return (
    <Suspense fallback={wait}>
      <Routes>
        <Route element={<Shell />}>
          <Route index element={<EntryPage />} />
          <Route element={<RedirectIfSignedIn />}>
            <Route path="login" element={<LoginPage />} />
            <Route path="staff" element={<LoginPage staff />} />
            <Route path="register" element={<RegisterPage />} />
          </Route>
          <Route path="verify" element={<VerifyOtpPage />} />
          <Route path="forgot-password" element={<ForgotPage />} />
          <Route path="reset-password" element={<ResetPage />} />
          <Route path="accept-invite" element={<AcceptInvitePage />} />
          <Route path="demo" element={<DemoPickerPage />} />
          <Route path="403" element={<ForbiddenPage />} />
          <Route path="trust" element={<TrustPage />} />

          <Route element={<RequireSession allowPending />}>
            <Route path="login/totp" element={<TotpPage />} />
            <Route path="setup-2fa" element={<SetupTotpPage />} />
          </Route>
          <Route element={<RequireSession />}>
            <Route path="account/sessions" element={<SessionsPage />} />
          </Route>
          <Route element={<RequireSession area="farmer" />}>
            <Route path="home" element={<Navigate to="/app" replace />} />
            <Route path="app" element={<FarmerLayout />}>
              <Route index element={<FarmerHomePage />} />
              <Route path="scan" element={<ScanPage />} />
              <Route path="scan/:id" element={<ResultPage />} />
              <Route path="history" element={<HistoryPage />} />
              <Route path="alerts" element={<AlertsPage />} />
              <Route path="more" element={<MorePage />} />
            </Route>
          </Route>
          <Route element={<RequireSession area="reviewer" />}>
            <Route path="review" element={<ReviewerAlertsPage />} />
          </Route>
          <Route element={<RequireSession area="admin" />}>
            <Route
              path="admin"
              element={
                <Suspense fallback={<p role="status">…</p>}>
                  <AdminHome />
                </Suspense>
              }
            />
          </Route>
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </Suspense>
  )
}
