import { zodResolver } from '@hookform/resolvers/zod'
import { useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useTranslation } from 'react-i18next'
import { Link, useLocation, useNavigate, useSearchParams } from 'react-router-dom'
import { z } from 'zod'
import { api, ApiError } from '../../lib/api'
import { authApi, homePath, type NextStep, type SessionReply } from '../../lib/authApi'
import { safeReturnTo } from '../../lib/returnTo'
import { useAuth } from '../auth'
import { Button, Field, FormError, Notice } from '../ui'
import { useCaptcha } from '../useCaptcha'

const V = 'errors.validation'

function destination(reply: SessionReply, returnTo: string | null): string {
  const next: NextStep = reply.next
  if (next === 'totp') return '/login/totp'
  if (next === 'setup_totp') return '/setup-2fa'
  return safeReturnTo(returnTo, reply.user ? homePath(reply.user.role) : '/')
}

function useAfterSignIn() {
  const { refresh } = useAuth()
  const navigate = useNavigate()
  const [params] = useSearchParams()
  return async (reply: SessionReply) => {
    await refresh()
    navigate(destination(reply, params.get('return_to')), { replace: true })
  }
}

// --- login ----------------------------------------------------------------------------------
const loginSchema = z.object({
  identifier: z.string().trim().min(1, V).max(254, V),
  password: z.string().min(1, V).max(128, V),
  keep: z.boolean(),
})
type LoginValues = z.infer<typeof loginSchema>

export function LoginPage({ staff = false }: { staff?: boolean }) {
  const { t } = useTranslation()
  const afterSignIn = useAfterSignIn()
  const [needCaptcha, setNeedCaptcha] = useState(false)
  const captcha = useCaptcha(needCaptcha)
  const [error, setError] = useState<unknown>(null)
  const [show, setShow] = useState(false)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { identifier: '', password: '', keep: false },
  })

  const onSubmit = handleSubmit(async (values) => {
    setError(null)
    try {
      const reply = await authApi.login({
        identifier: values.identifier,
        password: values.password,
        keep_signed_in: values.keep && !staff,
        captcha: captcha.consume() ?? undefined,
      })
      await afterSignIn(reply)
    } catch (err) {
      if (err instanceof ApiError && err.code === 'captcha_required') setNeedCaptcha(true)
      if (err instanceof ApiError && err.code === 'verification_required') {
        setError(err)
        return
      }
      setError(err)
    }
  })

  return (
    <section>
      <h1 className="text-2xl font-semibold">
        {t(staff ? 'auth.staff.title' : 'auth.login.title')}
      </h1>
      <form onSubmit={onSubmit} noValidate>
        <Field
          label={t('auth.login.identifier')}
          autoComplete="username"
          inputMode={staff ? 'email' : 'text'}
          error={errors.identifier ? t(V) : undefined}
          {...register('identifier')}
        />
        <Field
          label={t('auth.login.password')}
          type={show ? 'text' : 'password'}
          autoComplete="current-password"
          error={errors.password ? t(V) : undefined}
          {...register('password')}
        />
        <button
          type="button"
          aria-pressed={show}
          className="mt-2 min-h-[44px] text-sm text-primary underline"
          onClick={() => setShow((v) => !v)}
        >
          {t(show ? 'auth.login.hidePassword' : 'auth.login.showPassword')}
        </button>
        {!staff ? (
          <label className="mt-2 flex min-h-[44px] items-center gap-2">
            <input type="checkbox" {...register('keep')} />
            <span>{t('auth.login.keepSignedIn')}</span>
          </label>
        ) : null}
        {needCaptcha ? (
          <p role="status" className="mt-4 text-sm text-muted">
            {t(captcha.status === 'failed' ? 'auth.captcha.failed' : 'auth.captcha.verifying')}
          </p>
        ) : null}
        <FormError error={error} />
        <Button
          type="submit"
          disabled={isSubmitting || (needCaptcha && captcha.status === 'solving')}
        >
          {t('auth.login.submit')}
        </Button>
      </form>
      <p className="mt-6">
        <Link
          className="inline-flex min-h-[44px] items-center text-primary underline"
          to="/forgot-password"
        >
          {t('auth.login.forgot')}
        </Link>
      </p>
      {!staff ? (
        <>
          <p className="mt-2">
            {t('auth.login.noAccount')}{' '}
            <Link
              className="inline-flex min-h-[44px] items-center text-primary underline"
              to="/register"
            >
              {t('auth.login.registerLink')}
            </Link>
          </p>
          <p className="mt-2">
            <Link
              className="inline-flex min-h-[44px] items-center text-primary underline"
              to="/demo"
            >
              {t('auth.login.tryDemo')}
            </Link>
          </p>
        </>
      ) : null}
    </section>
  )
}

// --- farmer registration --------------------------------------------------------------------
interface ConsentWording {
  version: string
  consents: {
    purpose: 'service' | 'training_use' | 'push_alerts'
    required: boolean
    title: Record<'bn' | 'en', string>
    body: Record<'bn' | 'en', string>
  }[]
}

const registerSchema = z.object({
  display_name: z.string().trim().min(1, V).max(80, V),
  phone: z.string().trim().min(6, V).max(40, V),
  password: z.string().min(8, V).max(128, V),
  accept_service: z.literal(true, { error: V }),
  training_use: z.boolean(),
  push_alerts: z.boolean(),
  website: z.string().max(200),
})
type RegisterValues = z.infer<typeof registerSchema>

export function RegisterPage() {
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const captcha = useCaptcha(true)
  const [error, setError] = useState<unknown>(null)
  const wording = useQuery({
    queryKey: ['consent-wording'],
    queryFn: () => api.get<ConsentWording>('/api/v1/consents/texts', { quiet401: true }),
    staleTime: Infinity,
  })
  const lang: 'bn' | 'en' = i18n.language === 'en' ? 'en' : 'bn'
  const pick = (texts: Record<'bn' | 'en', string> | undefined): string =>
    texts ? (lang === 'en' ? texts.en : texts.bn) : ''
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      display_name: '',
      phone: '',
      password: '',
      training_use: false,
      push_alerts: false,
      website: '',
    },
  })

  const onSubmit = handleSubmit(async (values) => {
    setError(null)
    const token = captcha.consume()
    if (!token) {
      setError(new ApiError(400, 'captcha_required'))
      return
    }
    try {
      await authApi.registerFarmer({
        phone: values.phone,
        password: values.password,
        display_name: values.display_name,
        locale: lang,
        accept_service: true,
        training_use: values.training_use,
        push_alerts: values.push_alerts,
        captcha: token,
        website: values.website,
      })
      // the phone number travels in router state, never in the URL
      navigate('/verify', { state: { phone: values.phone } })
    } catch (err) {
      setError(err)
    }
  })

  const optional = wording.data?.consents.filter((c) => !c.required) ?? []
  const service = wording.data?.consents.find((c) => c.purpose === 'service')

  return (
    <section>
      <h1 className="text-2xl font-semibold">{t('auth.register.title')}</h1>
      <form onSubmit={onSubmit} noValidate>
        <Field
          label={t('auth.register.name')}
          autoComplete="name"
          error={errors.display_name ? t(V) : undefined}
          {...register('display_name')}
        />
        <Field
          label={t('auth.register.phone')}
          hint={t('auth.register.phoneHint')}
          type="tel"
          inputMode="tel"
          autoComplete="tel"
          error={errors.phone ? t(V) : undefined}
          {...register('phone')}
        />
        <Field
          label={t('auth.register.password')}
          hint={t('auth.register.passwordHint')}
          type="password"
          autoComplete="new-password"
          error={errors.password ? t(V) : undefined}
          {...register('password')}
        />
        {/* honeypot: hidden from people and assistive tech, bots fill it in */}
        <div aria-hidden="true" className="absolute left-[-9999px] h-0 w-0 overflow-hidden">
          <label>
            {t('auth.captcha.honeypot')}
            <input type="text" tabIndex={-1} autoComplete="off" {...register('website')} />
          </label>
        </div>
        {/* The consent labels ARE the checkbox names, so the fieldset only exists once the wording has
            loaded: an unnamed checkbox is a critical a11y failure (axe `label`) and a consent the
            farmer cannot read must not be submittable (fail closed). */}
        {service ? (
          <fieldset className="mt-6">
            <legend className="font-medium">{pick(service.title)}</legend>
            <p className="mt-1 text-sm text-muted">{pick(service.body)}</p>
            <label className="mt-2 flex min-h-[44px] items-start gap-2">
              <input type="checkbox" className="mt-1" {...register('accept_service')} />
              <span>{pick(service.title)}</span>
            </label>
            {errors.accept_service ? (
              <p role="alert" className="text-sm text-danger">
                {t(V)}
              </p>
            ) : null}
            {optional.map((c) => (
              <div key={c.purpose} className="mt-3">
                <label className="flex min-h-[44px] items-start gap-2">
                  <input
                    type="checkbox"
                    className="mt-1"
                    {...register(c.purpose === 'training_use' ? 'training_use' : 'push_alerts')}
                  />
                  <span>
                    <span className="font-medium">{pick(c.title)}</span>
                    <span className="block text-sm text-muted">{pick(c.body)}</span>
                  </span>
                </label>
              </div>
            ))}
          </fieldset>
        ) : wording.isError ? (
          <p role="alert" className="mt-6 text-danger">
            {t('errors.unavailable')}
          </p>
        ) : (
          <p role="status" className="mt-6 text-muted">
            {t('common.loading')}
          </p>
        )}
        <p role="status" className="mt-4 text-sm text-muted">
          {t(
            captcha.status === 'failed'
              ? 'auth.captcha.failed'
              : captcha.status === 'ready'
                ? 'auth.captcha.label'
                : 'auth.captcha.verifying',
          )}
        </p>
        <FormError error={error} />
        <Button type="submit" disabled={isSubmitting || captcha.status !== 'ready' || !service}>
          {t('auth.register.submit')}
        </Button>
      </form>
      <p className="mt-6">
        {t('auth.register.haveAccount')}{' '}
        <Link className="inline-flex min-h-[44px] items-center text-primary underline" to="/login">
          {t('auth.register.loginLink')}
        </Link>
      </p>
    </section>
  )
}

// --- OTP verification -----------------------------------------------------------------------
const otpSchema = z.object({
  phone: z.string().trim().min(6, V).max(40, V),
  code: z.string().regex(/^[0-9]{6}$/, V),
})
type OtpValues = z.infer<typeof otpSchema>

export function VerifyOtpPage() {
  const { t } = useTranslation()
  const location = useLocation()
  const afterSignIn = useAfterSignIn()
  const statePhone = (location.state as { phone?: string } | null)?.phone ?? ''
  const [error, setError] = useState<unknown>(null)
  const [seconds, setSeconds] = useState(60)
  const [resent, setResent] = useState(false)
  const {
    register,
    handleSubmit,
    getValues,
    formState: { errors, isSubmitting },
  } = useForm<OtpValues>({
    resolver: zodResolver(otpSchema),
    defaultValues: { phone: statePhone, code: '' },
  })

  useEffect(() => {
    if (seconds <= 0) return
    const id = setTimeout(() => setSeconds((s) => s - 1), 1000)
    return () => clearTimeout(id)
  }, [seconds])

  const onSubmit = handleSubmit(async (values) => {
    setError(null)
    try {
      await afterSignIn(
        await authApi.otpVerify({ phone: values.phone, code: values.code, keep_signed_in: true }),
      )
    } catch (err) {
      setError(err)
    }
  })

  const resend = async () => {
    setError(null)
    try {
      await authApi.otpSend({ phone: getValues('phone'), purpose: 'register' })
      setResent(true)
      setSeconds(60)
    } catch (err) {
      setError(err)
    }
  }

  return (
    <section>
      <h1 className="text-2xl font-semibold">{t('auth.otp.title')}</h1>
      <p className="mt-2 text-muted">{t('auth.otp.sent')}</p>
      <form onSubmit={onSubmit} noValidate>
        {statePhone ? (
          <input type="hidden" {...register('phone')} />
        ) : (
          <Field
            label={t('auth.register.phone')}
            type="tel"
            inputMode="tel"
            autoComplete="tel"
            error={errors.phone ? t(V) : undefined}
            {...register('phone')}
          />
        )}
        <Field
          label={t('auth.otp.code')}
          inputMode="numeric"
          autoComplete="one-time-code"
          maxLength={6}
          error={errors.code ? t(V) : undefined}
          {...register('code')}
        />
        {resent ? <Notice>{t('auth.otp.sent')}</Notice> : null}
        <FormError error={error} />
        <Button type="submit" disabled={isSubmitting}>
          {t('auth.otp.submit')}
        </Button>
      </form>
      <button
        type="button"
        className="mt-4 min-h-[48px] text-primary underline disabled:text-muted disabled:no-underline"
        disabled={seconds > 0}
        onClick={() => void resend()}
      >
        {seconds > 0 ? t('auth.otp.resendIn', { seconds }) : t('auth.otp.resend')}
      </button>
    </section>
  )
}

// --- forgot / reset -------------------------------------------------------------------------
const forgotSchema = z.object({ identifier: z.string().trim().min(1, V).max(254, V) })

export function ForgotPage() {
  const { t } = useTranslation()
  const captcha = useCaptcha(true)
  const [done, setDone] = useState(false)
  const [error, setError] = useState<unknown>(null)
  const [submitted, setSubmitted] = useState('')
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<z.infer<typeof forgotSchema>>({
    resolver: zodResolver(forgotSchema),
    defaultValues: { identifier: '' },
  })

  const onSubmit = handleSubmit(async (values) => {
    setError(null)
    try {
      setSubmitted(values.identifier)
      await authApi.forgot({
        identifier: values.identifier,
        captcha: captcha.consume() ?? undefined,
      })
      setDone(true)
    } catch (err) {
      setError(err)
    }
  })

  return (
    <section>
      <h1 className="text-2xl font-semibold">{t('auth.forgot.title')}</h1>
      <p className="mt-2 text-muted">{t('auth.forgot.subtitle')}</p>
      {done ? (
        <>
          <Notice>{t('auth.forgot.sentGeneric')}</Notice>
          {!submitted.includes('@') ? (
            <Link
              className="mt-4 inline-flex min-h-[48px] items-center text-primary underline"
              to="/reset-password"
              state={{ phone: submitted }}
            >
              {t('auth.reset.title')}
            </Link>
          ) : null}
        </>
      ) : (
        <form onSubmit={onSubmit} noValidate>
          <Field
            label={t('auth.login.identifier')}
            autoComplete="username"
            error={errors.identifier ? t(V) : undefined}
            {...register('identifier')}
          />
          <FormError error={error} />
          <Button type="submit" disabled={isSubmitting || captcha.status === 'solving'}>
            {t('auth.forgot.submit')}
          </Button>
        </form>
      )}
    </section>
  )
}

const resetSchema = z.object({
  new_password: z.string().min(8, V).max(128, V),
  phone: z.string().max(40).optional(),
  code: z
    .string()
    .regex(/^[0-9]{6}$/, V)
    .or(z.literal('')),
})

export function ResetPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const [params] = useSearchParams()
  // the emailed token is read once and then removed from the address bar and history
  const [token] = useState(() => params.get('token') ?? '')
  useEffect(() => {
    if (token) navigate(location.pathname, { replace: true })
  }, [token, navigate, location.pathname])
  const statePhone = (location.state as { phone?: string } | null)?.phone ?? ''
  const [error, setError] = useState<unknown>(null)
  const [done, setDone] = useState(false)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<z.infer<typeof resetSchema>>({
    resolver: zodResolver(resetSchema),
    defaultValues: { new_password: '', phone: statePhone, code: '' },
  })

  const onSubmit = handleSubmit(async (values) => {
    setError(null)
    try {
      await authApi.reset(
        token
          ? { new_password: values.new_password, token }
          : { new_password: values.new_password, phone: values.phone, code: values.code },
      )
      setDone(true)
    } catch (err) {
      setError(err)
    }
  })

  if (done) {
    return (
      <section>
        <h1 className="text-2xl font-semibold">{t('auth.reset.title')}</h1>
        <Notice>{t('auth.reset.done')}</Notice>
        <p className="mt-2 text-muted">{t('auth.reset.sessionsEnded')}</p>
        <Link
          className="mt-4 inline-flex min-h-[48px] items-center text-primary underline"
          to="/login"
        >
          {t('auth.login.submit')}
        </Link>
      </section>
    )
  }
  return (
    <section>
      <h1 className="text-2xl font-semibold">{t('auth.reset.title')}</h1>
      <form onSubmit={onSubmit} noValidate>
        {!token ? (
          <>
            <Field
              label={t('auth.register.phone')}
              type="tel"
              inputMode="tel"
              autoComplete="tel"
              {...register('phone')}
            />
            <Field
              label={t('auth.otp.code')}
              inputMode="numeric"
              autoComplete="one-time-code"
              maxLength={6}
              error={errors.code ? t(V) : undefined}
              {...register('code')}
            />
          </>
        ) : null}
        <Field
          label={t('auth.reset.newPassword')}
          type="password"
          autoComplete="new-password"
          error={errors.new_password ? t(V) : undefined}
          {...register('new_password')}
        />
        <FormError error={error} />
        <Button type="submit" disabled={isSubmitting}>
          {t('auth.reset.submit')}
        </Button>
      </form>
    </section>
  )
}

// --- staff invitation -----------------------------------------------------------------------
const inviteSchema = z.object({
  display_name: z.string().trim().min(1, V).max(80, V),
  password: z.string().min(12, V).max(128, V),
})

export function AcceptInvitePage() {
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const [params] = useSearchParams()
  const [token] = useState(() => params.get('token') ?? '')
  useEffect(() => {
    if (token) navigate(location.pathname, { replace: true })
  }, [token, navigate, location.pathname])
  const [error, setError] = useState<unknown>(null)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<z.infer<typeof inviteSchema>>({
    resolver: zodResolver(inviteSchema),
    defaultValues: { display_name: '', password: '' },
  })

  const onSubmit = handleSubmit(async (values) => {
    setError(null)
    try {
      await authApi.registerStaff({
        token,
        password: values.password,
        display_name: values.display_name,
        locale: i18n.language === 'en' ? 'en' : 'bn',
      })
      navigate('/staff', { replace: true })
    } catch (err) {
      setError(err)
    }
  })

  return (
    <section>
      <h1 className="text-2xl font-semibold">{t('auth.staff.title')}</h1>
      <p className="mt-2 text-muted">{t('auth.staff.subtitle')}</p>
      <form onSubmit={onSubmit} noValidate>
        <Field
          label={t('auth.register.name')}
          autoComplete="name"
          error={errors.display_name ? t(V) : undefined}
          {...register('display_name')}
        />
        <Field
          label={t('auth.register.password')}
          hint={t('auth.staff.passwordHint')}
          type="password"
          autoComplete="new-password"
          error={errors.password ? t(V) : undefined}
          {...register('password')}
        />
        <FormError error={error} />
        <Button type="submit" disabled={isSubmitting || !token}>
          {t('auth.staff.submit')}
        </Button>
      </form>
    </section>
  )
}

// --- two-factor -----------------------------------------------------------------------------
const totpSchema = z.object({ code: z.string().trim().min(6, V).max(16, V) })

export function TotpPage() {
  const { t } = useTranslation()
  const afterSignIn = useAfterSignIn()
  const [recovery, setRecovery] = useState(false)
  const [error, setError] = useState<unknown>(null)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<z.infer<typeof totpSchema>>({
    resolver: zodResolver(totpSchema),
    defaultValues: { code: '' },
  })

  const onSubmit = handleSubmit(async (values) => {
    setError(null)
    try {
      await afterSignIn(await authApi.loginTotp({ code: values.code, recovery }))
    } catch (err) {
      setError(err)
    }
  })

  return (
    <section>
      <h1 className="text-2xl font-semibold">{t('auth.totp.title')}</h1>
      <p className="mt-2 text-muted">{t('auth.totp.subtitle')}</p>
      <form onSubmit={onSubmit} noValidate>
        <Field
          label={t(recovery ? 'auth.totp.recoveryCode' : 'auth.totp.code')}
          inputMode={recovery ? 'text' : 'numeric'}
          autoComplete="one-time-code"
          maxLength={16}
          error={errors.code ? t(V) : undefined}
          {...register('code')}
        />
        <FormError error={error} />
        <Button type="submit" disabled={isSubmitting}>
          {t('auth.totp.submit')}
        </Button>
      </form>
      <button
        type="button"
        className="mt-4 min-h-[48px] text-primary underline"
        onClick={() => setRecovery((v) => !v)}
      >
        {t('auth.totp.useRecovery')}
      </button>
    </section>
  )
}

export function SetupTotpPage() {
  const { t } = useTranslation()
  const { refresh } = useAuth()
  const navigate = useNavigate()
  const setup = useQuery({
    queryKey: ['totp-setup'],
    queryFn: () => authApi.totpSetup(),
    staleTime: Infinity,
    gcTime: 0,
    retry: false,
    refetchOnWindowFocus: false,
  })
  const [codes, setCodes] = useState<string[] | null>(null)
  const [error, setError] = useState<unknown>(null)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<z.infer<typeof totpSchema>>({
    resolver: zodResolver(totpSchema),
    defaultValues: { code: '' },
  })

  const onSubmit = handleSubmit(async (values) => {
    setError(null)
    try {
      const reply = await authApi.totpConfirm(values.code)
      setCodes(reply.recovery_codes ?? [])
    } catch (err) {
      setError(err)
    }
  })

  if (codes) {
    return (
      <section>
        <h1 className="text-2xl font-semibold">{t('auth.totp.recoveryTitle')}</h1>
        <p role="alert" className="mt-2 text-warning">
          {t('auth.totp.recoveryWarn')}
        </p>
        <ul className="mt-4 grid grid-cols-2 gap-2 font-mono">
          {codes.map((c) => (
            <li key={c} className="rounded-md border border-border bg-surface p-2">
              {c}
            </li>
          ))}
        </ul>
        <Button
          type="button"
          onClick={async () => {
            await refresh()
            navigate('/', { replace: true })
          }}
        >
          {t('auth.totp.recoveryDone')}
        </Button>
      </section>
    )
  }
  return (
    <section>
      <h1 className="text-2xl font-semibold">{t('auth.totp.setupTitle')}</h1>
      <p className="mt-2 text-muted">{t('auth.totp.setupScan')}</p>
      {setup.isPending ? <p role="status">{t('common.loading')}</p> : null}
      {setup.isError ? <FormError error={setup.error} /> : null}
      {setup.data ? (
        <>
          <p className="mt-4 text-sm text-muted">{t('auth.totp.secretLabel')}</p>
          <code
            className="block break-all rounded-md border border-border bg-surface p-3 font-mono"
            data-testid="totp-secret"
          >
            {setup.data.secret}
          </code>
          <form onSubmit={onSubmit} noValidate>
            <Field
              label={t('auth.totp.setupConfirm')}
              inputMode="numeric"
              autoComplete="one-time-code"
              maxLength={6}
              error={errors.code ? t(V) : undefined}
              {...register('code')}
            />
            <FormError error={error} />
            <Button type="submit" disabled={isSubmitting}>
              {t('auth.totp.submit')}
            </Button>
          </form>
        </>
      ) : null}
    </section>
  )
}
