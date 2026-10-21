import { render, screen } from '@testing-library/react'
import { beforeAll, describe, expect, it } from 'vitest'
import { initI18n } from '../i18n'
import { App } from './App'

describe('App placeholder', () => {
  beforeAll(() => {
    initI18n('bn')
  })

  it('renders the Bangla app name and the demo notice from i18n', () => {
    render(<App />)
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('ফসল রক্ষী')
    expect(screen.getByText(/ডেমো/)).toBeInTheDocument()
  })

  it('has exactly one h1 and no script injection points', () => {
    const { container } = render(<App />)
    expect(container.querySelectorAll('h1')).toHaveLength(1)
    expect(container.innerHTML).not.toContain('<script')
  })
})
