import { api } from './api'

export type Role = 'FARMER' | 'REVIEWER' | 'ADMIN' | 'DEMO_FARMER' | 'DEMO_REVIEWER' | 'DEMO_ADMIN'
export type NextStep = 'home' | 'totp' | 'setup_totp'

export interface AuthState {
  authenticated: boolean
  next?: NextStep
  role?: Role
  tenant?: 'real' | 'demo'
  display_name?: string
  locale?: 'bn' | 'en'
  step_up?: boolean
  csrf_token?: string
}

export interface SessionReply {
  next: NextStep
  csrf_token: string
  user?: {
    id: string
    role: Role
    display_name: string
    locale: 'bn' | 'en'
    tenant: 'real' | 'demo'
  }
  recovery_codes?: string[]
}

export const baseRole = (role: Role): 'farmer' | 'reviewer' | 'admin' =>
  role.replace('DEMO_', '').toLowerCase() as 'farmer' | 'reviewer' | 'admin'

export const isDemo = (role: Role | undefined): boolean => role?.startsWith('DEMO_') ?? false

/** Where each role lands after signing in. */
export const homePath = (role: Role): string =>
  ({ farmer: '/home', reviewer: '/review', admin: '/admin' })[baseRole(role)]

export const authApi = {
  state: () => api.get<AuthState>('/api/v1/auth/state', { quiet401: true }),
  login: (body: {
    identifier: string
    password: string
    keep_signed_in: boolean
    captcha?: string
  }) => api.post<SessionReply>('/api/v1/auth/login', body, { quiet401: true }),
  loginTotp: (body: { code: string; recovery: boolean }) =>
    api.post<SessionReply>('/api/v1/auth/login/totp', body),
  stepUp: (code: string) => api.post<SessionReply>('/api/v1/auth/step-up', { code }),
  logout: () => api.post<void>('/api/v1/auth/logout'),
  logoutAll: () => api.post<void>('/api/v1/auth/logout-all'),
  registerFarmer: (body: {
    phone: string
    password: string
    display_name: string
    locale: 'bn' | 'en'
    accept_service: true
    training_use: boolean
    push_alerts: boolean
    captcha: string
    website: string
  }) => api.post<{ status: string }>('/api/v1/auth/register/farmer', body, { quiet401: true }),
  registerStaff: (body: {
    token: string
    password: string
    display_name: string
    locale: 'bn' | 'en'
  }) => api.post<{ status: string }>('/api/v1/auth/register/staff', body, { quiet401: true }),
  otpSend: (body: { phone: string; purpose: 'register' | 'reset'; captcha?: string }) =>
    api.post<{ status: string }>('/api/v1/auth/otp/send', body, { quiet401: true }),
  otpVerify: (body: { phone: string; code: string; keep_signed_in: boolean }) =>
    api.post<SessionReply>('/api/v1/auth/otp/verify', body, { quiet401: true }),
  forgot: (body: { identifier: string; captcha?: string }) =>
    api.post<{ status: string }>('/api/v1/auth/password/forgot', body, { quiet401: true }),
  reset: (body: { new_password: string; token?: string; phone?: string; code?: string }) =>
    api.post<void>('/api/v1/auth/password/reset', body, { quiet401: true }),
  totpSetup: () => api.post<{ secret: string; otpauth_uri: string }>('/api/v1/auth/totp/setup'),
  totpConfirm: (code: string) => api.post<SessionReply>('/api/v1/auth/totp/confirm', { code }),
  demoSession: (body: { role: 'DEMO_FARMER' | 'DEMO_REVIEWER' | 'DEMO_ADMIN'; captcha: string }) =>
    api.post<SessionReply>('/api/v1/demo/session', body, { quiet401: true }),
  sessions: () =>
    api.get<{
      sessions: {
        id: string
        created_at: string
        last_seen_at: string
        device: string
        current: boolean
      }[]
    }>('/api/v1/me/sessions'),
  revokeSession: (id: string) => api.delete<void>(`/api/v1/me/sessions/${encodeURIComponent(id)}`),
}
