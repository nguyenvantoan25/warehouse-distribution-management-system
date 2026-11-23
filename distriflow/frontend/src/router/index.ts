import { createRouter, createWebHistory } from 'vue-router'
import AdminDashboard from '../features/admin/AdminDashboard.vue'
import ShipperTasks from '../features/shipper/ShipperTasks.vue'

const router = createRouter({ history: createWebHistory(), routes: [
  { path: '/', redirect: '/admin/dashboard' },
  { path: '/admin/dashboard', component: AdminDashboard, meta: { roles: ['WAREHOUSE_ADMIN', 'DISPATCH_MANAGER'] } },
  { path: '/shipper/tasks', component: ShipperTasks, meta: { roles: ['SHIPPER'] } },
] })
export default router
