import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

export function ForbiddenPage() {
  const { t } = useTranslation()
  return (
    <section>
      <h1 className="text-2xl font-semibold">{t('errors.forbiddenTitle')}</h1>
      <p className="mt-2 text-muted">{t('errors.forbidden')}</p>
      <Link to="/" className="mt-6 inline-flex min-h-[48px] items-center text-primary underline">
        {t('errors.goHome')}
      </Link>
    </section>
  )
}

export function NotFoundPage() {
  const { t } = useTranslation()
  return (
    <section>
      <h1 className="text-2xl font-semibold">{t('errors.notFoundTitle')}</h1>
      <p className="mt-2 text-muted">{t('errors.notFound')}</p>
      <Link to="/" className="mt-6 inline-flex min-h-[48px] items-center text-primary underline">
        {t('errors.goHome')}
      </Link>
    </section>
  )
}
