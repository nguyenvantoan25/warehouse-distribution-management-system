import { createRouter, createWebHistory } from 'vue-router'
import AdminDashboard from '../features/dashboard/DashboardPage.vue'
import AdminLayout from '../features/admin/AdminLayout.vue'
import HandoverList from '../features/handover/HandoverList.vue'
import HandoverDetail from '../features/handover/HandoverDetail.vue'
import DispatchPage from '../features/dispatch/DispatchPage.vue'
import CatalogPage from '../features/catalog/CatalogPage.vue'
import InboundPage from '../features/inbound/InboundPage.vue'
import OutboundPage from '../features/outbound/OutboundPage.vue'
import InventoryPage from '../features/inventory/InventoryPage.vue'
import AccountScopesPage from '../features/accounts/AccountScopesPage.vue'
import PartnerLayout from '../features/partner/PartnerLayout.vue'
import ShipperTasks from '../features/shipper/ShipperTasks.vue'
import LoginPage from '../features/auth/LoginPage.vue'
import ForbiddenPage from '../features/auth/ForbiddenPage.vue'
import { auth, can, homePath, restoreSession } from '../app/access'

const router = createRouter({ history: createWebHistory(), routes: [
  { path: '/', redirect: () => homePath() },
  { path: '/login', component: LoginPage },
  { path: '/forbidden', component: ForbiddenPage },
  { path: '/admin', component: AdminLayout, meta: { access: 'dashboard.read' }, children: [
    { path: '', redirect: '/admin/dashboard' },
    { path: 'dashboard', component: AdminDashboard },
    { path: 'handovers', component: HandoverList, meta: { access: 'tasks.read' } },
    { path: 'handovers/:id', component: HandoverDetail, meta: { access: 'tasks.read' } },
    { path: 'dispatch', component: DispatchPage, meta: { access: 'dispatch.assign' } },
    { path: 'catalog', component: CatalogPage, meta: { access: 'catalog.manage' } },
    { path: 'partners', component: CatalogPage, meta: { access: 'catalog.manage' } },
    { path: 'inbounds', component: InboundPage, meta: { access: 'inbound.manage' } },
    { path: 'outbounds', component: OutboundPage, meta: { access: 'outbound.manage' } },
    { path: 'inventory', component: InventoryPage, meta: { access: 'inventory.read' } },
    { path: 'accounts', component: AccountScopesPage, meta: { access: 'accounts.manage' } },
  ] },
  { path: '/partner', component: PartnerLayout, meta: { access: 'catalog.read' }, children: [
    { path: 'inbounds', component: InboundPage, meta: { access: 'inbound.read' } },
    { path: 'outbounds', component: OutboundPage, meta: { access: 'outbound.read' } },
    { path: 'inventory', component: InventoryPage, meta: { access: 'inventory.read' } },
  ] },
  { path: '/shipper/tasks', component: ShipperTasks, meta: { access: 'tasks.read.own' } },
  { path: '/:pathMatch(.*)*', redirect: '/' },
] })
router.beforeEach(async (to) => {
  if (!auth.loaded) {
    try { await restoreSession() } catch { return to.path === '/login' ? true : '/login' }
  }
  if (!auth.user && to.path !== '/login') return '/login'
  if (auth.user && to.path === '/login') return homePath()
  if (to.matched.some(record => typeof record.meta.access === 'string' && !can(record.meta.access))) return '/forbidden'
})
export default router
