import './lib/zodConfig' // first: keeps Zod from probing eval under the strict CSP (D-027)
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { App } from './app/App'
import { DEFAULT_LOCALE, initI18n, setDocumentLocale } from './i18n'
import './styles/index.css'

initI18n(DEFAULT_LOCALE)
setDocumentLocale(DEFAULT_LOCALE)

const root = document.getElementById('root')
if (!root) throw new Error('#root element missing')
createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
