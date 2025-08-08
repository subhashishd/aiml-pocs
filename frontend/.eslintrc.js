module.exports = {
  root: true,
  env: {
    browser: true,
    es2022: true,
    node: true,
    jest: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'prettier',
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 'latest',
    sourceType: 'module',
    project: './tsconfig.json',
  },
  plugins: [
    'react',
    'react-hooks',
    '@typescript-eslint',
    'jsx-a11y',
    'import',
    'testing-library',
  ],
  settings: {
    react: {
      version: 'detect',
    },
    'import/resolver': {
      typescript: {
        alwaysTryTypes: true,
        project: './tsconfig.json',
      },
    },
  },
  rules: {
    // TypeScript - disabled for now
    // '@typescript-eslint/no-unused-vars': [
    //   'error',
    //   { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
    // ],
    // '@typescript-eslint/no-explicit-any': 'warn',
    // '@typescript-eslint/explicit-function-return-type': 'off',
    // '@typescript-eslint/explicit-module-boundary-types': 'off',
    // '@typescript-eslint/no-non-null-assertion': 'warn',
    // '@typescript-eslint/prefer-const': 'error',
    // '@typescript-eslint/no-var-requires': 'error',

    // React
    'react/react-in-jsx-scope': 'off',
    'react/prop-types': 'off',
    'react/display-name': 'off',
    'react/no-unescaped-entities': 'warn',
    'react/jsx-uses-react': 'off',
    'react/jsx-uses-vars': 'error',
    'react/jsx-key': 'error',
    'react/jsx-no-duplicate-props': 'error',
    'react/jsx-no-undef': 'error',
    'react/no-array-index-key': 'warn',
    'react/no-children-prop': 'error',
    'react/no-deprecated': 'warn',
    'react/self-closing-comp': 'error',

    // React Hooks
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',

    // Import - disabled for now
    // 'import/order': [
    //   'error',
    //   {
    //     groups: [
    //       'builtin',
    //       'external',
    //       'internal',
    //       'parent',
    //       'sibling',
    //       'index',
    //       'object',
    //       'type',
    //     ],
    //     'newlines-between': 'always',
    //     alphabetize: {
    //       order: 'asc',
    //       caseInsensitive: true,
    //     },
    //   },
    // ],
    'import/no-unresolved': 'error',
    'import/no-duplicates': 'error',
    'import/no-unused-modules': 'warn',
    'import/no-cycle': 'error',

    // General
    'no-console': ['warn', { allow: ['warn', 'error', 'debug'] }],
    'no-debugger': 'error',
    'no-alert': 'error',
    'no-var': 'error',
    'prefer-const': 'error',
    'no-duplicate-imports': 'error',
    'no-template-curly-in-string': 'error',
    'array-callback-return': 'error',
    'consistent-return': 'warn', // Changed from error to warn
    'no-return-assign': 'error',
    'no-param-reassign': 'error',
    'no-nested-ternary': 'warn',
    'no-unneeded-ternary': 'error',
    'prefer-template': 'warn', // Changed from error to warn
    'no-unused-vars': 'warn', // Add this to handle unused vars

    // Accessibility
    'jsx-a11y/alt-text': 'error',
    'jsx-a11y/anchor-has-content': 'error',
    'jsx-a11y/anchor-is-valid': 'error',
    'jsx-a11y/click-events-have-key-events': 'warn',
    'jsx-a11y/no-static-element-interactions': 'warn',
  },
  overrides: [
    {
      files: ['**/__tests__/**/*', '**/*.{test,spec}.*'],
      extends: ['plugin:testing-library/react'],
      rules: {
        'testing-library/await-async-query': 'error',
        'testing-library/no-await-sync-query': 'error',
        'testing-library/no-debug': 'warn',
        'testing-library/no-dom-import': 'error',
        'testing-library/prefer-screen-queries': 'error',
      },
    },
    {
      files: ['*.js'],
      rules: {
        '@typescript-eslint/no-var-requires': 'off',
      },
    },
  ],
  ignorePatterns: [
    'build/',
    'dist/',
    'node_modules/',
    '*.min.js',
    'coverage/',
    'public/',
  ],
};
