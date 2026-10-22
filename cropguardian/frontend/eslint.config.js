import js from '@eslint/js'
import i18next from 'eslint-plugin-i18next'
import jsxA11y from 'eslint-plugin-jsx-a11y'
import reactHooks from 'eslint-plugin-react-hooks'
import security from 'eslint-plugin-security'
import globals from 'globals'
import tseslint from 'typescript-eslint'

const xssSinks = [
  {
    selector: "JSXAttribute[name.name='dangerouslySetInnerHTML']",
    message: 'XSS sink forbidden',
  },
  {
    selector: 'MemberExpression[property.name=/^(innerHTML|outerHTML)$/]',
    message: 'XSS sink forbidden',
  },
  {
    selector: "CallExpression[callee.property.name='insertAdjacentHTML']",
    message: 'XSS sink forbidden',
  },
]

// Spec 15.2 / 19.8: colours and animation timing are defined in src/design only.
const designSystemOnly = [
  {
    selector: 'Literal[value=/#[0-9a-fA-F]{3,8}\\b/]',
    message:
      'Hex colours live in src/design/tokens.* only: use a token (CSS variable / tokens.ts).',
  },
  {
    selector:
      'Property[key.name=/^(duration|delay|staggerChildren|delayChildren)$/] > Literal[raw=/^[0-9.]/]',
    message: 'Animation durations and delays live in src/design/motion.ts only.',
  },
]

export default tseslint.config(
  { ignores: ['dist', 'node_modules', 'scripts', 'playwright-report', 'test-results'] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  security.configs.recommended,
  jsxA11y.flatConfigs.recommended,
  reactHooks.configs.flat.recommended,
  {
    files: ['src/**/*.{ts,tsx}'],
    languageOptions: { globals: { ...globals.browser } },
    plugins: { i18next },
    rules: {
      // no hard-coded user-facing strings in JSX (spec 15.9)
      'i18next/no-literal-string': ['error', { mode: 'jsx-text-only' }],
      'no-eval': 'error',
      'no-implied-eval': 'error',
      'no-new-func': 'error',
      'no-restricted-syntax': ['error', ...xssSinks, ...designSystemOnly],
    },
  },
  {
    // design tokens are the only place hex colours and numeric durations may be defined
    files: ['src/design/**'],
    rules: {
      'security/detect-object-injection': 'off',
      'no-restricted-syntax': ['error', ...xssSinks],
    },
  },
  {
    files: ['src/**/*.test.{ts,tsx}', 'tests/**/*.{ts,tsx}'],
    languageOptions: { globals: { ...globals.node, ...globals.browser } },
    rules: {
      'i18next/no-literal-string': 'off',
      'security/detect-non-literal-fs-filename': 'off',
      'security/detect-object-injection': 'off',
      'no-restricted-syntax': 'off',
    },
  },
)
