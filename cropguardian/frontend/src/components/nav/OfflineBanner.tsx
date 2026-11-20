import { WifiOff } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useOnline } from '../../lib/useOnline'
import { Reveal } from '../ui/reveal'

/**
 * Shown while the device has no network. Calm warning tone (amber, never red): photos are kept and
 * sent later, so being offline is a normal state, not an error (spec 15.2 "Offline outbox").
 */
export function OfflineBanner() {
  const { t } = useTranslation()
  const online = useOnline()
  if (online) return null
  return (
    <Reveal>
      <div
        role="status"
        className="flex items-center gap-2 border-b border-warning bg-warning-bg px-4 py-2 text-sm font-medium text-warning"
      >
        <WifiOff className="h-4 w-4 shrink-0" aria-hidden="true" />
        <span>{t('outbox.offline')}</span>
      </div>
    </Reveal>
  )
}
