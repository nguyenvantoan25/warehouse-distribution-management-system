<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Search, Download, RefreshCw, ChevronLeft, ChevronRight, Plus, Filter, FileText } from 'lucide-vue-next'
import { useOperations, exportTasks } from './useOperations'
import TaskTable from './TaskTable.vue'
import { can } from '../../app/access'
const route = useRoute()
const { tasks, warehouses, loading, error, load } = useOperations()
const search = ref(String(route.query.q ?? '')); const warehouse = ref(''); const status = ref(String(route.query.status ?? '')); const page = ref(1); const pageSize = ref(10)
const filtered = computed(() => tasks.value.filter(task => (!warehouse.value || task.warehouseName === warehouse.value) && (!status.value || task.status === status.value) && `${task.code} ${task.shipperName}`.toLocaleLowerCase('vi').includes(search.value.toLocaleLowerCase('vi'))))
const pages = computed(() => Math.max(1, Math.ceil(filtered.value.length / pageSize.value)))
const displayed = computed(() => filtered.value.slice((page.value - 1) * pageSize.value, page.value * pageSize.value))
watch([search, warehouse, status, pageSize], () => { page.value = 1 })
watch(() => route.query.status, value => { status.value = String(value ?? '') })
watch(() => route.query.q, value => { search.value = String(value ?? '') })
</script>
<template>
  <div class="ops-breadcrumb">Bàn giao điện tử <span>/</span><b>Danh sách phiếu bàn giao</b></div>
  <div class="ops-page-heading"><div><h1>Danh sách phiếu bàn giao</h1><p>Quản lý, tra cứu và theo dõi các phiếu bàn giao tại kho.</p></div><RouterLink v-if="can('outbound.create')" class="ops-button" to="/admin/outbounds"><Plus :size="17"/> Tạo yêu cầu xuất</RouterLink></div>
  <article class="ops-panel ops-list-panel">
    <div class="ops-list-filters"><label>Kho xuất<select v-model="warehouse"><option value="">Tất cả kho</option><option v-for="name in warehouses" :key="name">{{ name }}</option></select></label><label>Trạng thái<select v-model="status"><option value="">Tất cả trạng thái</option><option value="ready_for_handover">Sẵn sàng bàn giao</option><option value="pending_confirmations">Chờ đủ xác nhận</option><option value="handed_over">Đã bàn giao</option></select></label><label class="ops-search-label">Tìm kiếm<div class="ops-search"><Search :size="17"/><input v-model="search" placeholder="Nhập mã phiếu, tên shipper…"/></div></label></div>
    <div class="ops-toolbar"><span><Filter :size="15"/> {{ filtered.length }} phiếu bàn giao</span><div><button class="ops-button secondary" :disabled="loading" @click="load"><RefreshCw :size="15"/> Làm mới</button><button class="ops-button secondary" :disabled="!filtered.length" @click="exportTasks(filtered)"><Download :size="15"/> Xuất CSV</button></div></div>
    <p v-if="error" class="ops-alert error" role="alert">{{ error }}</p><p v-if="loading" class="ops-loading">Đang tải danh sách…</p><TaskTable v-else-if="!error" :tasks="displayed"/>
    <div class="ops-pagination"><span>Hiển thị {{ filtered.length ? (page-1)*pageSize+1 : 0 }}–{{ Math.min(page*pageSize,filtered.length) }} trên {{ filtered.length }} kết quả</span><div><label>Số dòng/trang<select v-model="pageSize"><option :value="10">10</option><option :value="20">20</option><option :value="50">50</option></select></label><button class="ops-icon-button" :disabled="page <= 1" aria-label="Trang trước" @click="page--"><ChevronLeft :size="17"/></button><span class="ops-current-page">{{ page }}</span><span>/ {{ pages }}</span><button class="ops-icon-button" :disabled="page >= pages" aria-label="Trang tiếp theo" @click="page++"><ChevronRight :size="17"/></button></div></div>
  </article>
  <div class="ops-hint"><FileText :size="17"/> Mở mã phiếu để xem danh sách kiện và tiến độ xác nhận hai bên.</div>
</template>
