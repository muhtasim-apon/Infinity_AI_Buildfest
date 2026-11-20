import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Bar, BarChart, CartesianGrid, Legend, Tooltip, XAxis, YAxis } from 'recharts'
import { Card, CardTitle } from '../../components/ui/card'
import { SkeletonCard } from '../../components/ui/states'
import { useScanStats } from '../../features/scans/api'
import { formatNumber } from '../../lib/format'
import { isLocale } from '../../i18n'

/**
 * Reviewer chart: scans per division by outcome (last 30 days). Token colours only, status never by
 * colour alone (legend + table), and a "view as table" alternative for screen readers (spec 15.3).
 * Fixed width keeps it CSP-safe and avoids ResizeObserver layout work on low-end devices.
 */
export function ScanStatsChart() {
  const { t, i18n } = useTranslation()
  const locale = isLocale(i18n.language) ? i18n.language : 'bn'
  const stats = useScanStats()
  const [table, setTable] = useState(false)

  if (stats.isPending) return <SkeletonCard />
  if (stats.isError || !stats.data) return null
  const rows = stats.data.divisions.map((d) => ({
    name: locale === 'bn' ? d.region_bn : d.region_en,
    diagnosed: d.diagnosed,
    notSure: d.not_sure,
    healthy: d.healthy,
  }))
  const total = rows.reduce((n, r) => n + r.diagnosed + r.notSure + r.healthy, 0)

  return (
    <Card>
      <div className="flex items-start justify-between gap-2">
        <div>
          <CardTitle>{t('cg.stats.chartTitle')}</CardTitle>
          <p className="mt-1 text-sm text-muted">{t('cg.stats.chartHint')}</p>
        </div>
        <button
          type="button"
          className="min-h-[44px] rounded-md border border-border px-3 text-sm"
          aria-pressed={table}
          onClick={() => setTable((v) => !v)}
        >
          {t('cg.stats.viewTable')}
        </button>
      </div>
      {total === 0 ? <p className="mt-3 text-muted">{t('cg.stats.noData')}</p> : null}
      {total > 0 && !table ? (
        <div className="mt-3 overflow-x-auto" aria-hidden="true">
          <BarChart
            width={440}
            height={260}
            data={rows}
            margin={{ top: 8, right: 8, bottom: 40, left: -16 }}
          >
            <CartesianGrid stroke="var(--border)" vertical={false} />
            <XAxis
              dataKey="name"
              tick={{ fontSize: 12, fill: 'var(--text-muted)' }}
              angle={-35}
              textAnchor="end"
              interval={0}
            />
            <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: 'var(--text-muted)' }} />
            <Tooltip />
            <Legend verticalAlign="top" height={28} />
            <Bar
              dataKey="diagnosed"
              name={t('cg.stats.diagnosed')}
              stackId="s"
              fill="var(--primary)"
            />
            <Bar dataKey="notSure" name={t('cg.stats.notSure')} stackId="s" fill="var(--sky)" />
            <Bar dataKey="healthy" name={t('cg.stats.healthy')} stackId="s" fill="var(--accent)" />
          </BarChart>
        </div>
      ) : null}
      {total > 0 ? (
        <table className={table ? 'mt-3 w-full text-sm' : 'sr-only'}>
          <thead>
            <tr className="text-left text-muted">
              <th className="py-1">{t('cg.stats.division')}</th>
              <th className="py-1 text-right">{t('cg.stats.diagnosed')}</th>
              <th className="py-1 text-right">{t('cg.stats.notSure')}</th>
              <th className="py-1 text-right">{t('cg.stats.healthy')}</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.name} className="border-t border-border">
                <td className="py-1">{r.name}</td>
                <td className="py-1 text-right tabular-nums">
                  {formatNumber(r.diagnosed, locale)}
                </td>
                <td className="py-1 text-right tabular-nums">{formatNumber(r.notSure, locale)}</td>
                <td className="py-1 text-right tabular-nums">{formatNumber(r.healthy, locale)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
    </Card>
  )
}
