import { BookOpen, CircleSlash, ExternalLink, ShieldCheck } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Badge } from '../../components/ui/badge'
import { Card, CardTitle } from '../../components/ui/card'
import { ErrorState, SkeletonCard } from '../../components/ui/states'
import { useKbSources } from '../../features/scans/api'
import { formatNumber } from '../../lib/format'
import { isLocale } from '../../i18n'
import { ApiError } from '../../lib/api'

const HONESTY_KEYS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] as const

/** Public Trust Centre (Gantt P4 step 6): sources, deliberate exclusions, limits, honesty markers. */
export function TrustPage() {
  const { t, i18n } = useTranslation()
  const locale = isLocale(i18n.language) ? i18n.language : 'bn'
  const kb = useKbSources()
  const honesty = HONESTY_KEYS.map((k) => t(`cg.trust.honesty.${k}`))

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">{t('cg.trust.title')}</h1>
      <p className="text-muted">{t('cg.trust.intro')}</p>

      <Card>
        <CardTitle>{t('cg.trust.honestyTitle')}</CardTitle>
        <ul className="mt-3 space-y-2">
          {honesty.map((line) => (
            <li key={line} className="flex items-start gap-2">
              <ShieldCheck className="mt-1 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
              <span>{line}</span>
            </li>
          ))}
        </ul>
        <Badge tone="neutral" className="mt-3">
          {t('cg.trust.notMeasured')}
        </Badge>
      </Card>

      {kb.isPending ? <SkeletonCard /> : null}
      {kb.isError ? (
        <ErrorState
          requestId={kb.error instanceof ApiError ? kb.error.requestId : undefined}
          onRetry={() => void kb.refetch()}
        />
      ) : null}
      {kb.data ? (
        <>
          <Card>
            <CardTitle>{t('cg.trust.sourcesTitle')}</CardTitle>
            <p className="mt-1 text-sm text-muted">{kb.data.transcription}</p>
            <ul className="mt-3 space-y-3">
              {kb.data.sources.map((s) => (
                <li key={s.id} className="rounded-md border border-border p-3">
                  <p className="flex items-start gap-2 font-medium" lang="bn">
                    <BookOpen className="mt-1 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                    <span>{s.title}</span>
                  </p>
                  <p className="mt-1 text-sm text-muted">
                    {s.publisher}
                    <span aria-hidden="true">{' · '}</span>
                    {t('cg.trust.chunks', { count: s.chunks, n: formatNumber(s.chunks, locale) })}
                  </p>
                  <a
                    href={s.url}
                    className="mt-1 inline-flex min-h-[44px] items-center gap-1 text-primary underline"
                  >
                    {t('cg.result.openSource')}
                    <ExternalLink className="h-4 w-4" aria-hidden="true" />
                  </a>
                </li>
              ))}
            </ul>
          </Card>

          <Card>
            <CardTitle>{t('cg.trust.excludedTitle')}</CardTitle>
            <p className="mt-1 text-sm text-muted">{kb.data.policy}</p>
            <ul className="mt-3 space-y-1 text-sm">
              {kb.data.excluded.map((e) => (
                <li key={`${e.source_id}-${e.page}`} className="flex items-start gap-2">
                  <CircleSlash className="mt-0.5 h-4 w-4 shrink-0 text-muted" aria-hidden="true" />
                  <span>
                    {e.source_id}
                    <span aria-hidden="true">{' · '}</span>
                    {e.reason}
                  </span>
                </li>
              ))}
            </ul>
          </Card>

          <Card>
            <CardTitle>{t('cg.trust.limitsTitle')}</CardTitle>
            <dl className="mt-3 space-y-2 text-sm">
              {Object.entries({
                confidence: kb.data.limits.confidence,
                retrieval: kb.data.limits.retrieval,
                image_retention: kb.data.limits.image_retention,
                crops: kb.data.limits.crops.join(', '),
                abstain_below: String(kb.data.limits.abstain_below),
                outbreak_rule: `${kb.data.limits.outbreak_rule.min_cases} / ${kb.data.limits.outbreak_rule.window_days}d / reviewer=${String(kb.data.limits.outbreak_rule.needs_reviewer_approval)}`,
              }).map(([k, v]) => (
                <div key={k} className="rounded-md bg-surface-2 p-2">
                  <dt className="font-mono text-xs text-muted">{k}</dt>
                  <dd>{v}</dd>
                </div>
              ))}
            </dl>
            <p className="mt-3 font-mono text-xs text-muted">{kb.data.kb_version}</p>
          </Card>
        </>
      ) : null}
    </section>
  )
}
