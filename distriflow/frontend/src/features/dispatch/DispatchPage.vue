<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Truck, Search, ArrowRight, CheckCircle2, Info, RefreshCw } from 'lucide-vue-next'
import { api } from '../../shared/api/client'
import { command } from '../../shared/api/commands'
import { useOperations } from '../handover/useOperations'
const { tasks, loading, error, load } = useOperations()
const shippers = ref<{ id: string; name: string }[]>([])
const shipperId = ref(''); const selected = ref<string[]>([]); const search = ref(''); const busy = ref(false); const notice = ref('')
const eligible = computed(() => tasks.value.filter(task => task.status === 'ready_for_handover' && !task.shipperAccepted && task.code.toLowerCase().includes(search.value.toLowerCase())))
const chosen = computed(() => tasks.value.filter(task => selected.value.includes(task.id)))
const assigned = computed(() => tasks.value.filter(task => task.shipperId))
const allSelected = computed(() => !!eligible.value.length && eligible.value.every(task => selected.value.includes(task.id)))
function toggleAll() { selected.value = allSelected.value ? [] : eligible.value.map(task => task.id) }
onMounted(async () => { try { shippers.value = await api('/shippers') } catch (e) { notice.value = e instanceof Error ? e.message : 'Không thể tải danh sách shipper' } })
async function assign() {
  if (!shipperId.value || !chosen.value.length || busy.value) return
  busy.value = true; notice.value = ''
  let success = 0
  const failures: string[] = []
  for (const task of chosen.value) {
    try { await command(`/pickup-tasks/${task.id}/assign`, { version: task.version, shipper_id: shipperId.value }); success++ }
    catch (e) { failures.push(`${task.code}: ${e instanceof Error ? e.message : 'Chưa xác định kết quả'}`) }
  }
  await load(); selected.value = []; busy.value = false
  notice.value = `Đã ghi nhận ${success} phiếu. ${failures.join(' · ')}`
}
</script>
<template>
  <div class="ops-breadcrumb">Điều phối vận chuyển <span>/</span><b>Phân bổ nhiệm vụ</b></div><div class="ops-page-heading"><div><h1>Phân bổ vận chuyển</h1><p>Chọn shipper nhận hàng tại kho cho các phiếu chưa được tiếp nhận.</p></div><button class="ops-button secondary" :disabled="loading || busy" @click="load"><RefreshCw :size="16"/> Làm mới</button></div>
  <p v-if="error" class="ops-alert error" role="alert">{{ error }}</p><p v-if="notice" class="ops-alert" role="status">{{ notice }}</p><p v-if="loading" class="ops-loading">Đang tải danh sách phiếu…</p>
  <div v-else class="ops-dispatch-grid"><article class="ops-panel"><div class="ops-panel-heading"><h2>Phiếu có thể phân bổ <span class="ops-count blue">{{ eligible.length }}</span></h2></div><div class="ops-search ops-dispatch-search"><Search :size="16"/><input v-model="search" placeholder="Nhập mã phiếu…" aria-label="Tìm phiếu phân bổ"/></div>
    <div class="ops-table-wrap ops-dispatch-table"><table class="ops-table"><thead><tr><th><input type="checkbox" :checked="allSelected" :disabled="busy || !eligible.length" aria-label="Chọn tất cả" @change="toggleAll"/></th><th>Mã phiếu</th><th>Kho xuất</th><th class="numeric">Số kiện</th></tr></thead><tbody><tr v-for="task in eligible" :key="task.id" :class="{ 'row-selected': selected.includes(task.id) }"><td><input v-model="selected" :value="task.id" type="checkbox" :disabled="busy" :aria-label="`Chọn ${task.code}`"/></td><td><RouterLink class="ops-code" :to="`/admin/handovers/${task.id}`">{{ task.code }}</RouterLink></td><td>{{ task.warehouseName }}</td><td class="numeric">{{ task.packages.length }}</td></tr><tr v-if="!eligible.length"><td colspan="4" class="ops-empty">Không có phiếu chưa được tiếp nhận phù hợp.</td></tr></tbody></table></div>
    <div class="ops-selection-summary"><span>Đã chọn <b>{{ chosen.length }}</b> phiếu ({{ chosen.reduce((sum, task) => sum + task.packages.length, 0) }} kiện)</span><ArrowRight :size="19"/></div>
  </article><div class="ops-dispatch-side"><article class="ops-panel"><div class="ops-panel-heading"><h2><Truck :size="19"/> Thông tin phân bổ</h2></div><form class="ops-dispatch-form" @submit.prevent="assign"><label for="shipper">Shipper nhận hàng <span class="text-red">*</span></label><select id="shipper" v-model="shipperId" required :disabled="busy"><option value="">Chọn shipper trong phạm vi kho</option><option v-for="shipper in shippers" :key="shipper.id" :value="shipper.id">{{ shipper.name }}</option></select><div class="ops-form-summary"><div><small>Số phiếu đã chọn</small><b>{{ chosen.length }}</b></div><div><small>Tổng số kiện</small><b>{{ chosen.reduce((sum, task) => sum + task.packages.length, 0) }}</b></div></div><div class="ops-callout"><Info :size="19"/><p>Chỉ được đổi phân công khi shipper chưa nhận nhiệm vụ. Mọi lựa chọn được kiểm tra theo phạm vi kho.</p></div><div class="ops-actions"><button class="ops-button" :disabled="busy || !chosen.length || !shipperId"><CheckCircle2 :size="17"/> {{ busy ? 'Đang phân bổ…' : 'Xác nhận phân bổ' }}</button><button class="ops-button secondary" type="button" :disabled="busy" @click="selected = []; shipperId = ''">Bỏ chọn</button></div></form></article>
    <article class="ops-panel"><div class="ops-panel-heading"><h2>Phân công hiện tại</h2><span class="ops-count blue">{{ assigned.length }}</span></div><div class="ops-table-wrap"><table class="ops-table"><thead><tr><th>Mã phiếu</th><th>Shipper</th><th>Nhiệm vụ</th></tr></thead><tbody><tr v-for="task in assigned.slice(0, 6)" :key="task.id"><td><RouterLink class="ops-code" :to="`/admin/handovers/${task.id}`">{{ task.code }}</RouterLink></td><td>{{ task.shipperName }}</td><td>{{ task.shipperAccepted ? 'Đã nhận' : 'Chờ nhận' }}</td></tr><tr v-if="!assigned.length"><td colspan="3" class="ops-empty">Chưa có phân công.</td></tr></tbody></table></div></article></div></div>
</template>
