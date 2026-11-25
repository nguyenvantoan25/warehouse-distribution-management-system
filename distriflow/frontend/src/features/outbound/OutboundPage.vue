<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { Plus, RefreshCw } from 'lucide-vue-next'
import { can } from '../../app/access'
import type { StockDocument } from '../../shared/types/documents'
import { getOutbounds, outboundCommand } from './api'
import RequestEditor from '../../shared/components/RequestEditor.vue'
import DocumentList from '../../shared/components/DocumentList.vue'
import StatusBadge from '../../shared/components/StatusBadge.vue'
const documents = ref<StockDocument[]>([]); const selectedId = ref(''); const selected = computed(() => documents.value.find(doc => doc.id === selectedId.value))
const loading = ref(true); const busy = ref(false); const notice = ref(''); const creating = ref(false); const packageCount = ref(1)
async function load() {
  loading.value = true
  try { documents.value = await getOutbounds(); if (!documents.value.some(doc => doc.id === selectedId.value)) selectedId.value = documents.value[0]?.id ?? '' }
  catch (e) { notice.value = e instanceof Error ? e.message : 'Không thể tải yêu cầu' }
  finally { loading.value = false }
}
async function perform(action: 'approve' | 'pick' | 'pack' | 'cancel') {
  if (!selected.value || busy.value) return
  if (action === 'cancel' && !window.confirm('Hủy yêu cầu xuất này? Lượng hàng đang giữ sẽ được giải phóng.')) return
  busy.value = true; notice.value = ''
  try { await outboundCommand(selected.value.id, action, { version: selected.value.version, ...(action === 'pack' ? { package_count: Number(packageCount.value) } : {}) }); await load(); notice.value = 'Đã cập nhật yêu cầu xuất kho.' }
  catch (e) { notice.value = e instanceof Error ? e.message : 'Chưa xác định kết quả; hãy tải lại.' }
  finally { busy.value = false }
}
async function saved(id: string) { creating.value = false; selectedId.value = id; await load(); notice.value = 'Đã gửi yêu cầu xuất. Hàng chưa được giữ cho tới khi kho duyệt.' }
onMounted(load)
</script>
<template><div class="ops-page-heading"><div><h1>Yêu cầu xuất kho</h1><p>Duyệt giữ hàng, soạn và đóng kiện trước khi bàn giao.</p></div><div class="ops-actions"><button class="ops-button secondary" :disabled="loading || busy" @click="load"><RefreshCw :size="15"/> Làm mới</button><button v-if="can('outbound.create')" class="ops-button" @click="creating = true"><Plus :size="16"/> Tạo yêu cầu xuất</button></div></div><p v-if="notice" class="ops-alert" role="status">{{ notice }}</p><p v-if="loading" class="ops-loading">Đang tải yêu cầu xuất…</p><template v-else><DocumentList :documents="documents" :selected-id="selectedId" @select="selectedId = $event"/><section v-if="selected" class="ops-panel module-detail"><div class="ops-panel-heading"><div><h2>{{ selected.code }}</h2><p class="df-subtitle">{{ selected.ownerName }} · {{ selected.warehouseName }} · {{ selected.shipperMode === 'OWNER_ASSIGNED' ? 'Chủ hàng chỉ định shipper' : 'DistriFlow điều phối' }}</p></div><StatusBadge :status="selected.status"/></div><div class="ops-table-wrap"><table class="ops-table"><thead><tr><th>SKU</th><th>Tên hàng</th><th>Số lượng</th><th>Đơn vị</th></tr></thead><tbody><tr v-for="line in selected.lines" :key="line.id"><td>{{ line.skuCode }}</td><td>{{ line.skuName }}</td><td>{{ line.quantity }}</td><td>{{ line.unit }}</td></tr></tbody></table></div><div class="module-workflow"><div v-if="can('outbound.manage') && selected.status === 'picked'" class="module-fields"><label>Số kiện đóng gói<input v-model.number="packageCount" type="number" min="1" max="100"/></label></div><div class="ops-actions"><template v-if="can('outbound.manage')"><button v-if="selected.status === 'submitted'" class="ops-button" :disabled="busy" @click="perform('approve')">Duyệt & giữ hàng</button><button v-if="selected.status === 'approved'" class="ops-button" :disabled="busy" @click="perform('pick')">Xác nhận soạn xong</button><button v-if="selected.status === 'picked'" class="ops-button" :disabled="busy || packageCount < 1" @click="perform('pack')">Đóng kiện & tạo nhiệm vụ</button></template><button v-if="can('outbound.cancel') && ['submitted','approved'].includes(selected.status)" class="ops-button secondary" :disabled="busy" @click="perform('cancel')">Hủy yêu cầu</button><RouterLink v-if="selected.taskId && can('tasks.read')" class="ops-button secondary" :to="`/admin/handovers/${selected.taskId}`">Xem phiếu bàn giao</RouterLink></div><p v-if="selected.status === 'packed'" class="module-note">Đã đóng kiện; tồn ghi sổ chưa giảm. Chỉ ghi xuất sau khi kho và shipper xác nhận bàn giao.</p><p v-if="selected.status === 'handed_over'" class="module-note">Đã bàn giao và ghi xuất hàng thành công.</p></div></section></template><RequestEditor v-if="creating" kind="outbound" @close="creating = false" @saved="saved"/></template>
