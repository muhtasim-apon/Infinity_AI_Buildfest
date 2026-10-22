import type { Config } from 'tailwindcss'
import plugin from 'tailwindcss/plugin'

// Colours come from CSS variables defined in src/design/tokens.css (single source of truth).
const v = (name: string) => `var(--${name})`

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: v('bg'),
        surface: v('surface'),
        'surface-2': v('surface-2'),
        border: v('border'),
        text: v('text'),
        muted: v('text-muted'),
        subtle: v('text-subtle'),
        primary: {
          DEFAULT: v('primary'),
          hover: v('primary-hover'),
          soft: v('primary-soft'),
          on: v('on-primary'),
        },
        accent: { DEFAULT: v('accent'), bg: v('accent-bg') },
        sky: { DEFAULT: v('sky'), bg: v('sky-bg') },
        success: { DEFAULT: v('success'), bg: v('success-bg') },
        warning: { DEFAULT: v('warning'), bg: v('warning-bg') },
        danger: { DEFAULT: v('danger'), bg: v('danger-bg') },
        simulated: { DEFAULT: v('simulated'), bg: v('simulated-bg') },
        disease: {
          1: v('disease-1'),
          2: v('disease-2'),
          3: v('disease-3'),
          4: v('disease-4'),
          5: v('disease-5'),
          6: v('disease-6'),
          7: v('disease-7'),
        },
        risk: { low: v('risk-low'), medium: v('risk-medium'), high: v('risk-high') },
      },
      borderRadius: {
        sm: v('radius-sm'),
        md: v('radius-md'),
        lg: v('radius-lg'),
        xl: v('radius-xl'),
      },
      boxShadow: { xs: v('shadow-xs'), sm: v('shadow-sm'), md: v('shadow-md'), lg: v('shadow-lg') },
      fontFamily: { bn: [v('font-bn')], latin: [v('font-latin')], mono: [v('font-mono')] },
      // Timing comes from tokens.css (mirror of design/motion.ts): no numeric durations in class names.
      transitionDuration: {
        press: v('duration-press'),
        fast: v('duration-fast'),
        base: v('duration-base'),
        slow: v('duration-slow'),
        page: v('duration-page'),
      },
      transitionTimingFunction: {
        standard: v('ease-standard'),
        emphasized: v('ease-emphasized'),
        exit: v('ease-exit'),
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '200% 0' },
          '100%': { backgroundPosition: '-200% 0' },
        },
        drain: { from: { transform: 'scaleX(1)' }, to: { transform: 'scaleX(0)' } },
        breathe: {
          '0%': { transform: 'scale(1)', opacity: '0.5' },
          '100%': { transform: 'scale(1.04)', opacity: '0' },
        },
      },
      animation: {
        shimmer: 'shimmer var(--shimmer-duration) linear infinite',
        breathe: 'breathe var(--breathe-duration) ease-out infinite',
        drain: 'drain var(--toast-duration) linear forwards',
      },
    },
  },
  plugins: [
    // `motion-ok:` applies only when the OS and the in-app setting both allow motion and data saver
    // is off (spec 15.2: reduced motion = no transforms, scale, shimmer, pulses).
    plugin(({ addVariant }) => {
      addVariant(
        'motion-ok',
        '@media (prefers-reduced-motion: no-preference) { :root:not([data-reduced-motion="true"]) & }',
      )
    }),
  ],
} satisfies Config
