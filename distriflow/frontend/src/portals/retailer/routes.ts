import type { RouteRecordRaw } from 'vue-router'
export const retailerRoutes: RouteRecordRaw[] = [{
  path: '/retailer', component: () => import('./RetailerLayout.vue'),
  meta: { portal: 'retailer', access: 'catalog.read' },
  children: [
    { path: '', redirect: '/retailer/outbounds' },
    { path: 'outbounds', component: () => import('../../features/outbound/OutboundPage.vue'), meta: { access: 'outbound.read' } },
    { path: 'inventory', component: () => import('../../features/inventory/InventoryPage.vue'), meta: { access: 'inventory.read' } },
  ],
}]
