import {
  type LucideIcon,
  ShieldAlert,
  ShieldCheck,
  ShieldX,
  SignalHigh,
  SignalLow,
  SignalMedium,
} from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { cn } from '../../lib/cn'
import { Badge, type BadgeTone } from './badge'

export type ConfidenceBand = 'high' | 'medium' | 'low'
export type RiskLevel = 'low' | 'medium' | 'high'

interface ChipConfig {
  key: string
  tone: BadgeTone
  icon: LucideIcon
}

function bandConfig(band: ConfidenceBand): ChipConfig {
  switch (band) {
    case 'high':
      return { key: 'result.band.high', tone: 'success', icon: SignalHigh }
    case 'medium':
      return { key: 'result.band.medium', tone: 'warning', icon: SignalMedium }
    default:
      return { key: 'ui.band.low', tone: 'danger', icon: SignalLow }
  }
}

function riskConfig(level: RiskLevel): ChipConfig {
  switch (level) {
    case 'low':
      return { key: 'ui.risk.low', tone: 'success', icon: ShieldCheck }
    case 'medium':
      return { key: 'ui.risk.medium', tone: 'warning', icon: ShieldAlert }
    default:
      return { key: 'ui.risk.high', tone: 'danger', icon: ShieldX }
  }
}

/**
 * Confidence band (spec 15.5.5: farmers see bands, never raw percentages). Icon + words, and the
 * words are the accessible name, so a screen reader hears "উচ্চ নিশ্চয়তা" rather than a colour.
 */
export function ConfidenceBandChip({
  band,
  className,
}: {
  band: ConfidenceBand
  className?: string
}) {
  const { t } = useTranslation()
  const { key, tone, icon: Icon } = bandConfig(band)
  return (
    <Badge tone={tone} className={cn('gap-2', className)} data-band={band}>
      <Icon className="h-4 w-4" aria-hidden="true" />
      {t(key)}
    </Badge>
  )
}

/** Outbreak risk chip for maps and alerts; level word is always present (never colour alone). */
export function RiskChip({ level, className }: { level: RiskLevel; className?: string }) {
  const { t } = useTranslation()
  const { key, tone, icon: Icon } = riskConfig(level)
  return (
    <Badge tone={tone} className={cn('gap-2', className)} data-risk={level}>
      <Icon className="h-4 w-4" aria-hidden="true" />
      {t(key)}
    </Badge>
  )
}
