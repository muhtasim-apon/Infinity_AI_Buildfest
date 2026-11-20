import { CircleCheck, CircleX, Inbox } from 'lucide-react'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Badge, SimulatedBadge } from '../../components/ui/badge'
import { Button } from '../../components/ui/button'
import { ConfirmDialog } from '../../components/ui/modal'
import { EmptyState, SkeletonCard } from '../../components/ui/states'
import { useAlerts, useDecideAlert, type OutbreakAlert } from '../../features/scans/api'
import { formatDate } from '../../lib/format'
import { isLocale } from '../../i18n'
import { useAuth } from '../auth'
import { FormError } from '../ui'
import { AlertCard } from './farmer'
import { ScanStatsChart } from './ScanStatsChart'

/**
 * Reviewer console, outbreak drafts (Gantt P3 step 4). Nothing reaches farmers until a human
 * approves; every decision is confirmed in a native dialog and written to the audit log server-side.
 * Real reviewers need a fresh step-up 2FA (the API answers step_up_required otherwise).
 */
export function ReviewerAlertsPage() {
  const { t, i18n } = useTranslation()
  const locale = isLocale(i18n.language) ? i18n.language : 'bn'
  const { state } = useAuth()
  const alerts = useAlerts()
  const decide = useDecideAlert()
  const [pending, setPending] = useState<{ alert: OutbreakAlert; approve: boolean } | null>(null)
  const [done, setDone] = useState(false)

  const drafts = alerts.data?.filter((a) => a.status === 'draft') ?? []
  const decided = alerts.data?.filter((a) => a.status !== 'draft') ?? []

  const confirm = async () => {
    if (!pending) return
    setDone(false)
    try {
      await decide.mutateAsync({
        id: pending.alert.id,
        decision: pending.approve ? 'approve' : 'reject',
      })
      setDone(true)
    } finally {
      setPending(null)
    }
  }

  return (
    <section className="space-y-4">
      <div className="flex items-start justify-between gap-2">
        <h1 className="text-2xl font-semibold">{t('cg.review.title')}</h1>
        {state?.role?.startsWith('DEMO_') ? <SimulatedBadge /> : null}
      </div>
      <p className="text-muted">{t('cg.review.intro')}</p>
      <ScanStatsChart />
      {done ? (
        <p
          role="status"
          className="rounded-md border border-success bg-success-bg p-3 text-success"
        >
          {t('cg.review.done')}
        </p>
      ) : null}
      <FormError error={decide.error} />

      <h2 className="text-lg font-semibold">{t('cg.review.drafts')}</h2>
      {alerts.isPending ? <SkeletonCard /> : null}
      {alerts.isError ? <FormError error={alerts.error} /> : null}
      {alerts.data && drafts.length === 0 ? (
        <EmptyState
          icon={Inbox}
          title={t('cg.review.empty')}
          description={t('cg.review.emptyHint')}
        />
      ) : null}
      <div className="space-y-3">
        {drafts.map((a) => (
          <AlertCard key={a.id} alert={a}>
            <p className="mt-2 text-sm text-muted">
              {t('cg.review.window', {
                from: formatDate(a.window_start, locale),
                to: formatDate(a.window_end, locale),
              })}
            </p>
            <div className="mt-3 grid grid-cols-2 gap-2">
              <Button onClick={() => setPending({ alert: a, approve: true })}>
                <CircleCheck className="h-5 w-5" aria-hidden="true" />
                {t('cg.review.approve')}
              </Button>
              <Button variant="outline" onClick={() => setPending({ alert: a, approve: false })}>
                <CircleX className="h-5 w-5" aria-hidden="true" />
                {t('cg.review.reject')}
              </Button>
            </div>
          </AlertCard>
        ))}
      </div>

      {decided.length > 0 ? (
        <>
          <h2 className="text-lg font-semibold">{t('cg.review.decided')}</h2>
          <ul className="space-y-2">
            {decided.map((a) => (
              <li
                key={a.id}
                className="flex items-center justify-between gap-2 rounded-lg border border-border bg-surface p-3"
              >
                <span>
                  {(locale === 'bn' ? a.disease_bn : a.disease_en) ?? a.disease}
                  <span aria-hidden="true">{' · '}</span>
                  {locale === 'bn' ? a.region_bn : a.region_en}
                </span>
                <Badge tone={a.status === 'approved' ? 'success' : 'neutral'}>
                  {t(`cg.review.status.${a.status}`)}
                </Badge>
              </li>
            ))}
          </ul>
        </>
      ) : null}

      <ConfirmDialog
        open={pending !== null}
        onOpenChange={(open) => {
          if (!open) setPending(null)
        }}
        title={pending?.approve ? t('cg.review.approveTitle') : t('cg.review.rejectTitle')}
        description={pending?.approve ? t('cg.review.approveBody') : t('cg.review.rejectBody')}
        confirmLabel={pending?.approve ? t('cg.review.approve') : t('cg.review.reject')}
        destructive={!pending?.approve}
        loading={decide.isPending}
        onConfirm={() => void confirm()}
      />
    </section>
  )
}
