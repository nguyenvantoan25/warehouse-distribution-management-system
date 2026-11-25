import { test, expect } from '@playwright/test'
import { readFileSync, mkdirSync } from 'node:fs'
import { resolve } from 'node:path'

const accounts = JSON.parse(readFileSync(resolve(process.cwd(), '../backend/accounts.local.json'), 'utf8'))
const account = accounts.find((user: { username: string }) => user.username === 'dispatch')
const screenshots = resolve(process.cwd(), '../../docs/screenshots')
mkdirSync(screenshots, { recursive: true })

test.afterEach(async ({ page }) => {
  const profile = await page.request.get('/api/v1/auth/me')
  if (profile.ok()) {
    await page.request.post('/api/v1/auth/logout', { headers: { 'X-CSRF-Token': (await profile.json()).csrfToken } })
  }
})

for (const width of [1440, 1024, 390, 360]) {
  test(`reference layout and navigation at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1000 })
    const errors: string[] = []
    page.on('pageerror', error => errors.push(error.message))
    await page.goto('/login')
    await page.getByLabel('Tên đăng nhập', { exact: true }).fill(account.username)
    await page.getByLabel('Mật khẩu', { exact: true }).fill(account.password)
    await page.getByRole('button', { name: 'Đăng nhập', exact: true }).click()
    await expect(page.getByRole('heading', { name: 'Tình hình vận hành', exact: true })).toBeVisible()
    await page.evaluate(() => document.fonts.ready)
    await expect(page.locator('.df-kpi')).toHaveCount(4)
    await expect(page.locator('.df-flow-chart svg')).toBeVisible()
    const measurements = await page.evaluate(() => ({
      sidebar: document.querySelector('.ops-sidebar')!.getBoundingClientRect().width,
      header: document.querySelector('.ops-topbar')!.getBoundingClientRect().height,
      padding: getComputedStyle(document.querySelector('.ops-main')!).paddingLeft,
      font: getComputedStyle(document.querySelector('.ops-shell')!).fontFamily,
      fontLoaded: document.fonts.check('12px "Be Vietnam Pro"'),
      kpiGap: getComputedStyle(document.querySelector('.df-kpi-grid')!).gap,
      cardRadius: getComputedStyle(document.querySelector('.df-kpi')!).borderRadius,
      chartHeight: document.querySelector('.df-flow-chart')!.getBoundingClientRect().height,
      overflow: document.documentElement.scrollWidth > innerWidth,
    }))
    expect(measurements.sidebar).toBe(248)
    expect(measurements.header).toBe(72)
    expect(measurements.font).toContain('Be Vietnam Pro')
    expect(measurements.fontLoaded).toBe(true)
    expect(measurements.kpiGap).toBe('12px')
    expect(measurements.cardRadius).toBe('12px')
    if (width >= 640) expect(measurements.chartHeight).toBe(260)
    if (width >= 1024) expect(measurements.padding).toBe('28px')
    expect(measurements.overflow).toBe(false)
    await page.screenshot({ path: resolve(screenshots, `dashboard-${width}.png`), fullPage: true })
    if (width === 1440) {
      await page.getByRole('link', { name: 'Xem tất cả' }).click()
      await expect(page.getByRole('heading', { name: 'Danh sách phiếu bàn giao' })).toBeVisible()
      await page.locator('.ops-search input').fill('NO-SUCH-DOCUMENT')
      await expect(page.getByText('Không có phiếu phù hợp với bộ lọc.')).toBeVisible()
      await page.locator('.ops-search input').fill('')
      await page.screenshot({ path: resolve(screenshots, 'handovers-1440.png'), fullPage: true })
      if (await page.locator('.ops-code').count()) {
      await page.locator('.ops-code').first().click()
      await expect(page.getByRole('heading', { name: 'Chi tiết phiếu bàn giao' })).toBeVisible()
      await page.screenshot({ path: resolve(screenshots, 'detail-1440.png'), fullPage: true })
      } else {
        await expect(page.getByText('Không có phiếu phù hợp với bộ lọc.')).toBeVisible()
      }
      await page.getByRole('link', { name: 'Điều phối vận chuyển', exact: true }).click()
      await expect(page.getByRole('heading', { name: 'Phân bổ vận chuyển', exact: true })).toBeVisible()
      await expect(page.locator('#shipper')).toBeVisible()
      await page.screenshot({ path: resolve(screenshots, 'dispatch-1440.png'), fullPage: true })
    } else if (width < 1024) {
      await page.getByRole('button', { name: 'Mở menu' }).click()
      await expect(page.locator('.ops-sidebar')).toBeInViewport()
      await page.locator('.ops-nav').getByRole('link', { name: 'Phiếu bàn giao' }).click()
      await expect(page.locator('.ops-sidebar')).not.toBeInViewport()
      await expect(page.getByRole('heading', { name: 'Danh sách phiếu bàn giao' })).toBeVisible()
      expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false)
      await page.screenshot({ path: resolve(screenshots, `handovers-${width}.png`), fullPage: true })
    }
    expect(errors).toEqual([])
  })
}

test('shipper portal keeps four functional mobile tabs', async ({ page }) => {
  const shipper = accounts.find((user: { username: string }) => user.username === 'shipper')
  await page.setViewportSize({ width: 390, height: 844 })
  const errors: string[] = []
  page.on('pageerror', error => errors.push(error.message))
  await page.goto('/login')
  await page.evaluate(() => document.fonts.ready)
  await page.screenshot({ path: resolve(screenshots, 'login-390.png'), fullPage: true })
  await page.getByLabel('Tên đăng nhập', { exact: true }).fill(shipper.username)
  await page.getByLabel('Mật khẩu', { exact: true }).fill(shipper.password)
  await page.getByRole('button', { name: 'Đăng nhập', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Nhiệm vụ', exact: true })).toBeVisible()
  await expect(page.locator('nav[aria-label="Shipper"] button')).toHaveCount(4)
  if (await page.locator('.task .badge').count()) {
    expect((await page.locator('.task .badge').boundingBox())!.height).toBeLessThan(40)
  }
  await page.screenshot({ path: resolve(screenshots, 'shipper-390.png'), fullPage: true })
  for (const tab of ['Lịch sử', 'Tài khoản', 'Quét mã', 'Nhiệm vụ']) {
    await page.getByRole('navigation', { name: 'Shipper' }).getByRole('button', { name: tab, exact: true }).click()
    await expect(page.getByRole('heading', { name: tab, exact: true })).toBeVisible()
  }
  expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false)
  expect(errors).toEqual([])
})
