import { useTranslation } from 'react-i18next'
import { useAuth } from '../auth'

/** Admin area: a separate chunk, so non-admins never download it (spec 15.4). Console: Phase 10. */
export default function AdminHome() {
  const { t } = useTranslation()
  const { state } = useAuth()
  return (
    <section>
      <h1 className="text-2xl font-semibold">{t('home.admin')}</h1>
      <p className="mt-2">{t('home.welcome', { name: state?.display_name ?? '' })}</p>
      <p className="mt-4 rounded-lg border border-border bg-surface p-4 text-muted">
        {t('home.placeholder')}
      </p>
    </section>
  )
}
