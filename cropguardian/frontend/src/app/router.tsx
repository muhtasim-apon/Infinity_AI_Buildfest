import { lazy, Suspense } from 'react'
import { Route, Routes } from 'react-router-dom'
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
import { DemoPickerPage, EntryPage, FarmerHome, ReviewerHome, SessionsPage } from './pages/home'
import { Shell } from './ui'

// The admin area is a separate chunk: a farmer or reviewer never even requests this file.
const AdminHome = lazy(() => import('./pages/AdminHome'))

export function AppRoutes() {
  return (
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

        <Route element={<RequireSession allowPending />}>
          <Route path="login/totp" element={<TotpPage />} />
          <Route path="setup-2fa" element={<SetupTotpPage />} />
        </Route>
        <Route element={<RequireSession />}>
          <Route path="account/sessions" element={<SessionsPage />} />
        </Route>
        <Route element={<RequireSession area="farmer" />}>
          <Route path="home" element={<FarmerHome />} />
        </Route>
        <Route element={<RequireSession area="reviewer" />}>
          <Route path="review" element={<ReviewerHome />} />
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
  )
}
