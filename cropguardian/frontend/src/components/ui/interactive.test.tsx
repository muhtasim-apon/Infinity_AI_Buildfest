import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Camera } from 'lucide-react'
import { useState } from 'react'
import { axe } from 'vitest-axe'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { TOAST_DISMISS_MS } from '../../design/motion'
import { initI18n } from '../../i18n'
import { bnText } from '../../../tests/render'
import { Button } from './button'
import { CheckboxField, NativeSelect, RadioCards, SliderField, SwitchField } from './controls'
import { FormField } from './input'
import { ConfirmDialog, Modal, Sheet, matchesRequiredText } from './modal'
import { DropdownMenu, Popover, Tooltip } from './overlays'
import { Meter, Progress, Ring, Stepper } from './progress'
import { SegmentedControl, Tabs, TabsContent, TabsList, TabsTrigger } from './tabs'
import { Toaster, toast } from './toast'

function renderUi(ui: React.ReactElement) {
  initI18n('bn')
  return render(ui)
}

afterEach(() => {
  toast.clear()
  vi.useRealTimers()
})

describe('Toaster', () => {
  it('shows a toast with title and description in a polite region', async () => {
    renderUi(<Toaster />)
    act(() => {
      toast.show({ title: 'সংরক্ষিত', description: 'ছবি পাঠানো হয়েছে', tone: 'success' })
    })
    expect(await screen.findByText('সংরক্ষিত')).toBeInTheDocument()
    expect(screen.getByText('ছবি পাঠানো হয়েছে')).toBeInTheDocument()
    // Radix labels the landmark "<label> (F8)" and announces each toast through a polite live region
    const region = document.querySelector('[role="region"]')
    expect(region?.getAttribute('aria-label')).toContain(bnText('ui.notifications'))
    expect(document.querySelector('[aria-live="polite"]')).not.toBeNull()
  })

  it('keeps at most three on screen (a burst of errors cannot bury the page)', async () => {
    renderUi(<Toaster />)
    act(() => {
      for (const n of [1, 2, 3, 4, 5]) toast.show({ title: `বার্তা ${n}`, tone: 'error' })
    })
    expect(await screen.findByText('বার্তা 5')).toBeInTheDocument()
    expect(screen.queryByText('বার্তা 1')).toBeNull()
    expect(screen.queryByText('বার্তা 2')).toBeNull()
    expect(screen.getAllByText(/বার্তা/)).toHaveLength(3)
  })

  it('can be dismissed with its close button (named, >= 44 px target)', async () => {
    renderUi(<Toaster />)
    act(() => {
      toast.show({ title: 'বন্ধ হবে' })
    })
    await userEvent
      .setup()
      .click(await screen.findByRole('button', { name: bnText('common.close') }))
    await waitFor(() => expect(screen.queryByText('বন্ধ হবে')).toBeNull())
  })

  it('auto-dismisses after the 5 second token', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true })
    renderUi(<Toaster />)
    act(() => {
      toast.show({ title: 'চলে যাবে' })
    })
    expect(await screen.findByText('চলে যাবে')).toBeInTheDocument()
    await act(async () => {
      await vi.advanceTimersByTimeAsync(TOAST_DISMISS_MS + 200)
    })
    await waitFor(() => expect(screen.queryByText('চলে যাবে')).toBeNull())
  })

  it('exposes the drain duration from the motion token to CSS', async () => {
    renderUi(<Toaster />)
    act(() => {
      toast.show({ title: 'বার' })
    })
    await screen.findByText('বার')
    const bar = document.querySelector<HTMLElement>('[data-toast-progress]')
    expect(bar?.style.getPropertyValue('--toast-duration')).toBe(`${TOAST_DISMISS_MS}ms`)
  })
})

function ModalHarness(props: { dismissible?: boolean }) {
  const [open, setOpen] = useState(false)
  return (
    <>
      <Button onClick={() => setOpen(true)}>খুলুন</Button>
      <Modal open={open} onOpenChange={setOpen} title="শিরোনাম" description="বিবরণ" {...props}>
        <button type="button">ভিতরে</button>
      </Modal>
      <output data-testid="state">{String(open)}</output>
    </>
  )
}

describe('Modal (native <dialog>)', () => {
  it('opens as a modal dialog named by its title and described by its description', async () => {
    renderUi(<ModalHarness />)
    await userEvent.setup().click(screen.getByRole('button', { name: 'খুলুন' }))
    const dialog = screen.getByRole('dialog', { name: 'শিরোনাম' })
    expect(dialog).toHaveAttribute('open')
    expect(dialog).toHaveAccessibleDescription('বিবরণ')
    expect(within(dialog).getByRole('button', { name: 'ভিতরে' })).toBeInTheDocument()
  })

  it('renders its content only while open (nothing hidden is focusable)', () => {
    renderUi(<ModalHarness />)
    expect(screen.queryByText('ভিতরে')).toBeNull()
  })

  it('closes with the close button and reports it', async () => {
    const user = userEvent.setup()
    renderUi(<ModalHarness />)
    await user.click(screen.getByRole('button', { name: 'খুলুন' }))
    await user.click(screen.getByRole('button', { name: bnText('common.close') }))
    expect(screen.getByTestId('state')).toHaveTextContent('false')
    expect(document.querySelector('dialog')).not.toHaveAttribute('open')
  })

  it('syncs state when the browser closes it itself (Escape fires "close")', async () => {
    renderUi(<ModalHarness />)
    await userEvent.setup().click(screen.getByRole('button', { name: 'খুলুন' }))
    act(() => {
      document.querySelector('dialog')?.close()
    })
    expect(screen.getByTestId('state')).toHaveTextContent('false')
  })

  it('closes on a press on the backdrop but not on a press inside the panel', async () => {
    renderUi(<ModalHarness />)
    await userEvent.setup().click(screen.getByRole('button', { name: 'খুলুন' }))
    const dialog = document.querySelector('dialog') as HTMLDialogElement
    fireEvent.mouseDown(screen.getByText('শিরোনাম'))
    expect(screen.getByTestId('state')).toHaveTextContent('true')
    fireEvent.mouseDown(dialog)
    expect(screen.getByTestId('state')).toHaveTextContent('false')
  })

  it('non-dismissible: no X, backdrop ignored, Escape (cancel) is prevented', async () => {
    renderUi(<ModalHarness dismissible={false} />)
    await userEvent.setup().click(screen.getByRole('button', { name: 'খুলুন' }))
    const dialog = document.querySelector('dialog') as HTMLDialogElement
    expect(screen.queryByRole('button', { name: bnText('common.close') })).toBeNull()
    fireEvent.mouseDown(dialog)
    expect(screen.getByTestId('state')).toHaveTextContent('true')
    const cancel = new Event('cancel', { cancelable: true })
    dialog.dispatchEvent(cancel)
    expect(cancel.defaultPrevented).toBe(true)
  })

  it('dismissible dialogs let Escape through', async () => {
    renderUi(<ModalHarness />)
    await userEvent.setup().click(screen.getByRole('button', { name: 'খুলুন' }))
    const cancel = new Event('cancel', { cancelable: true })
    document.querySelector('dialog')?.dispatchEvent(cancel)
    expect(cancel.defaultPrevented).toBe(false)
  })

  it('still opens (non-modally) when showModal does not exist, e.g. very old browsers (CC-38)', async () => {
    const original = HTMLDialogElement.prototype.showModal
    // @ts-expect-error simulate a browser without <dialog>.showModal
    HTMLDialogElement.prototype.showModal = undefined
    try {
      renderUi(<ModalHarness />)
      await userEvent.setup().click(screen.getByRole('button', { name: 'খুলুন' }))
      expect(document.querySelector('dialog')).toHaveAttribute('open')
      expect(screen.getByText('ভিতরে')).toBeInTheDocument()
    } finally {
      HTMLDialogElement.prototype.showModal = original
    }
  })

  it('a bottom sheet and a side sheet use their placements', () => {
    renderUi(
      <>
        <Sheet open onOpenChange={() => undefined} title="নিচের" />
        <Sheet open onOpenChange={() => undefined} title="পাশের" side="side" />
      </>,
    )
    const dialogs = document.querySelectorAll('dialog')
    expect(dialogs[0]?.className).toContain('mt-auto')
    expect(dialogs[1]?.className).toContain('h-full')
  })
})

describe('ConfirmDialog', () => {
  function Harness({ requireText, onConfirm }: { requireText?: string; onConfirm: () => void }) {
    const [open, setOpen] = useState(true)
    return (
      <>
        <button type="button" onClick={() => setOpen(true)}>
          আবার খুলুন
        </button>
        <ConfirmDialog
          open={open}
          onOpenChange={setOpen}
          title="মুছবেন?"
          description="এটি ফেরানো যাবে না"
          requireText={requireText}
          onConfirm={onConfirm}
        />
      </>
    )
  }

  it('is an alertdialog and starts focus on Cancel (the safe choice)', () => {
    renderUi(<Harness onConfirm={() => undefined} />)
    expect(screen.getByRole('alertdialog', { name: 'মুছবেন?' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: bnText('common.cancel') })).toHaveFocus()
  })

  it('confirm is destructive and calls back once', async () => {
    const onConfirm = vi.fn()
    renderUi(<Harness onConfirm={onConfirm} />)
    const confirm = screen.getByRole('button', { name: bnText('ui.confirm.confirm') })
    expect(confirm.className).toContain('bg-danger')
    await userEvent.setup().click(confirm)
    expect(onConfirm).toHaveBeenCalledTimes(1)
  })

  it('typed confirmation: disabled until the exact text is typed', async () => {
    const onConfirm = vi.fn()
    const user = userEvent.setup()
    renderUi(<Harness requireText="মুছে ফেলুন" onConfirm={onConfirm} />)
    const confirm = screen.getByRole('button', { name: bnText('ui.confirm.confirm') })
    expect(confirm).toBeDisabled()
    const field = screen.getByLabelText(/মুছে ফেলুন/)
    await user.type(field, 'মুছে ফেল')
    expect(confirm).toBeDisabled()
    await user.type(field, 'ুন')
    expect(confirm).toBeEnabled()
    await user.click(confirm)
    expect(onConfirm).toHaveBeenCalledTimes(1)
  })

  it('typed text is cleared when the dialog is reopened', async () => {
    const user = userEvent.setup()
    renderUi(<Harness requireText="DELETE" onConfirm={() => undefined} />)
    await user.type(screen.getByLabelText(/DELETE/), 'DELETE')
    await user.click(screen.getByRole('button', { name: bnText('common.cancel') }))
    await user.click(screen.getByRole('button', { name: 'আবার খুলুন' }))
    expect(screen.getByLabelText(/DELETE/)).toHaveValue('')
  })

  it('matches after Unicode normalisation and trimming, never loosely', () => {
    expect(matchesRequiredText('  DELETE ', 'DELETE')).toBe(true)
    expect(matchesRequiredText('Café', 'Café')).toBe(true) // composed vs decomposed
    expect(matchesRequiredText('delete', 'DELETE')).toBe(false)
    expect(matchesRequiredText('', 'DELETE')).toBe(false)
    expect(matchesRequiredText('DELETE now', 'DELETE')).toBe(false)
  })

  it('loading locks the dialog: cancel disabled, not dismissible', () => {
    renderUi(
      <ConfirmDialog
        open
        onOpenChange={() => undefined}
        title="t"
        onConfirm={() => undefined}
        loading
      />,
    )
    expect(screen.getByRole('button', { name: bnText('common.cancel') })).toBeDisabled()
    expect(screen.queryByRole('button', { name: bnText('common.close') })).toBeNull()
  })
})

describe('Tabs and SegmentedControl', () => {
  it('switches panels by click and by arrow keys, with one sliding indicator', async () => {
    const user = userEvent.setup()
    renderUi(
      <Tabs defaultValue="a">
        <TabsList aria-label="ট্যাব">
          <TabsTrigger value="a">এক</TabsTrigger>
          <TabsTrigger value="b">দুই</TabsTrigger>
        </TabsList>
        <TabsContent value="a">প্রথম</TabsContent>
        <TabsContent value="b">দ্বিতীয়</TabsContent>
      </Tabs>,
    )
    expect(screen.getByText('প্রথম')).toBeVisible()
    expect(document.querySelectorAll('[aria-hidden="true"].bg-primary')).toHaveLength(1)
    await user.click(screen.getByRole('tab', { name: 'দুই' }))
    expect(screen.getByText('দ্বিতীয়')).toBeVisible()
    screen.getByRole('tab', { name: 'দুই' }).focus()
    await user.keyboard('{ArrowLeft}')
    expect(screen.getByRole('tab', { name: 'এক' })).toHaveAttribute('aria-selected', 'true')
    expect(document.querySelectorAll('[aria-hidden="true"].bg-primary')).toHaveLength(1)
  })

  it('SegmentedControl is a named radio group that reports changes', async () => {
    const onValueChange = vi.fn()
    renderUi(
      <SegmentedControl
        aria-label="কার জন্য"
        value="farmers"
        onValueChange={onValueChange}
        options={[
          { value: 'farmers', label: 'কৃষক' },
          { value: 'ngo', label: 'এনজিও' },
        ]}
      />,
    )
    expect(screen.getByRole('radiogroup', { name: 'কার জন্য' })).toBeInTheDocument()
    expect(screen.getByRole('radio', { name: 'কৃষক' })).toBeChecked()
    await userEvent.setup().click(screen.getByRole('radio', { name: 'এনজিও' }))
    expect(onValueChange).toHaveBeenCalledWith('ngo')
  })
})

describe('form controls', () => {
  it('SwitchField is labelled, toggles with click and Space, and is disabled-aware', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    renderUi(
      <SwitchField
        label="বিজ্ঞপ্তি"
        description="আপনার এলাকার সতর্কতা"
        checked={false}
        onCheckedChange={onChange}
      />,
    )
    const sw = screen.getByRole('switch', { name: /বিজ্ঞপ্তি/ })
    expect(sw).toHaveAccessibleDescription('আপনার এলাকার সতর্কতা')
    await user.click(sw)
    sw.focus()
    await user.keyboard(' ')
    expect(onChange).toHaveBeenCalledTimes(2)
    expect(onChange).toHaveBeenLastCalledWith(true)
  })

  it('SwitchField disabled does not fire', async () => {
    const onChange = vi.fn()
    renderUi(<SwitchField label="x" checked={false} onCheckedChange={onChange} disabled />)
    await userEvent.setup().click(screen.getByRole('switch'))
    expect(onChange).not.toHaveBeenCalled()
  })

  it('CheckboxField reports a real boolean', async () => {
    const onChange = vi.fn()
    renderUi(<CheckboxField label="সম্মতি" checked={false} onCheckedChange={onChange} />)
    await userEvent.setup().click(screen.getByRole('checkbox', { name: /সম্মতি/ }))
    expect(onChange).toHaveBeenCalledWith(true)
  })

  it('RadioCards select with the arrow keys and show icon + text', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    renderUi(
      <RadioCards
        aria-label="ভূমিকা"
        value="farmer"
        onValueChange={onChange}
        options={[
          { value: 'farmer', label: 'কৃষক', description: 'ছবি তুলুন', icon: Camera },
          { value: 'reviewer', label: 'পর্যালোচক' },
        ]}
      />,
    )
    const farmer = screen.getByRole('radio', { name: /কৃষক/ })
    expect(farmer.querySelector('svg[aria-hidden="true"]')).not.toBeNull()
    farmer.focus()
    // hold the key like a finger does: Radix moves roving focus on a timer and only selects the
    // focused card while an arrow key is still down (user-event would release it instantly)
    await user.keyboard('{ArrowDown>}')
    await waitFor(() => expect(onChange).toHaveBeenCalledWith('reviewer'))
    await user.keyboard('{/ArrowDown}')
  })

  it('SliderField shows the formatted value and survives NaN / out-of-range input', () => {
    const fmt = (n: number) => `${n} কিমি`
    const { rerender } = renderUi(
      <SliderField
        label="ব্যাসার্ধ"
        value={5}
        min={2}
        max={10}
        onValueChange={() => undefined}
        formatValue={fmt}
      />,
    )
    expect(screen.getByText('5 কিমি')).toBeInTheDocument()
    rerender(
      <SliderField
        label="ব্যাসার্ধ"
        value={99}
        min={2}
        max={10}
        onValueChange={() => undefined}
        formatValue={fmt}
      />,
    )
    expect(screen.getByText('10 কিমি')).toBeInTheDocument()
    rerender(
      <SliderField
        label="ব্যাসার্ধ"
        value={Number.NaN}
        min={2}
        max={10}
        onValueChange={() => undefined}
        formatValue={fmt}
      />,
    )
    expect(screen.getByText('2 কিমি')).toBeInTheDocument()
  })

  it('SliderField moves with the keyboard', async () => {
    const onChange = vi.fn()
    renderUi(
      <SliderField
        label="ব্যাসার্ধ"
        value={5}
        min={2}
        max={10}
        onValueChange={onChange}
        formatValue={String}
      />,
    )
    const thumb = screen.getByRole('slider')
    thumb.focus()
    await userEvent.setup().keyboard('{ArrowRight}')
    expect(onChange).toHaveBeenCalledWith(6)
  })

  it('NativeSelect works inside a FormField and reports invalid state', async () => {
    const onChange = vi.fn()
    renderUi(
      <FormField label="জাত" error="একটি বাছুন">
        {(p) => (
          <NativeSelect
            {...p}
            invalid
            onChange={(e) => onChange(e.target.value)}
            options={[
              { value: '', label: 'বাছুন' },
              { value: 'dhan28', label: 'BRRI dhan28' },
            ]}
          />
        )}
      </FormField>,
    )
    const select = screen.getByLabelText('জাত')
    expect(select).toHaveAttribute('aria-invalid', 'true')
    await userEvent.setup().selectOptions(select, 'dhan28')
    expect(onChange).toHaveBeenCalledWith('dhan28')
  })
})

describe('progress, meter, ring and stepper', () => {
  it('Progress clamps to 0..1 and ignores NaN', () => {
    const { rerender } = renderUi(<Progress value={2} label="আপলোড" />)
    expect(screen.getByRole('progressbar', { name: 'আপলোড' })).toHaveAttribute(
      'aria-valuenow',
      '100',
    )
    rerender(<Progress value={-1} label="আপলোড" />)
    expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '0')
    rerender(<Progress value={Number.NaN} label="আপলোড" />)
    expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '0')
  })

  it('Meter exposes a text alternative and clamps its value', () => {
    renderUi(<Meter value={9} min={0} max={5} label="ঝুঁকি" valueText="উচ্চ ঝুঁকি" />)
    const meter = screen.getByRole('meter', { name: 'ঝুঁকি' })
    expect(meter).toHaveAttribute('aria-valuenow', '5')
    expect(meter).toHaveAttribute('aria-valuetext', 'উচ্চ ঝুঁকি')
  })

  it('Ring is an image with a spoken label, never just a coloured circle', () => {
    renderUi(<Ring value={0.9} label="উচ্চ নিশ্চয়তা" />)
    expect(screen.getByRole('img', { name: 'উচ্চ নিশ্চয়তা' })).toBeInTheDocument()
  })

  it('Stepper marks only the current step with aria-current and gives every state an icon', () => {
    renderUi(
      <Stepper
        steps={[
          { id: 'a', label: 'ছবি পরীক্ষা', state: 'done' },
          { id: 'b', label: 'রোগ শনাক্ত', state: 'current' },
          { id: 'c', label: 'পরামর্শ তৈরি', state: 'upcoming' },
        ]}
      />,
    )
    const items = screen.getAllByRole('listitem')
    expect(items.map((i) => i.getAttribute('aria-current'))).toEqual([null, 'step', null])
    for (const item of items) expect(item.querySelector('svg[aria-hidden="true"]')).not.toBeNull()
  })
})

describe('overlays', () => {
  it('Tooltip shows its text on keyboard focus (not hover-only)', async () => {
    renderUi(
      <Tooltip content="১৬ অক্টোবর ২০২৬, ৩:৩০ PM">
        <button type="button">৩ ঘণ্টা আগে</button>
      </Tooltip>,
    )
    await userEvent.setup().tab()
    expect((await screen.findAllByText(/১৬ অক্টোবর/)).length).toBeGreaterThan(0)
  })

  it('Popover opens from its trigger and closes with Escape', async () => {
    const user = userEvent.setup()
    renderUi(
      <Popover trigger={<button type="button">তথ্য</button>}>
        <p>বিস্তারিত</p>
      </Popover>,
    )
    await user.click(screen.getByRole('button', { name: 'তথ্য' }))
    expect(await screen.findByText('বিস্তারিত')).toBeInTheDocument()
    await user.keyboard('{Escape}')
    await waitFor(() => expect(screen.queryByText('বিস্তারিত')).toBeNull())
  })

  it('DropdownMenu opens from the keyboard and runs the chosen item', async () => {
    const onSelect = vi.fn()
    const user = userEvent.setup()
    renderUi(
      <DropdownMenu
        trigger={<button type="button">আরও</button>}
        items={[
          { id: 'a', label: 'সম্পাদনা', onSelect },
          { id: 'b', label: 'মুছুন', onSelect: () => undefined, destructive: true },
        ]}
      />,
    )
    screen.getByRole('button', { name: 'আরও' }).focus()
    await user.keyboard('{Enter}')
    const item = await screen.findByRole('menuitem', { name: 'সম্পাদনা' })
    await user.click(item)
    expect(onSelect).toHaveBeenCalledTimes(1)
  })
})

describe('accessibility of interactive components', () => {
  it('open modal, switch, tabs, slider and progress have no axe violations', async () => {
    const { container } = renderUi(
      <main>
        <h1>শিরোনাম</h1>
        <SwitchField label="বিজ্ঞপ্তি" checked onCheckedChange={() => undefined} />
        <CheckboxField label="সম্মতি" checked={false} onCheckedChange={() => undefined} />
        <Tabs defaultValue="a">
          <TabsList aria-label="ট্যাব">
            <TabsTrigger value="a">এক</TabsTrigger>
            <TabsTrigger value="b">দুই</TabsTrigger>
          </TabsList>
          <TabsContent value="a">প্রথম</TabsContent>
        </Tabs>
        <SliderField
          label="ব্যাসার্ধ"
          value={5}
          min={2}
          max={10}
          onValueChange={() => undefined}
          formatValue={String}
        />
        <Progress value={0.4} label="আপলোড" />
        <Meter value={2} max={5} label="ঝুঁকি" valueText="মাঝারি" />
        <Ring value={0.6} label="মাঝারি নিশ্চয়তা" />
        <Modal open onOpenChange={() => undefined} title="শিরোনাম ২" description="বিবরণ">
          <button type="button">ঠিক আছে</button>
        </Modal>
      </main>,
    )
    expect(await axe(container)).toHaveNoViolations()
  })
})
