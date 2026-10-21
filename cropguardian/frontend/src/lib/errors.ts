import { ApiError } from './api'

export interface MessageRef {
  key: string
  values?: Record<string, string | number>
}

/** Maps an API failure to a Bangla-first message key. Uniform on purpose for credential errors. */
export function messageFor(error: unknown): MessageRef {
  if (!(error instanceof ApiError)) return { key: 'errors.generic' }
  if (error.isUnavailable) return { key: 'errors.waking' }
  switch (error.code) {
    case 'invalid_credentials':
      return { key: 'errors.invalidCredentials' }
    case 'account_locked':
      return { key: 'errors.locked' }
    case 'rate_limited':
      return error.retryAfter === undefined
        ? { key: 'errors.rateLimited' }
        : { key: 'errors.retryAfter', values: { seconds: error.retryAfter } }
    case 'captcha_required':
      return { key: 'errors.captchaRequired' }
    case 'captcha_invalid':
      return { key: 'auth.captcha.failed' }
    case 'password_weak':
      return {
        key: error.extra.reason === 'common' ? 'errors.passwordCommon' : 'errors.passwordWeak',
      }
    case 'phone_invalid':
      return { key: 'errors.phoneInvalid' }
    case 'otp_invalid':
    case 'totp_invalid':
      return { key: 'auth.otp.wrong' }
    case 'invite_invalid':
      return { key: 'auth.staff.inviteInvalid' }
    case 'token_invalid':
    case 'reset_invalid':
      return { key: 'auth.reset.invalidLink' }
    case 'step_up_required':
      return { key: 'errors.stepUpRequired' }
    case 'validation_error':
      return { key: 'errors.validation' }
    case 'auth_unavailable':
    case 'rate_limiter_unavailable':
    case 'captcha_unavailable':
    case 'demo_unavailable':
      return { key: 'errors.unavailable' }
    default:
      return { key: error.status === 401 ? 'errors.sessionExpired' : 'errors.generic' }
  }
}
