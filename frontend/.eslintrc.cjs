module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint', 'react'],
  extends: ['next/core-web-vitals', 'plugin:@typescript-eslint/recommended'],
  rules: {
    // Disallow relative API calls from the browser – must use absolute base URL
    'no-restricted-syntax': [
      'error',
      {
        selector: "CallExpression[callee.name='fetch'] Literal[value^='/api/']",
        message: 'Do not use relative /api URLs. Use NEXT_PUBLIC_API_URL (absolute) or ApiClient.'
      }
    ]
  }
}
