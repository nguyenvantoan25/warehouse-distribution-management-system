import { test, expect } from '@playwright/test'
import { readFileSync, mkdirSync } from 'node:fs'
import { resolve } from 'node:path'

test('live PostgreSQL starts with no fabricated business records', async ({ page }) => {
  const accounts = JSON.parse(readFileSync(resolve(process.cwd(), '../backend/accounts.local.json'), 'utf8'))
  const account = accounts.find((a: { username: string }) => a.username === 'admin')
  await page.goto('/login')
  await page.getByLabel('Tên đăng nhập', { exact: true }).fill(account.username)
  await page.getByLabel('Mật khẩu', { exact: true }).fill(account.password)
  await page.getByRole('button', { name: 'Đăng nhập', exact: true }).click()
  await expect(page.getByText(/Nguồn: PostgreSQL/)).toBeVisible()
  const dashboard = await (await page.request.get('/api/v1/dashboard')).json()
  expect(dashboard.dataSource.storage).toBe('postgresql')
  expect(dashboard.tasks).toEqual([])
  mkdirSync(resolve(process.cwd(), '../../docs/screenshots'), { recursive: true })
  await page.screenshot({ path: resolve(process.cwd(), '../../docs/screenshots/postgresql-empty.png'), fullPage: true })
  expect(dashboard.flow.every((point: { quantity: number }) => point.quantity === 0)).toBe(true)
  for (const resource of ['warehouses', 'partners', 'skus', 'inventory/balances', 'inbound-requests', 'outbound-requests']) {
    const response = await page.request.get('/api/v1/' + resource)
    expect(response.ok()).toBe(true)
    expect(await response.json()).toEqual([])
  }
  const profile = await (await page.request.get('/api/v1/auth/me')).json()
  await page.request.post('/api/v1/auth/logout', { headers: { 'X-CSRF-Token': profile.csrfToken } })
})
