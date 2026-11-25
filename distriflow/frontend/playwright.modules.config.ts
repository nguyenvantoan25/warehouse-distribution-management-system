import { defineConfig } from '@playwright/test'
import { resolve } from 'node:path'
export default defineConfig({
  testDir: './tests/e2e', testMatch: 'modules-workflow.spec.ts', workers: 1, timeout: 90000,
  use: { baseURL: 'http://127.0.0.1:5174', channel: 'msedge', headless: true, actionTimeout: 10000, navigationTimeout: 15000, viewport: { width: 1440, height: 1000 } },
  reporter: [['list']],
  webServer: [
    { command: 'python -m tests.serve_e2e', cwd: resolve(process.cwd(), '../backend'), url: 'http://127.0.0.1:8001/health', reuseExistingServer: false },
    { command: 'node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5174', url: 'http://127.0.0.1:5174', env: { API_PROXY_TARGET: 'http://127.0.0.1:8001' }, reuseExistingServer: false },
  ],
})
