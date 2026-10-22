import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Camera } from 'lucide-react'
import { axe } from 'vitest-axe'
import { describe, expect, it, vi } from 'vitest'
import { initI18n } from '../../i18n'
import { bnText } from '../../../tests/render'
import { Badge, SimulatedBadge } from './badge'
import { Button, IconButton } from './button'
import { Card, StatCard } from './card'
import { ConfidenceBandChip, RiskChip } from './chips'
import { CharacterCounter, FormField, Input, Textarea } from './input'
import { EmptyState, ErrorState, Skeleton, SkeletonGroup, SkeletonText } from './states'

function renderUi(ui: React.ReactElement) {
  initI18n('bn')
  return render(ui)
}

describe('Button', () => {
  it('defaults to type="button" so a button in a form never submits by accident', () => {
    renderUi(<Button>go</Button>)
    expect(screen.getByRole('button', { name: 'go' })).toHaveAttribute('type', 'button')
  })

  it('can be a real submit button when asked', () => {
    renderUi(<Button type="submit">send</Button>)
    expect(screen.getByRole('button')).toHaveAttribute('type', 'submit')
  })

  it('activates with click, Enter and Space', async () => {
    const onClick = vi.fn()
    const user = userEvent.setup()
    renderUi(<Button onClick={onClick}>go</Button>)
    await user.click(screen.getByRole('button'))
    screen.getByRole('button').focus()
    await user.keyboard('{Enter}')
    await user.keyboard(' ')
    expect(onClick).toHaveBeenCalledTimes(3)
  })

  it('does nothing when disabled', async () => {
    const onClick = vi.fn()
    renderUi(
      <Button disabled onClick={onClick}>
        go
      </Button>,
    )
    await userEvent.setup().click(screen.getByRole('button'))
    expect(onClick).not.toHaveBeenCalled()
  })

  it('loading disables the button, announces busy and keeps the label (width locked)', async () => {
    const onClick = vi.fn()
    renderUi(
      <Button loading onClick={onClick}>
        save
      </Button>,
    )
    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
    expect(button).toHaveAttribute('aria-busy', 'true')
    expect(button).toHaveTextContent('save') // label still in the DOM (invisible) so width does not jump
    await userEvent.setup().click(button)
    expect(onClick).not.toHaveBeenCalled()
  })

  it('asChild styles a link as a button without nesting a <button>', () => {
    renderUi(
      <Button asChild>
        <a href="/demo">demo</a>
      </Button>,
    )
    expect(screen.getByRole('link', { name: 'demo' }).className).toContain('bg-primary')
    expect(screen.queryByRole('button')).toBeNull()
  })

  it('keeps the touch-target sizes: >= 44 everywhere, 48 default, 56 farmer primary', () => {
    renderUi(
      <>
        <Button size="sm">sm</Button>
        <Button>md</Button>
        <Button size="xl-farmer">xl</Button>
      </>,
    )
    expect(screen.getByText('sm').closest('button')?.className).toContain('min-h-[44px]')
    expect(screen.getByText('md').closest('button')?.className).toContain('min-h-[48px]')
    expect(screen.getByText('xl').closest('button')?.className).toContain('min-h-[56px]')
  })

  it('an icon button has its accessible name', () => {
    renderUi(
      <IconButton aria-label="ছবি তুলুন">
        <Camera aria-hidden="true" />
      </IconButton>,
    )
    expect(screen.getByRole('button', { name: 'ছবি তুলুন' })).toBeInTheDocument()
  })

  it('refuses an icon-only button without an aria-label at compile time', () => {
    // @ts-expect-error aria-label is mandatory on IconButton (spec 15.3)
    const bad = <IconButton>x</IconButton>
    expect(bad).toBeTruthy()
  })
})

describe('FormField / Input / Textarea', () => {
  it('connects label, hint and error to the control', () => {
    renderUi(
      <FormField label="ফোন" hint="০১৭ দিয়ে শুরু" error="নম্বরটি ঠিক নয়">
        {(p) => <Input {...p} />}
      </FormField>,
    )
    const input = screen.getByLabelText('ফোন', { exact: false })
    expect(input).toHaveAttribute('aria-invalid', 'true')
    const described = input.getAttribute('aria-describedby') ?? ''
    expect(described.split(' ')).toHaveLength(2)
    expect(screen.getByRole('alert')).toHaveTextContent('নম্বরটি ঠিক নয়')
    expect(document.getElementById(described.split(' ')[0] ?? '')).toHaveTextContent(
      '০১৭ দিয়ে শুরু',
    )
  })

  it('has no aria-invalid / describedby when there is nothing to say', () => {
    renderUi(<FormField label="নাম">{(p) => <Input {...p} />}</FormField>)
    const input = screen.getByLabelText('নাম')
    expect(input).not.toHaveAttribute('aria-invalid')
    expect(input).not.toHaveAttribute('aria-describedby')
    expect(screen.queryByRole('alert')).toBeNull()
  })

  it('marks required fields visually and for screen readers', () => {
    renderUi(
      <FormField label="নাম" required>
        {(p) => <Input {...p} />}
      </FormField>,
    )
    expect(screen.getByLabelText(/নাম/)).toHaveAttribute('aria-required', 'true')
    expect(screen.getByText(bnText('ui.required'))).toBeInTheDocument()
  })

  it('accepts typing, including Bangla text', async () => {
    renderUi(<Input aria-label="n" />)
    await userEvent.setup().type(screen.getByLabelText('n'), 'রহিমা')
    expect(screen.getByLabelText('n')).toHaveValue('রহিমা')
  })

  it('the counter uses locale digits and turns red when over the limit', () => {
    const { rerender } = renderUi(<CharacterCounter count={12} max={280} locale="bn" />)
    expect(screen.getByText('১২ / ২৮০')).toBeInTheDocument()
    rerender(<CharacterCounter count={300} max={280} locale="en" />)
    expect(screen.getByText('300 / 280').className).toContain('text-danger')
  })

  it('textarea is invalid-aware and tall enough to write in', () => {
    renderUi(<Textarea aria-label="t" invalid />)
    expect(screen.getByLabelText('t')).toHaveAttribute('aria-invalid', 'true')
    expect(screen.getByLabelText('t').className).toContain('min-h-[96px]')
  })
})

describe('Badge and SimulatedBadge', () => {
  it.each(['neutral', 'success', 'warning', 'danger', 'info', 'simulated'] as const)(
    '%s badge always has an icon AND text (never colour alone)',
    (tone) => {
      renderUi(<Badge tone={tone}>স্থিতি</Badge>)
      const badge = screen.getByText('স্থিতি').closest('span[class*="rounded-full"]')
      expect(badge?.querySelector('svg[aria-hidden="true"]')).not.toBeNull()
      expect(badge).toHaveTextContent('স্থিতি')
    },
  )

  it('SimulatedBadge says SIMULATED in the locale and is machine-detectable', () => {
    renderUi(<SimulatedBadge />)
    const badge = screen.getByText(bnText('demo.simulated'))
    expect(badge.closest('[data-simulated]')).not.toBeNull()
  })
})

describe('chips', () => {
  it('confidence chips show words, never a percentage', () => {
    renderUi(
      <>
        <ConfidenceBandChip band="high" />
        <ConfidenceBandChip band="medium" />
        <ConfidenceBandChip band="low" />
      </>,
    )
    expect(screen.getByText(bnText('result.band.high'))).toBeInTheDocument()
    expect(screen.getByText(bnText('result.band.medium'))).toBeInTheDocument()
    expect(screen.getByText(bnText('ui.band.low'))).toBeInTheDocument()
    expect(document.body.textContent).not.toMatch(/%|শতাংশ/)
  })

  it('risk chips carry the level word and an icon', () => {
    renderUi(
      <>
        <RiskChip level="low" />
        <RiskChip level="medium" />
        <RiskChip level="high" />
      </>,
    )
    for (const level of ['low', 'medium', 'high']) {
      const chip = screen.getByText(bnText(`ui.risk.${level}`)).closest('[data-risk]')
      expect(chip).toHaveAttribute('data-risk', level)
      expect(chip?.querySelector('svg[aria-hidden="true"]')).not.toBeNull()
    }
  })
})

describe('Card / StatCard', () => {
  it('renders a card and an interactive card with lift classes', () => {
    renderUi(
      <>
        <Card data-testid="plain">a</Card>
        <Card data-testid="live" interactive>
          b
        </Card>
      </>,
    )
    expect(screen.getByTestId('plain').className).not.toContain('hover:shadow-md')
    expect(screen.getByTestId('live').className).toContain('hover:shadow-md')
  })

  it('shows value, positive delta, and a sparkline that is hidden from assistive tech', () => {
    const { container } = renderUi(
      <StatCard label="আজকের ছবি" value="১২" delta="+৩" trend={[1, 4, 2, 6]} />,
    )
    expect(screen.getByText('আজকের ছবি')).toBeInTheDocument()
    expect(screen.getByText('+৩').className).toContain('text-success')
    expect(container.querySelector('svg[aria-hidden="true"] polyline')).not.toBeNull()
  })

  it('a negative delta is red with its own sign (ASCII hyphen or Unicode minus)', () => {
    renderUi(
      <>
        <StatCard label="a" value="1" delta="-2" />
        <StatCard label="b" value="1" delta="−2" />
      </>,
    )
    expect(screen.getByText('-2').className).toContain('text-danger')
    expect(screen.getByText('−2').className).toContain('text-danger')
  })

  it('ignores a sparkline with NaN or fewer than two points instead of drawing garbage', () => {
    const { container } = renderUi(
      <>
        <StatCard label="a" value="1" trend={[1, Number.NaN, 3]} />
        <StatCard label="b" value="1" trend={[5]} />
      </>,
    )
    expect(container.querySelector('polyline')).toBeNull()
  })

  it('can show "not yet measured" instead of a number', () => {
    renderUi(<StatCard label="নির্ভুলতা" value="—" note="এখনও পরিমাপ হয়নি" />)
    expect(screen.getByText('এখনও পরিমাপ হয়নি')).toBeInTheDocument()
  })
})

describe('skeleton, empty and error states', () => {
  it('Skeleton shapes are hidden from assistive tech; the group announces loading once', () => {
    renderUi(
      <SkeletonGroup>
        <Skeleton className="h-4" data-testid="s" />
      </SkeletonGroup>,
    )
    expect(screen.getByTestId('s')).toHaveAttribute('aria-hidden', 'true')
    const status = screen.getByRole('status')
    expect(status).toHaveAttribute('aria-busy', 'true')
    expect(status).toHaveTextContent(bnText('common.loading'))
  })

  it('SkeletonText clamps nonsense line counts', () => {
    const { container, rerender } = renderUi(<SkeletonText lines={0} />)
    expect(container.querySelectorAll('[aria-hidden="true"]')).toHaveLength(3)
    rerender(<SkeletonText lines={500} />)
    expect(container.querySelectorAll('[aria-hidden="true"]')).toHaveLength(12)
    rerender(<SkeletonText lines={Number.NaN} />)
    expect(container.querySelectorAll('[aria-hidden="true"]')).toHaveLength(3)
  })

  it('EmptyState shows title, one line and an action', async () => {
    const onClick = vi.fn()
    renderUi(
      <EmptyState
        title="কোনো ছবি নেই"
        description="প্রথম ছবি তুলুন"
        action={<Button onClick={onClick}>ছবি তুলুন</Button>}
      />,
    )
    expect(screen.getByText('কোনো ছবি নেই')).toBeInTheDocument()
    await userEvent.setup().click(screen.getByRole('button', { name: 'ছবি তুলুন' }))
    expect(onClick).toHaveBeenCalled()
  })

  it('ErrorState announces itself, shows the request id and offers a retry', async () => {
    const onRetry = vi.fn()
    renderUi(<ErrorState message="আবার চেষ্টা করুন" requestId="abc123" onRetry={onRetry} />)
    expect(screen.getByRole('alert')).toHaveTextContent(bnText('errors.generic'))
    expect(screen.getByText(/abc123/)).toBeInTheDocument()
    await userEvent.setup().click(screen.getByRole('button', { name: bnText('common.retry') }))
    expect(onRetry).toHaveBeenCalledTimes(1)
  })

  it('ErrorState without a handler or id has no dead retry button', () => {
    renderUi(<ErrorState title="কিছু ভুল" />)
    expect(screen.queryByRole('button')).toBeNull()
    expect(screen.queryByText(/abc/)).toBeNull()
  })
})

describe('accessibility', () => {
  it('all core primitives together have no axe violations', async () => {
    const { container } = renderUi(
      <main>
        <h1>শিরোনাম</h1>
        <Button>বোতাম</Button>
        <FormField label="নাম" hint="সংক্ষেপে" required>
          {(p) => <Input {...p} />}
        </FormField>
        <Badge tone="success">ঠিক আছে</Badge>
        <SimulatedBadge />
        <ConfidenceBandChip band="high" />
        <RiskChip level="medium" />
        <StatCard label="ছবি" value="১২" delta="+৩" trend={[1, 2, 3]} />
        <EmptyState title="খালি" />
        <ErrorState onRetry={() => undefined} />
        <SkeletonGroup>
          <SkeletonText />
        </SkeletonGroup>
      </main>,
    )
    expect(await axe(container)).toHaveNoViolations()
  })
})
