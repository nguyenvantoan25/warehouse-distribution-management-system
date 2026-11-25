<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { LayoutDashboard, FileText, Truck, BarChart3, Settings, ChevronDown, Menu, LogOut, Bell, Search, MoreHorizontal, Warehouse, Users, Store, ArrowDownToLine, ArrowUpRight, MapPin } from 'lucide-vue-next'
import { auth, can, logout } from '../../app/access'
import { useOperations } from '../handover/useOperations'
import DistriFlowLogo from '../../shared/components/DistriFlowLogo.vue'
const route = useRoute(); const router = useRouter()
const mobileOpen = ref(false); const quickSearch = ref('')
const { tasks, load } = useOperations()
const pending = computed(() => tasks.value.filter(task => task.status === 'pending_confirmations'))
const pageTitles: Record<string, string> = { '/admin/dashboard': 'Tổng quan', '/admin/dispatch': 'Điều phối vận chuyển', '/admin/catalog': 'Danh mục & vị trí', '/admin/partners': 'Đối tác', '/admin/inbounds': 'Nhập kho', '/admin/outbounds': 'Xuất kho', '/admin/inventory': 'Tồn kho' }
const page = computed(() => pageTitles[route.path] ?? (route.params.id ? 'Chi tiết bàn giao' : 'Phiếu bàn giao'))
pageTitles['/admin/accounts'] = 'Tài khoản & phạm vi'
const roles: Record<string, string> = { WAREHOUSE_ADMIN: 'Quản trị hệ thống', DISPATCH_MANAGER: 'Quản lý điều phối' }
const name = computed(() => auth.user?.username ?? '')
const initials = computed(() => name.value.slice(0,2).toUpperCase())
async function leave() { await logout(); await router.replace('/login') }
function search() { if (quickSearch.value.trim()) { router.push({ path: '/admin/handovers', query: { q: quickSearch.value.trim() } }); quickSearch.value = '' } }
function closeMenu() { mobileOpen.value = false }
</script>
<template>
  <div class="ops-shell" :class="{ 'sidebar-open': mobileOpen }">
    <button v-if="mobileOpen" class="ops-mobile-overlay" aria-label="Đóng menu" @click="closeMenu"/>
    <aside class="ops-sidebar">
      <RouterLink class="ops-brand" to="/admin/dashboard" @click="closeMenu"><DistriFlowLogo/></RouterLink>
      <div class="ops-nav">
        <span class="ops-nav-label">KHÔNG GIAN QUẢN TRỊ</span>
        <RouterLink to="/admin/dashboard" class="ops-nav-item" :class="{ selected: route.path === '/admin/dashboard' }" @click="closeMenu"><LayoutDashboard :size="17"/> Tổng quan</RouterLink>
        <RouterLink to="/admin/handovers" class="ops-nav-item" :class="{ selected: route.path.includes('/handovers') }" @click="closeMenu"><FileText :size="17"/> Phiếu bàn giao<span v-if="pending.length" class="ops-nav-counter">{{ pending.length }}</span></RouterLink>
        <RouterLink v-if="can('dispatch.assign')" to="/admin/dispatch" class="ops-nav-item" :class="{ selected: route.path === '/admin/dispatch' }" @click="closeMenu"><Truck :size="17"/> Điều phối vận chuyển</RouterLink>
        <RouterLink v-if="can('catalog.manage')" to="/admin/partners" class="ops-nav-item" active-class="selected" @click="closeMenu"><Store :size="17"/> Đối tác</RouterLink>
        <RouterLink v-if="can('inbound.manage')" to="/admin/inbounds" class="ops-nav-item" active-class="selected" @click="closeMenu"><ArrowDownToLine :size="17"/> Nhập kho</RouterLink>
        <RouterLink v-if="can('outbound.manage')" to="/admin/outbounds" class="ops-nav-item" active-class="selected" @click="closeMenu"><ArrowUpRight :size="17"/> Xuất kho</RouterLink>
        <RouterLink v-if="can('inventory.read')" to="/admin/inventory" class="ops-nav-item" active-class="selected" @click="closeMenu"><Warehouse :size="17"/> Tồn kho</RouterLink>
        <RouterLink v-if="can('catalog.manage')" to="/admin/catalog" class="ops-nav-item" active-class="selected" @click="closeMenu"><MapPin :size="17"/> Danh mục & vị trí</RouterLink>
        <button class="ops-nav-item" disabled title="Chưa triển khai"><BarChart3 :size="17"/> Báo cáo</button>
        <RouterLink v-if="can('accounts.manage')" to="/admin/accounts" class="ops-nav-item ops-nav-divider" active-class="selected" @click="closeMenu"><Users :size="17"/> Tài khoản & phạm vi</RouterLink>
        <button class="ops-nav-item" disabled title="Chưa triển khai"><Settings :size="17"/> Cài đặt</button>
      </div>
      <div class="ops-sidebar-user"><span class="ops-user-square">{{ initials }}</span><div><b>{{ name }}</b><small>{{ roles[auth.user?.role ?? ''] }}</small></div><details class="ops-sidebar-user-menu"><summary aria-label="Tùy chọn tài khoản"><MoreHorizontal :size="17"/></summary><button @click="leave"><LogOut :size="15"/> Đăng xuất</button></details></div>
    </aside>
    <div class="ops-workspace">
      <header class="ops-topbar">
        <button class="ops-icon-button ops-mobile-menu" aria-label="Mở menu" @click="mobileOpen = !mobileOpen"><Menu :size="19"/></button>
        <div class="ops-header-title"><p>DistriFlow <span>/</span> {{ page }}</p><h1>{{ page }}</h1></div>
        <div class="ops-topbar-right">
          <form class="ops-quick-search" @submit.prevent="search"><Search :size="15"/><input v-model="quickSearch" aria-label="Tìm kiếm nhanh" placeholder="Tìm kiếm nhanh…"/></form>
          <details class="ops-notifications"><summary class="ops-icon-button" aria-label="Thông báo cần xác nhận" @click="load"><Bell :size="18"/><i v-if="pending.length"/></summary><div class="ops-notification-popover"><b>Cần xác nhận bàn giao</b><p v-if="!pending.length">Không có phiếu chờ xác nhận.</p><RouterLink v-for="task in pending" :key="task.id" :to="`/admin/handovers/${task.id}`">{{ task.code }} <small>{{ task.packages.length }} kiện</small></RouterLink></div></details>
          <details class="ops-account"><summary><span class="ops-avatar">{{ initials }}</span><ChevronDown :size="14"/></summary><div class="ops-account-menu"><b>{{ name }}</b><small>{{ roles[auth.user?.role ?? ''] }}</small><button @click="leave"><LogOut :size="15"/> Đăng xuất</button></div></details>
        </div>
      </header>
      <main class="ops-main"><RouterView/></main>
    </div>
  </div>
</template>
