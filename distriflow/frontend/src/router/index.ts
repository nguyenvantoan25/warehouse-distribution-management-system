import { createRouter, createWebHistory } from 'vue-router'
import { belongsToPortal } from '../app/portals'
import { operationsRoutes } from '../portals/operations/routes'
import { supplierRoutes } from '../portals/supplier/routes'
import { retailerRoutes } from '../portals/retailer/routes'
import { shipperRoutes } from '../portals/shipper/routes'
import { auth, can, homePath, restoreSession } from '../app/access'

const router = createRouter({ history: createWebHistory(), routes: [
  // Resolve home only after restoring the session in beforeEach.
  { path: '/', component: { render: () => null } },
  { path: '/login', component: () => import('../features/auth/LoginPage.vue') },
  { path: '/forbidden', component: () => import('../features/auth/ForbiddenPage.vue') },
  ...operationsRoutes,
  ...supplierRoutes,
  ...retailerRoutes,
  ...shipperRoutes,
  // Preserve existing bookmarks; every destination still passes the access guard.
  { path: '/partner', component: { render: () => null } },
  { path: '/partner/inbounds', redirect: '/supplier/inbounds' },
  { path: '/partner/outbounds', redirect: '/retailer/outbounds' },
  { path: '/partner/inventory', redirect: '/retailer/inventory' },
  { path: '/:pathMatch(.*)*', redirect: '/' },
] })
router.beforeEach(async (to) => {
  if (!auth.loaded) {
    try { await restoreSession() } catch { return to.path === '/login' ? true : '/login' }
  }
  if (!auth.user && to.path !== '/login') return '/login'
  if (to.path === '/' || to.path === '/partner') return homePath()
  if (auth.user && to.path === '/login') return homePath()
  if (to.matched.some(record => {
    const portal = record.meta.portal
    return (portal && !belongsToPortal(auth.user?.role ?? '', portal))
      || (typeof record.meta.access === 'string' && !can(record.meta.access))
  })) return '/forbidden'
})
export default router
