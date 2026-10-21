import { QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import { MemoryRouter, useLocation } from 'react-router-dom'
import { AuthProvider } from '../src/app/auth'
import { makeQueryClient } from '../src/app/App'
import { AppRoutes } from '../src/app/router'
import bn from '../src/i18n/bn.json'
import { initI18n } from '../src/i18n'

/** Bangla text for a key, so assertions read like the screen does. */
export function bnText(key: string): string {
  let node: unknown = bn
  for (const part of key.split('.')) node = (node as Record<string, unknown>)[part]
  return String(node)
}

export function LocationProbe() {
  const loc = useLocation()
  return <span data-testid="location">{`${loc.pathname}${loc.search}`}</span>
}

export function renderApp(entry: string | { pathname: string; state?: unknown } = '/') {
  initI18n('bn')
  const client = makeQueryClient()
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[entry]}>
        <AuthProvider>
          <AppRoutes />
          <LocationProbe />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}
