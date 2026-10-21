import type { Config } from 'tailwindcss'

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
      },
      borderRadius: {
        sm: v('radius-sm'),
        md: v('radius-md'),
        lg: v('radius-lg'),
        xl: v('radius-xl'),
      },
      boxShadow: { xs: v('shadow-xs'), sm: v('shadow-sm'), md: v('shadow-md'), lg: v('shadow-lg') },
      fontFamily: { bn: [v('font-bn')], latin: [v('font-latin')], mono: [v('font-mono')] },
    },
  },
  plugins: [],
} satisfies Config
