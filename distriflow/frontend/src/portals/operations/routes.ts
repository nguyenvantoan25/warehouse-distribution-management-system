import type { RouteRecordRaw } from 'vue-router'

export const operationsRoutes: RouteRecordRaw[] = [{
  path: '/admin',
  component: () => import('../../features/admin/AdminLayout.vue'),
  meta: { portal: 'operations', access: 'dashboard.read' },
  children: [
    { path: '', redirect: '/admin/dashboard' },
    { path: 'dashboard', component: () => import('../../features/dashboard/DashboardPage.vue') },
    { path: 'handovers', component: () => import('../../features/handover/HandoverList.vue'), meta: { access: 'tasks.read' } },
    { path: 'handovers/:id', component: () => import('../../features/handover/HandoverDetail.vue'), meta: { access: 'tasks.read' } },
    { path: 'dispatch', component: () => import('../../features/dispatch/DispatchPage.vue'), meta: { access: 'dispatch.assign' } },
    { path: 'catalog', component: () => import('../../features/catalog/CatalogPage.vue'), meta: { access: 'catalog.manage' } },
    { path: 'warehouses', component: () => import('../../features/catalog/WarehousePage.vue'), meta: { access: 'catalog.manage' } },
    { path: 'partners', redirect: { path: '/admin/accounts', query: { group: 'supplier' } } },
    { path: 'inbounds', component: () => import('../../features/inbound/InboundPage.vue'), meta: { access: 'inbound.manage' } },
    { path: 'outbounds', component: () => import('../../features/outbound/OutboundPage.vue'), meta: { access: 'outbound.manage' } },
    { path: 'inventory', component: () => import('../../features/inventory/InventoryPage.vue'), meta: { access: 'inventory.read' } },
    { path: 'accounts', component: () => import('../../features/accounts/DirectoryPage.vue'), meta: { access: 'accounts.manage' } },
    { path: 'account-scopes', component: () => import('../../features/accounts/AccountScopesPage.vue'), meta: { access: 'accounts.manage' } },
  ],
}]
