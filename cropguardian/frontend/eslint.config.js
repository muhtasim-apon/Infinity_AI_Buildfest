import js from '@eslint/js'
import i18next from 'eslint-plugin-i18next'
import jsxA11y from 'eslint-plugin-jsx-a11y'
import reactHooks from 'eslint-plugin-react-hooks'
import security from 'eslint-plugin-security'
import globals from 'globals'
import tseslint from 'typescript-eslint'

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
      'no-restricted-syntax': [
        'error',
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
      ],
    },
  },
  {
    // design tokens are the only place hex colours and numeric durations may be defined
    files: ['src/design/**'],
    rules: { 'security/detect-object-injection': 'off' },
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
