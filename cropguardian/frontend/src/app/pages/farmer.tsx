import { useQueryClient } from '@tanstack/react-query'
import {
  BookOpen,
  Camera,
  ChevronRight,
  CircleCheck,
  CircleHelp,
  Clock,
  ExternalLink,
  Image as ImageIcon,
  KeyRound,
  Leaf,
  LogOut,
  Megaphone,
  Phone,
  ShieldCheck,
  Volume2,
  VolumeX,
} from 'lucide-react'
import { useEffect, useId, useMemo, useRef, useState, type ReactNode } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { BottomTabBar } from '../../components/nav/BottomTabBar'
import { OfflineBanner } from '../../components/nav/OfflineBanner'
import { Badge, SimulatedBadge } from '../../components/ui/badge'
import { Button } from '../../components/ui/button'
import { Card, CardTitle } from '../../components/ui/card'
import { ConfidenceBandChip } from '../../components/ui/chips'
import { Ring } from '../../components/ui/progress'
import { HeroBackground } from '../../components/app/HeroBackground'
import { AnimatedOutlet } from '../../components/app/PageTransition'
import { NativeSelect } from '../../components/ui/controls'
import { EmptyState, ErrorState, SkeletonCard } from '../../components/ui/states'
import {
  DIVISIONS,
  compressPhoto,
  newIdempotencyKey,
  scanKeys,
  uploadScan,
  useAlerts,
  useKbSources,
  useScan,
  useScans,
  type OutbreakAlert,
  type Scan,
} from '../../features/scans/api'
import { ApiError } from '../../lib/api'
import { dayPart, formatDate, formatExact, formatNumber } from '../../lib/format'
import { flushOutbox, outbox } from '../../lib/outbox'
import { useOnline } from '../../lib/useOnline'
import { isLocale } from '../../i18n'
import { useAuth } from '../auth'
import { FormError, LanguageToggle } from '../ui'

const REGION_KEY = 'cg.region'

function useLocale() {
  const { i18n } = useTranslation()
  return isLocale(i18n.language) ? i18n.language : 'bn'
}

function savedRegion(): string {
  try {
    const value = window.localStorage.getItem(REGION_KEY) // forbidden-ok: division is a coarse UI preference (D-032)
    return value && (DIVISIONS as readonly string[]).includes(value) ? value : 'BD-C'
  } catch {
    return 'BD-C'
  }
}

function isNetworkError(err: unknown): boolean {
  return err instanceof ApiError && err.status === 0
}

/** Sends queued photos when the phone is back online; same Idempotency-Key => never a duplicate. */
function OutboxSync({ onCount }: { onCount: (n: number) => void }) {
  const online = useOnline()
  const client = useQueryClient()
  useEffect(() => {
    let cancelled = false
    const run = async () => {
      if (online) {
        const sent = await flushOutbox(
          (item) => uploadScan(item.blob, item.region, item.key),
          isNetworkError,
        )
        if (sent > 0) await client.invalidateQueries({ queryKey: scanKeys.all })
      }
      const left = (await outbox.list()).length
      if (!cancelled) onCount(left)
    }
    void run()
    return () => {
      cancelled = true
    }
  }, [online, client, onCount])
  return null
}

export function FarmerLayout() {
  const [queued, setQueued] = useState(0)
  const { t } = useTranslation()
  return (
    <div className="pb-24">
      <OfflineBanner />
      <OutboxSync onCount={setQueued} />
      {queued > 0 ? (
        <p
          role="status"
          className="mt-3 rounded-md border border-warning bg-warning-bg p-3 text-warning"
        >
          {t('cg.history.queued', { count: queued })}
        </p>
      ) : null}
      <AnimatedOutlet depth="page" />
      <BottomTabBar />
    </div>
  )
}

// ------------------------------------------------------------------------------------- home
export function FarmerHomePage() {
  const { t } = useTranslation()
  const locale = useLocale()
  const { state } = useAuth()
  const scans = useScans()
  const alerts = useAlerts()
  const kb = useKbSources()
  const demo = state?.role?.startsWith('DEMO_') ?? false
  const all = scans.data ?? []
  const diagnosed = all.filter((s) => s.status === 'diagnosed').length
  const confident = all.filter((s) => s.status !== 'not_sure').length
  const now = new Date()
  const n = (x: number) => formatNumber(x, locale)
  const diseases = Object.entries(kb.data?.diseases ?? {})
  const tones = [
    'bg-disease-1',
    'bg-disease-2',
    'bg-disease-3',
    'bg-disease-4',
    'bg-disease-5',
    'bg-disease-6',
    'bg-disease-7',
  ]
  return (
    <section className="space-y-5">
      <div className="relative -mx-4 -mt-2 h-72 overflow-hidden rounded-b-xl">
        <HeroBackground scarecrow={false} />
        <div
          className="absolute inset-0 bg-gradient-to-t from-primary from-30% to-transparent to-70%"
          aria-hidden="true"
        />
        <div className="absolute inset-x-0 bottom-0 p-5 text-primary-on">
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm opacity-90">{formatDate(now, locale)}</p>
            {demo ? <SimulatedBadge /> : null}
          </div>
          <h1 className="mt-1 text-2xl font-bold">
            {t(`farmerHome.greeting.${dayPart(now)}`, { name: state?.display_name ?? '' })}
          </h1>
          <div className="mt-4 grid grid-cols-3 gap-2">
            {[
              [n(all.length), t('cg.ui2.statScans')],
              [n(diagnosed), t('cg.ui2.statDiagnosed')],
              [n(alerts.data?.length ?? 0), t('cg.ui2.statAlerts')],
            ].map(([value, label]) => (
              <div
                key={label}
                className="rounded-lg border border-primary-on px-3 py-2 text-center"
              >
                <p className="text-xl font-bold tabular-nums">{value}</p>
                <p className="text-xs opacity-90">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <Card className="flex items-center gap-4">
        <Ring
          value={all.length ? confident / all.length : 0}
          label={t('cg.ui2.ringTitle')}
          size={84}
        >
          <span className="text-lg font-bold tabular-nums">
            {all.length ? `${n(confident)}/${n(all.length)}` : n(0)}
          </span>
        </Ring>
        <div>
          <p className="text-lg font-semibold">{t('cg.ui2.ringTitle')}</p>
          <p className="text-sm text-muted">
            {all.length ? t('cg.ui2.ringBody') : t('cg.ui2.ringEmpty')}
          </p>
        </div>
      </Card>

      <Button asChild size="xl-farmer" className="rounded-full">
        <Link to="/app/scan">
          <Camera className="h-6 w-6" aria-hidden="true" />
          {t('farmerHome.hero.cta')}
        </Link>
      </Button>
      <p className="-mt-3 text-center text-sm text-muted">{t('cg.scan.riceOnly')}</p>

      {diseases.length ? (
        <div>
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">{t('cg.ui2.diseasesTitle')}</h2>
            <Link
              to="/trust"
              className="min-h-[44px] content-center text-sm text-primary underline"
            >
              {t('cg.ui2.viewAll')}
            </Link>
          </div>
          <ul className="-mx-4 mt-2 flex snap-x gap-3 overflow-x-auto px-4 pb-2">
            {diseases.map(([code, names], idx) => (
              <li
                key={code}
                className="w-36 shrink-0 snap-start overflow-hidden rounded-lg border border-border bg-surface shadow-xs"
              >
                <div
                  className={`flex h-20 items-center justify-center ${tones[idx % tones.length]}`}
                >
                  <Leaf className="h-9 w-9 text-primary-on" aria-hidden="true" />
                </div>
                <div className="p-3">
                  <p className="font-semibold" lang="bn">
                    {locale === 'bn' ? names.bn : names.en}
                  </p>
                  <p className="text-xs text-muted">{t('cg.ui2.diseaseHint')}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <div>
        <h2 className="text-lg font-semibold">{t('farmerHome.alerts.title')}</h2>
        {alerts.isPending ? <SkeletonCard className="mt-2" /> : null}
        {alerts.data && alerts.data.length === 0 ? (
          <p className="mt-2 text-muted">{t('farmerHome.alerts.empty')}</p>
        ) : null}
        <div className="mt-2 space-y-3">
          {alerts.data?.slice(0, 2).map((a) => (
            <AlertCard key={a.id} alert={a} />
          ))}
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold">{t('farmerHome.recent.title')}</h2>
        {scans.isPending ? <SkeletonCard className="mt-2" /> : null}
        {scans.isError ? <FormError error={scans.error} /> : null}
        {scans.data && scans.data.length === 0 ? (
          <EmptyState
            icon={ImageIcon}
            title={t('farmerHome.recent.empty')}
            description={t('farmerHome.recent.hint')}
          />
        ) : null}
        <ul className="mt-2 space-y-2">
          {scans.data?.slice(0, 3).map((s) => (
            <ScanRow key={s.id} scan={s} />
          ))}
        </ul>
      </div>
    </section>
  )
}

function ScanRow({ scan }: { scan: Scan }) {
  const { t } = useTranslation()
  const locale = useLocale()
  const name =
    scan.status === 'diagnosed'
      ? locale === 'bn'
        ? scan.disease_bn
        : scan.disease_en
      : scan.status === 'healthy'
        ? t('cg.history.healthy')
        : t('cg.history.notSure')
  const Icon =
    scan.status === 'diagnosed' ? Leaf : scan.status === 'healthy' ? CircleCheck : CircleHelp
  return (
    <li>
      <Link
        to={`/app/scan/${scan.id}`}
        className="flex min-h-[56px] items-center gap-3 rounded-lg border border-border bg-surface p-3 hover:border-primary"
      >
        <Icon className="h-6 w-6 shrink-0 text-primary" aria-hidden="true" />
        <span className="flex-1">
          <span className="block font-semibold">{name}</span>
          <span className="block text-sm text-muted">{formatExact(scan.created_at, locale)}</span>
        </span>
        {scan.synthetic ? <SimulatedBadge /> : null}
        <ChevronRight className="h-5 w-5 text-muted" aria-hidden="true" />
        <span className="sr-only">{t('cg.history.open')}</span>
      </Link>
    </li>
  )
}

// ------------------------------------------------------------------------------------- scan
export function ScanPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const client = useQueryClient()
  const online = useOnline()
  const cameraRef = useRef<HTMLInputElement>(null)
  const galleryRef = useRef<HTMLInputElement>(null)
  const selectId = useId()
  const [region, setRegion] = useState(savedRegion)
  const [photo, setPhoto] = useState<Blob | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<unknown>(null)
  const [note, setNote] = useState<string | null>(null)

  const preview = useMemo(() => (photo ? URL.createObjectURL(photo) : null), [photo])
  useEffect(() => () => (preview ? URL.revokeObjectURL(preview) : undefined), [preview])

  const choose = async (file: File | undefined) => {
    setError(null)
    setNote(null)
    if (!file) return
    setPhoto(await compressPhoto(file))
  }

  const send = async () => {
    if (!photo) return
    try {
      window.localStorage.setItem(REGION_KEY, region) // forbidden-ok: coarse UI preference
    } catch {
      // preference only
    }
    const key = newIdempotencyKey()
    if (!online) {
      const ok = await outbox.add({ key, region, blob: photo, createdAt: Date.now() })
      setNote(ok ? t('cg.scan.queued') : t('cg.scan.queueFull'))
      setPhoto(null)
      return
    }
    setBusy(true)
    setError(null)
    try {
      const scan = await uploadScan(photo, region, key)
      client.setQueryData(scanKeys.one(scan.id), scan)
      await client.invalidateQueries({ queryKey: scanKeys.all })
      navigate(`/app/scan/${scan.id}`)
    } catch (err) {
      if (isNetworkError(err)) {
        await outbox.add({ key, region, blob: photo, createdAt: Date.now() })
        setNote(t('cg.scan.queued'))
        setPhoto(null)
      } else {
        setError(err)
      }
    } finally {
      setBusy(false)
    }
  }

  const options = DIVISIONS.map((code) => ({
    value: code,
    label: t(`cg.division.${code}`, { defaultValue: code }),
  }))

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">{t('scan.title')}</h1>
      <p className="text-muted">{t('cg.scan.intro')}</p>

      <div>
        <label htmlFor={selectId} className="block font-medium">
          {t('cg.region.label')}
        </label>
        <div className="mt-1">
          <NativeSelect
            id={selectId}
            value={region}
            options={options}
            onChange={(e) => setRegion(e.target.value)}
            aria-describedby={`${selectId}-hint`}
          />
        </div>
        <p id={`${selectId}-hint`} className="mt-1 text-sm text-muted">
          {t('cg.region.hint')}
        </p>
      </div>

      <input
        ref={cameraRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="sr-only"
        tabIndex={-1}
        aria-hidden="true"
        onChange={(e) => void choose(e.target.files?.[0])}
      />
      <input
        ref={galleryRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="sr-only"
        tabIndex={-1}
        aria-hidden="true"
        onChange={(e) => void choose(e.target.files?.[0])}
      />

      {preview && photo ? (
        <Card>
          <p className="font-medium">{t('cg.scan.preview')}</p>
          <img
            src={preview}
            alt={t('cg.scan.preview')}
            className="mt-2 max-h-72 w-full rounded-md object-contain"
          />
          <Button size="xl-farmer" className="mt-4" loading={busy} onClick={() => void send()}>
            <ShieldCheck className="h-6 w-6" aria-hidden="true" />
            {t('cg.scan.send')}
          </Button>
          <Button
            variant="outline"
            className="mt-2 w-full"
            disabled={busy}
            onClick={() => setPhoto(null)}
          >
            {t('cg.scan.change')}
          </Button>
          {busy ? (
            <p role="status" aria-live="polite" className="mt-3 text-center text-muted">
              {t('cg.scan.working')}
            </p>
          ) : null}
        </Card>
      ) : (
        <div className="space-y-3">
          <Button size="xl-farmer" onClick={() => cameraRef.current?.click()}>
            <Camera className="h-6 w-6" aria-hidden="true" />
            {t('cg.scan.camera')}
          </Button>
          <Button size="xl-farmer" variant="outline" onClick={() => galleryRef.current?.click()}>
            <ImageIcon className="h-6 w-6" aria-hidden="true" />
            {t('cg.scan.gallery')}
          </Button>
          <ul className="space-y-1 text-muted">
            <li>{t('scan.hint.oneLeaf')}</li>
            <li>{t('notSure.tipLight')}</li>
          </ul>
        </div>
      )}

      {note ? (
        <p
          role="status"
          className="rounded-md border border-warning bg-warning-bg p-3 text-warning"
        >
          {note}
        </p>
      ) : null}
      <FormError error={error} />
      <p className="text-sm text-muted">{t('cg.scan.privacy')}</p>
    </section>
  )
}

// ------------------------------------------------------------------------------------- result
function useSpeech() {
  const [speaking, setSpeaking] = useState(false)
  const supported = typeof window !== 'undefined' && 'speechSynthesis' in window
  useEffect(() => () => window.speechSynthesis?.cancel(), [])
  const speak = (text: string, lang: string) => {
    if (!supported) return
    window.speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(text)
    u.lang = lang
    u.rate = 0.9
    u.onend = () => setSpeaking(false)
    u.onerror = () => setSpeaking(false)
    setSpeaking(true)
    window.speechSynthesis.speak(u)
  }
  const stop = () => {
    window.speechSynthesis?.cancel()
    setSpeaking(false)
  }
  return { supported, speaking, speak, stop }
}

function ListenButton({ text }: { text: string }) {
  const { t } = useTranslation()
  const { supported, speaking, speak, stop } = useSpeech()
  if (!supported) return null
  return (
    <Button
      variant="secondary"
      size="sm"
      onClick={() => (speaking ? stop() : speak(text, 'bn-BD'))}
    >
      {speaking ? (
        <VolumeX className="h-5 w-5" aria-hidden="true" />
      ) : (
        <Volume2 className="h-5 w-5" aria-hidden="true" />
      )}
      {speaking ? t('cg.result.stop') : t('advice.listen')}
    </Button>
  )
}

function OfficeCard() {
  const { t } = useTranslation()
  return (
    <Card>
      <div className="flex items-start gap-3">
        <Phone className="mt-1 h-6 w-6 shrink-0 text-primary" aria-hidden="true" />
        <div>
          <CardTitle>{t('cg.office.title')}</CardTitle>
          <p className="mt-1">{t('cg.office.body')}</p>
          <p className="mt-2 text-sm text-muted">{t('cg.office.brri')}</p>
        </div>
      </div>
    </Card>
  )
}

export function ResultPage() {
  const { id = '' } = useParams()
  const { t } = useTranslation()
  const locale = useLocale()
  const scan = useScan(id)

  if (scan.isPending) return <SkeletonCard />
  if (scan.isError) {
    const err = scan.error
    return (
      <ErrorState
        title={t('errors.notFound')}
        requestId={err instanceof ApiError ? err.requestId : undefined}
        onRetry={() => void scan.refetch()}
      />
    )
  }
  const s = scan.data
  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between gap-2">
        <h1 className="text-2xl font-semibold">{t('result.title')}</h1>
        {s.synthetic ? <SimulatedBadge /> : null}
      </div>
      <p className="text-sm text-muted">{formatExact(s.created_at, locale)}</p>

      {s.status === 'diagnosed' ? <Diagnosed scan={s} /> : null}
      {s.status === 'healthy' ? (
        <Card className="border-success">
          <div className="flex items-center gap-3">
            <CircleCheck className="h-10 w-10 text-success" aria-hidden="true" />
            <div>
              <p className="text-xl font-semibold">{t('result.healthy')}</p>
              {s.confidence_band ? <ConfidenceBandChip band={s.confidence_band} /> : null}
            </div>
          </div>
          <p className="mt-3">{t('cg.result.healthyBody')}</p>
          <p className="mt-2 text-sm text-muted">{t('cg.result.aiNote')}</p>
        </Card>
      ) : null}
      {s.status === 'not_sure' ? <NotSure scan={s} /> : null}

      <Button asChild size="xl-farmer" variant="outline">
        <Link to="/app/scan">
          <Camera className="h-6 w-6" aria-hidden="true" />
          {t('cg.result.scanAgain')}
        </Link>
      </Button>

      <details className="rounded-md border border-border p-3 text-sm text-muted">
        <summary className="cursor-pointer">{t('cg.result.technical')}</summary>
        <p className="mt-2">
          {t('cg.result.technicalBody', {
            model: s.model ?? '-',
            prompt: s.prompt_version ?? '-',
            kb: s.kb_version,
          })}
        </p>
      </details>
    </section>
  )
}

function Diagnosed({ scan }: { scan: Scan }) {
  const { t } = useTranslation()
  const locale = useLocale()
  const name = locale === 'bn' ? scan.disease_bn : scan.disease_en
  const advice = scan.advice
  const readText = advice
    ? [name, advice.summary_bn, ...advice.steps_bn, advice.safety_bn].join('। ')
    : (name ?? '')
  return (
    <>
      <Card className="border-primary">
        <p className="text-sm font-medium text-muted">{t('cg.result.diagnosed')}</p>
        <p className="mt-1 text-2xl font-semibold text-primary">{name}</p>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          {scan.confidence_band ? <ConfidenceBandChip band={scan.confidence_band} /> : null}
        </div>
        <p className="mt-3 text-sm text-muted">{t('cg.result.aiNote')}</p>
      </Card>

      {advice ? (
        <Card>
          <div className="flex items-center justify-between gap-2">
            <CardTitle>{t('cg.result.stepsTitle')}</CardTitle>
            <ListenButton text={readText} />
          </div>
          <p className="mt-2 text-lg" lang="bn">
            {advice.summary_bn}
          </p>
          <ol className="mt-3 list-decimal space-y-2 ps-6 text-lg" lang="bn">
            {advice.steps_bn.map((step, i) => (
              <li key={i}>{step}</li>
            ))}
          </ol>
          <p
            className="mt-4 rounded-md border border-warning bg-warning-bg p-3 text-warning"
            lang="bn"
          >
            {advice.safety_bn}
          </p>
          <p className="mt-3 text-sm text-muted">
            {scan.advice_source === 'static_card'
              ? t('cg.result.fromSource')
              : t('cg.result.fromLlm')}
          </p>
          <p className="mt-1 text-sm text-muted">{t('advice.basedOn')}</p>
        </Card>
      ) : (
        <Card>
          <p>{t('cg.result.noAdvice')}</p>
        </Card>
      )}

      {scan.citations.length > 0 ? (
        <Card>
          <CardTitle>{t('cg.result.sourcesTitle')}</CardTitle>
          <ul className="mt-3 space-y-3">
            {scan.citations.map((c) => (
              <li key={c.id} className="rounded-md border border-border p-3">
                <p className="flex items-start gap-2 font-medium">
                  <BookOpen className="mt-1 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                  <span>{c.title}</span>
                </p>
                <p className="mt-1 text-sm text-muted">
                  {c.publisher}
                  <span aria-hidden="true">{' · '}</span>
                  {t('cg.result.page', { page: formatNumber(c.page, locale) })}
                </p>
                <blockquote className="mt-2 border-s-4 border-primary ps-3 text-sm" lang="bn">
                  {c.excerpt}
                </blockquote>
                <a
                  href={c.url}
                  className="mt-2 inline-flex min-h-[44px] items-center gap-1 text-primary underline"
                >
                  {t('cg.result.openSource')}
                  <ExternalLink className="h-4 w-4" aria-hidden="true" />
                </a>
              </li>
            ))}
          </ul>
        </Card>
      ) : null}
      <OfficeCard />
    </>
  )
}

function NotSure({ scan }: { scan: Scan }) {
  const { t } = useTranslation()
  const reason = scan.reason ?? 'low_confidence'
  const body = t(`cg.reason.${reason}`)
  return (
    <>
      <Card className="border-sky">
        <div className="flex items-start gap-3">
          <CircleHelp className="h-10 w-10 shrink-0 text-sky" aria-hidden="true" />
          <div>
            <p className="text-xl font-semibold">{t('notSure.title')}</p>
            <p className="mt-1">{body}</p>
            <p className="mt-2 text-muted">{t('notSure.body')}</p>
          </div>
        </div>
        <ul className="mt-3 list-disc space-y-1 ps-6">
          <li>{t('notSure.tipLight')}</li>
          <li>{t('notSure.tipClose')}</li>
          <li>{t('scan.hint.blurry')}</li>
        </ul>
        <div className="mt-3">
          <ListenButton text={[t('notSure.title'), body, t('notSure.tipLight')].join('। ')} />
        </div>
      </Card>
      <OfficeCard />
    </>
  )
}

// ------------------------------------------------------------------------------------- history
export function HistoryPage() {
  const { t } = useTranslation()
  const scans = useScans()
  return (
    <section>
      <h1 className="text-2xl font-semibold">{t('history.title')}</h1>
      {scans.isPending ? <SkeletonCard className="mt-4" /> : null}
      {scans.isError ? <FormError error={scans.error} /> : null}
      {scans.data && scans.data.length === 0 ? (
        <EmptyState icon={Clock} title={t('history.empty')} description={t('history.hint')} />
      ) : null}
      <ul className="mt-4 space-y-2">
        {scans.data?.map((s) => (
          <ScanRow key={s.id} scan={s} />
        ))}
      </ul>
    </section>
  )
}

// ------------------------------------------------------------------------------------- alerts
export function AlertCard({ alert, children }: { alert: OutbreakAlert; children?: ReactNode }) {
  const { t } = useTranslation()
  const locale = useLocale()
  const disease = (locale === 'bn' ? alert.disease_bn : alert.disease_en) ?? alert.disease
  const region = locale === 'bn' ? alert.region_bn : alert.region_en
  const days = Math.max(
    1,
    Math.ceil((Date.parse(alert.window_end) - Date.parse(alert.window_start)) / 86_400_000),
  )
  return (
    <Card className="border-warning">
      <div className="flex items-start gap-3">
        <Megaphone className="mt-1 h-6 w-6 shrink-0 text-warning" aria-hidden="true" />
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone="warning">{t('cg.alerts.unverified')}</Badge>
            {alert.synthetic ? <SimulatedBadge /> : null}
          </div>
          <p className="mt-2 text-lg font-semibold">{disease}</p>
          <p className="mt-1">
            {t('cg.alerts.body', {
              region,
              count: formatNumber(alert.case_count, locale),
              days: formatNumber(days, locale),
              disease,
            })}
          </p>
          {alert.status === 'approved' ? (
            <p className="mt-2 text-sm text-muted">{t('cg.alerts.approvedNote')}</p>
          ) : null}
          {children}
        </div>
      </div>
    </Card>
  )
}

export function AlertsPage() {
  const { t } = useTranslation()
  const alerts = useAlerts()
  return (
    <section>
      <h1 className="text-2xl font-semibold">{t('cg.alerts.title')}</h1>
      {alerts.isPending ? <SkeletonCard className="mt-4" /> : null}
      {alerts.isError ? <FormError error={alerts.error} /> : null}
      {alerts.data && alerts.data.length === 0 ? (
        <EmptyState
          icon={Megaphone}
          title={t('cg.alerts.empty')}
          description={t('cg.alerts.emptyHint')}
        />
      ) : null}
      <div className="mt-4 space-y-3">
        {alerts.data?.map((a) => (
          <AlertCard key={a.id} alert={a} />
        ))}
      </div>
    </section>
  )
}

// ------------------------------------------------------------------------------------- more
export function MorePage() {
  const { t } = useTranslation()
  const { signOut } = useAuth()
  const linkClass =
    'flex min-h-[56px] items-center gap-3 rounded-lg border border-border bg-surface p-3 hover:border-primary'
  return (
    <section className="space-y-3">
      <h1 className="text-2xl font-semibold">{t('cg.more.title')}</h1>
      <div className="flex items-center justify-between gap-2 rounded-lg border border-border bg-surface p-3">
        <span>{t('cg.more.language')}</span>
        <LanguageToggle />
      </div>
      <Link to="/trust" className={linkClass}>
        <ShieldCheck className="h-6 w-6 text-primary" aria-hidden="true" />
        <span className="flex-1">{t('cg.more.trust')}</span>
        <ChevronRight className="h-5 w-5 text-muted" aria-hidden="true" />
      </Link>
      <Link to="/account/sessions" className={linkClass}>
        <KeyRound className="h-6 w-6 text-primary" aria-hidden="true" />
        <span className="flex-1">{t('cg.more.sessions')}</span>
        <ChevronRight className="h-5 w-5 text-muted" aria-hidden="true" />
      </Link>
      <Button variant="outline" className="w-full" onClick={() => void signOut()}>
        <LogOut className="h-5 w-5" aria-hidden="true" />
        {t('cg.more.logout')}
      </Button>
    </section>
  )
}
