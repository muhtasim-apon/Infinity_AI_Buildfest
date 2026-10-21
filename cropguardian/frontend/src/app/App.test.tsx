import { render, screen } from '@testing-library/react'
import { beforeAll, describe, expect, it } from 'vitest'
import { initI18n } from '../i18n'
import { App } from './App'

describe('App entry (anonymous visitor)', () => {
  beforeAll(() => {
    initI18n('bn')
  })

  it('renders the Bangla app name, the demo notice and the two ways in', async () => {
    render(<App />)
    expect(await screen.findByRole('heading', { level: 1 })).toHaveTextContent('ফসল রক্ষী')
    expect(screen.getByText(/ডেমো/, { selector: 'p' })).toBeInTheDocument()
    expect(screen.getAllByRole('link').length).toBeGreaterThanOrEqual(2)
  })

  it('has exactly one h1, a skip link and no script injection points', async () => {
    const { container } = render(<App />)
    await screen.findByRole('heading', { level: 1 })
    expect(container.querySelectorAll('h1')).toHaveLength(1)
    expect(container.querySelector('a[href="#main"]')).not.toBeNull()
    expect(container.innerHTML).not.toContain('<script')
  })
})
