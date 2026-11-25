<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, Printer, Warehouse, Truck, Package, ShieldCheck, Check, AlertTriangle, UserRound } from 'lucide-vue-next'
import { can } from '../../app/access'
import { api } from '../../shared/api/client'
import { command } from '../../shared/api/commands'
import { useOperations } from './useOperations'
import StatusBadge from '../../shared/components/StatusBadge.vue'
const route = useRoute()
const { tasks, loading, error, load } = useOperations()
const task = computed(() => tasks.value.find(item => item.id === route.params.id))
const busy = ref(false); const notice = ref(''); const search = ref('')
const packages = computed(() => task.value?.packages.filter(code => code.toLowerCase().includes(search.value.toLowerCase())) ?? [])
const steps = computed(() => [{ label: 'Chuẩn bị tại kho', done: true }, { label: 'Shipper nhận nhiệm vụ', done: !!task.value?.shipperAccepted }, { label: 'Đối chiếu & nhận hàng', done: task.value?.status !== 'ready_for_handover' }, { label: 'Kho xác nhận bàn giao', done: task.value?.status === 'handed_over' }])
async function confirm() {
  if (!task.value || busy.value || !window.confirm('Xác nhận bàn giao toàn bộ kiện? Thao tác sẽ ghi xuất tồn kho và tạo biên nhận.')) return
  busy.value = true; notice.value = ''
  try { await command(`/pickup-tasks/${task.value.id}/warehouse-confirm`, { version: task.value.version }); await load(); notice.value = 'Đã hoàn tất bàn giao và ghi nhận xuất kho.' }
  catch (e) { notice.value = e instanceof Error ? e.message : 'Chưa xác định kết quả, hãy tải lại để kiểm tra.' }
  finally { busy.value = false }
}
function printDocument() { window.print() }
async function downloadReceipt() {
  if (!task.value || busy.value) return
  busy.value = true
  try {
    const receipt = await api(`/pickup-tasks/${task.value.id}/receipt`)
    const url = URL.createObjectURL(new Blob([JSON.stringify(receipt, null, 2)], { type: 'application/json' }))
    const link = document.createElement('a')
    link.href = url; link.download = `bien-nhan-${task.value.code}.json`; link.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  } catch (e) { notice.value = e instanceof Error ? e.message : 'Không tải được biên nhận.' }
  finally { busy.value = false }
}
</script>
<template>
  <div class="ops-breadcrumb"><RouterLink to="/admin/handovers"><ArrowLeft :size="14"/> Bàn giao điện tử</RouterLink><span>/</span><b>{{ task?.code ?? 'Chi tiết phiếu' }}</b></div>
  <p v-if="loading" class="ops-loading">Đang tải chi tiết phiếu…</p><p v-else-if="error" role="alert" class="ops-alert error">{{ error }}</p><article v-else-if="!task" class="ops-panel ops-empty">Không tìm thấy phiếu trong phạm vi được cấp quyền.</article>
  <template v-else>
    <div class="ops-page-heading"><div><h1>Chi tiết phiếu bàn giao</h1><div class="ops-title-tags"><span class="ops-document-code">{{ task.code }}</span><StatusBadge :status="task.status"/></div></div><div class="ops-actions"><RouterLink class="ops-button secondary" to="/admin/handovers"><ArrowLeft :size="16"/> Quay lại</RouterLink><button class="ops-button secondary" @click="printDocument"><Printer :size="16"/> In chi tiết</button></div></div>
    <p v-if="notice" role="status" class="ops-alert">{{ notice }}</p>
    <p v-if="task.receiptId"><button class="ops-button secondary" :disabled="busy" @click="downloadReceipt">Tải biên nhận JSON</button></p>
    <div class="ops-metadata ops-panel"><div><Warehouse :size="23"/><span><small>Kho xuất</small><b>{{ task.warehouseName }}</b></span></div><div><Truck :size="23"/><span><small>Người nhận hàng</small><b>{{ task.shipperName }}</b></span></div><div><Package :size="23"/><span><small>Số kiện bàn giao</small><b>{{ task.packages.length }} kiện</b></span></div><div><ShieldCheck :size="23"/><span><small>Phiên bản hiện tại</small><b>Phiên {{ task.version }}</b></span></div></div>
    <div class="ops-detail-grid"><article class="ops-panel"><div class="ops-panel-heading"><h2>Danh sách kiện ({{ task.packages.length }})</h2><input v-model="search" class="ops-compact-input" aria-label="Tìm mã kiện" placeholder="Tìm mã kiện…"/></div><div class="ops-table-wrap"><table class="ops-table"><thead><tr><th>Mã kiện</th><th>Trạng thái đối chiếu</th><th>Ghi chú</th></tr></thead><tbody><tr v-for="code in packages" :key="code"><td class="ops-package-code">{{ code }}</td><td><span class="ops-pill" :class="task.scannedCodes.includes(code) ? 'green' : 'amber'">{{ task.scannedCodes.includes(code) ? 'Đã đối chiếu' : 'Chưa đối chiếu' }}</span></td><td>{{ task.scannedCodes.includes(code) ? 'Đã xác minh tại kho' : 'Chờ shipper quét mã' }}</td></tr><tr v-if="!packages.length"><td colspan="3" class="ops-empty">Không tìm thấy kiện.</td></tr></tbody></table></div></article>
      <article class="ops-panel"><div class="ops-panel-heading"><h2>Tổng hợp đối chiếu</h2></div><div class="ops-reconcile"><p><span><Package :size="16"/> Tổng số kiện</span><b>{{ task.packages.length }}</b></p><p><span><Check :size="16" class="text-green"/> Đã đối chiếu</span><b>{{ task.scannedCodes.length }}</b></p><p><span><AlertTriangle :size="16" class="text-amber"/> Chưa đối chiếu</span><b>{{ task.packages.length-task.scannedCodes.length }}</b></p></div><div class="ops-callout" :class="{ complete: task.status === 'handed_over' }"><ShieldCheck :size="21"/><div><b>{{ task.status === 'handed_over' ? 'Bàn giao hoàn tất' : 'Kiểm tra trước khi bàn giao' }}</b><p>{{ task.status === 'handed_over' ? 'Hai bên đã xác nhận. Hệ thống đã ghi xuất và tạo biên nhận.' : 'Cần đối chiếu đủ kiện và xác nhận của cả kho lẫn shipper.' }}</p></div></div></article></div>
    <article class="ops-panel ops-timeline-panel"><h2>Tiến độ xử lý</h2><ol class="ops-timeline"><li v-for="(step, index) in steps" :key="step.label" :class="{ done: step.done }"><span><Check v-if="step.done" :size="15"/><template v-else>{{ index+1 }}</template></span><b>{{ step.label }}</b><small>{{ step.done ? 'Đã ghi nhận' : 'Chờ thực hiện' }}</small></li></ol></article>
    <div class="ops-confirm-grid"><article class="ops-panel ops-confirm"><h2><Warehouse :size="22"/> Xác nhận của kho</h2><p>Trạng thái: <b>{{ task.status === 'handed_over' ? 'Đã xác nhận' : 'Chưa xác nhận' }}</b></p><button v-if="can('handover.confirm')" class="ops-button" :disabled="busy || task.status !== 'pending_confirmations'" @click="confirm"><ShieldCheck :size="17"/> {{ busy ? 'Đang xác nhận…' : 'Xác nhận tại kho' }}</button><small v-if="task.status === 'ready_for_handover'">Chờ shipper đối chiếu và xác nhận nhận hàng.</small><small v-else-if="!can('handover.confirm')">Tài khoản chưa được cấp quyền xác nhận kho.</small></article><article class="ops-panel ops-confirm"><h2><UserRound :size="22"/> Xác nhận của shipper</h2><p>Người nhận: <b>{{ task.shipperName }}</b></p><span class="ops-pill" :class="task.status !== 'ready_for_handover' ? 'green' : 'amber'">{{ task.status !== 'ready_for_handover' ? 'Đã xác nhận nhận hàng' : 'Chưa xác nhận nhận hàng' }}</span><small>Shipper xác nhận trực tiếp từ tài khoản được phân công.</small></article></div>
  </template>
</template>
