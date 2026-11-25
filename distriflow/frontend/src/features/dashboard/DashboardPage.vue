<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { FileText, ArrowRight, Package, Truck, AlertTriangle, Filter, CheckCircle2, Clock3, ChevronRight, RefreshCw, ShieldCheck } from 'lucide-vue-next'
import { auth, can } from '../../app/access'
import { api } from '../../shared/api/client'
import { useOperations } from '../handover/useOperations'
import TaskTable from '../handover/TaskTable.vue'
import FlowChart from './FlowChart.vue'
const { tasks, loading, error, load } = useOperations()
const flow = ref<{ date: string; quantity: number }[]>([])
const source = ref(''); const generatedAt = ref('')
async function loadFlow() {
  try { const data = await api<{ flow: typeof flow.value; dataSource: { storage: string; generatedAt: string } }>('/dashboard'); flow.value = data.flow; source.value = data.dataSource.storage; generatedAt.value = new Date(data.dataSource.generatedAt).toLocaleString('vi-VN') }
  catch (e) { error.value = e instanceof Error ? e.message : 'Không thể tải biểu đồ' }
}
async function refresh() { await Promise.all([load(), loadFlow()]) }
onMounted(loadFlow)
const totalPackages = computed(() => tasks.value.reduce((sum, task) => sum + task.packages.length, 0))
const pending = computed(() => tasks.value.filter(task => task.status === 'pending_confirmations'))
const done = computed(() => tasks.value.filter(task => task.status === 'handed_over'))
const awaiting = computed(() => tasks.value.filter(task => !task.shipperAccepted && task.status === 'ready_for_handover'))
const breakdown = computed(() => [
  { name: 'Đang đối chiếu', value: tasks.value.filter(t => t.status === 'ready_for_handover' && !!t.shipperId).length, color: '#2563eb' },
  { name: 'Đã bàn giao', value: done.value.length, color: '#10b981' },
  { name: 'Chờ xác nhận', value: pending.value.length, color: '#8b5cf6' },
  { name: 'Chưa phân công', value: tasks.value.filter(t => !t.shipperId && t.status === 'ready_for_handover').length, color: '#f59e0b' },
])
const donut = computed(() => {
  let offset = 0
  return 'conic-gradient(' + breakdown.value.map(item => {
    const start = offset; offset += tasks.value.length ? item.value / tasks.value.length * 100 : 0
    return `${item.color} ${start}% ${offset}%`
  }).join(',') + ')'
})
const ratio = (n: number) => tasks.value.length ? Math.round(n / tasks.value.length * 100) : 0
</script>
<template>
  <div class="df-dashboard">
    <div class="df-dashboard-heading"><div><p>Xin chào, {{ auth.user?.username }}!</p><h2>Tình hình vận hành</h2></div><div class="ops-actions"><span class="ops-button secondary df-period"><Filter :size="15"/> 30 ngày qua</span><RouterLink class="ops-button" to="/admin/handovers"><FileText :size="16"/> Phiếu bàn giao</RouterLink></div></div>
    <p v-if="error" class="ops-alert error" role="alert">{{ error }}</p>
    <p v-if="source" class="df-subtitle">Nguồn: {{ source === 'postgresql' ? 'PostgreSQL' : source }} · Cập nhật {{ generatedAt }} · KPI: toàn bộ phiếu trong kho, biểu đồ: 30 ngày.</p>
    <p v-if="!loading && !error && !tasks.length" class="ops-alert">Chưa có dữ liệu bàn giao. <RouterLink v-if="can('catalog.manage')" to="/admin/catalog">Khai báo kho và nhập dữ liệu thật</RouterLink>. Không hiển thị dữ liệu mẫu.</p>
    <p v-if="loading" class="ops-loading">Đang tải dữ liệu vận hành…</p>
    <template v-else-if="!error">
      <div class="df-kpi-grid">
        <RouterLink to="/admin/handovers" class="df-kpi tone-blue"><div class="df-kpi-top"><span class="df-kpi-icon"><FileText :size="19"/></span><span class="df-kpi-chip">Tổng hiện có</span></div><p>Phiếu bàn giao</p><strong>{{ tasks.length.toLocaleString('vi-VN') }}</strong><div class="df-kpi-bar"><i :style="{ width: tasks.length ? '100%' : '0%' }"/></div></RouterLink>
        <RouterLink to="/admin/handovers" class="df-kpi tone-violet"><div class="df-kpi-top"><span class="df-kpi-icon"><Package :size="19"/></span><span class="df-kpi-chip">Tại kho</span></div><p>Kiện hàng quản lý</p><strong>{{ totalPackages.toLocaleString('vi-VN') }}</strong><div class="df-kpi-bar"><i :style="{ width: totalPackages ? '100%' : '0%' }"/></div></RouterLink>
        <RouterLink to="/admin/handovers?status=handed_over" class="df-kpi tone-emerald"><div class="df-kpi-top"><span class="df-kpi-icon"><Truck :size="19"/></span><span class="df-kpi-chip">{{ done.length }} phiếu</span></div><p>Tỷ lệ hoàn tất bàn giao</p><strong>{{ ratio(done.length) }}%</strong><div class="df-kpi-bar"><i :style="{ width: ratio(done.length) + '%' }"/></div></RouterLink>
        <RouterLink to="/admin/handovers?status=pending_confirmations" class="df-kpi tone-amber"><div class="df-kpi-top"><span class="df-kpi-icon"><AlertTriangle :size="19"/></span><span class="df-kpi-chip">Cần xử lý</span></div><p>Chờ xác nhận kho</p><strong>{{ pending.length.toLocaleString('vi-VN') }}</strong><div class="df-kpi-bar"><i :style="{ width: ratio(pending.length) + '%' }"/></div></RouterLink>
      </div>
      <div class="df-chart-grid">
        <section class="ops-panel df-flow-panel"><div class="ops-panel-heading"><div><h2>Luồng bàn giao tại kho</h2><p class="df-subtitle">Số kiện đã hoàn tất trong 30 ngày gần nhất</p></div><button class="ops-icon-button" aria-label="Làm mới dữ liệu" @click="refresh"><RefreshCw :size="16"/></button></div><div class="df-chart-legend"><span><i style="background:#2563eb"/> Kiện đã bàn giao</span></div><FlowChart :flow="flow"/></section>
        <section class="ops-panel df-allocation-panel"><div class="ops-panel-heading"><div><h2>Phân bổ phiếu bàn giao</h2><p class="df-subtitle">Theo trạng thái xử lý tại kho</p></div></div><div class="df-donut-wrap"><div class="df-donut" :style="{ background: tasks.length ? donut : '#e2e8f0' }"/><div class="df-donut-center"><b>{{ tasks.length.toLocaleString('vi-VN') }}</b><small>phiếu đang quản lý</small></div></div><div class="df-allocation-legend"><div v-for="item in breakdown" :key="item.name"><i :style="{ background: item.color }"/><span>{{ item.name }}</span><b>{{ ratio(item.value) }}%</b></div></div></section>
      </div>
      <div class="df-bottom-grid">
        <section class="ops-panel df-recent-panel"><div class="ops-panel-heading"><div><h2>Phiếu bàn giao hiện tại</h2><p class="df-subtitle">Dữ liệu trong phạm vi kho của bạn</p></div><RouterLink to="/admin/handovers" class="ops-text-link">Xem tất cả <ArrowRight :size="14"/></RouterLink></div><TaskTable :tasks="tasks.slice(0, 5)"/></section>
        <section class="ops-panel df-attention-panel"><div class="ops-panel-heading"><div><h2>Công việc cần xử lý</h2><p class="df-subtitle">Theo dõi để bàn giao thông suốt</p></div><span class="df-alert-count">{{ pending.length + awaiting.length }} công việc</span></div><div class="df-attention-list"><RouterLink v-for="task in pending.slice(0,2)" :key="task.id" :to="`/admin/handovers/${task.id}`" class="df-attention-item"><span class="df-attention-icon amber"><AlertTriangle :size="17"/></span><span><b>{{ task.code }}</b><small>{{ task.packages.length }} kiện chờ kho xác nhận</small></span><ChevronRight :size="14"/></RouterLink><RouterLink v-for="task in awaiting.slice(0,3)" :key="task.id" :to="`/admin/handovers/${task.id}`" class="df-attention-item"><span class="df-attention-icon violet"><Clock3 :size="17"/></span><span><b>{{ task.code }}</b><small>Chờ {{ task.shipperName }} nhận nhiệm vụ</small></span><ChevronRight :size="14"/></RouterLink><div v-if="!pending.length && !awaiting.length" class="df-attention-empty"><CheckCircle2 :size="28"/><b>Không có công việc tồn đọng</b><span>Các phiếu hiện đã được xử lý.</span></div></div><div class="df-panel-note"><ShieldCheck :size="14"/> Chỉ hoàn tất khi hai bên cùng xác nhận</div></section>
      </div>
    </template>
  </div>
</template>
