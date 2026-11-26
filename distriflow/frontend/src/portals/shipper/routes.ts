import type { RouteRecordRaw } from 'vue-router'
// Browser fallback; the native client lives in android-shipper/.
export const shipperRoutes: RouteRecordRaw[] = [{
  path: '/shipper/tasks', component: () => import('../../features/shipper/ShipperTasks.vue'),
  meta: { portal: 'shipper', access: 'tasks.read.own' },
}]
