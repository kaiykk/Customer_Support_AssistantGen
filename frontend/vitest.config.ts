import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'node:url'

/**
 * Vitest configuration for AssistGen frontend tests
 * 
 * This configuration sets up the testing environment for Vue 3 components
 * with TypeScript support and coverage reporting.
 */
export default defineConfig({
  plugins: [vue()],
  
  test: {
    // Test environment
    environment: 'jsdom',
    
    // Global test setup
    globals: true,
    
    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.spec.ts',
        '**/*.test.ts',
        '**/dist/**',
      ],
      // Minimum coverage thresholds
      statements: 70,
      branches: 70,
      functions: 70,
      lines: 70,
    },
    
    // Test file patterns
    include: ['**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    
    // Setup files
    setupFiles: ['./tests/setup.ts'],
  },
  
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
