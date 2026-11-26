import type { RouteRecordRaw } from 'vue-router'
export const supplierRoutes: RouteRecordRaw[] = [{
  path: '/supplier', component: () => import('./SupplierLayout.vue'),
  meta: { portal: 'supplier', access: 'catalog.read' },
  children: [
    { path: '', redirect: '/supplier/inbounds' },
    { path: 'inbounds', component: () => import('../../features/inbound/InboundPage.vue'), meta: { access: 'inbound.read' } },
  ],
}]
