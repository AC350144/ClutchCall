import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './setupTests.ts',
    include: ['frontend/tests/**/*.test.tsx', 'frontend/components/**/*.test.tsx'],
  },
});