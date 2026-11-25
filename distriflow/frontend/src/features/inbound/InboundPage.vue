<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { Plus, RefreshCw } from 'lucide-vue-next'
import { can } from '../../app/access'
import type { StockDocument } from '../../shared/types/documents'
import { api } from '../../shared/api/client'
import type { Location } from '../catalog/api'
import { getInbounds, inboundCommand } from './api'
import RequestEditor from '../../shared/components/RequestEditor.vue'
import DocumentList from '../../shared/components/DocumentList.vue'
import StatusBadge from '../../shared/components/StatusBadge.vue'
const documents = ref<StockDocument[]>([]); const selectedId = ref(''); const selected = computed(() => documents.value.find(doc => doc.id === selectedId.value))
const locations = ref<Location[]>([]); const locationId = ref(''); const loading = ref(true); const busy = ref(false); const notice = ref(''); const creating = ref(false)
const good = ref<Record<string, number>>({}); const quarantined = ref<Record<string, number>>({}); const note = ref('')
watch(selected, doc => { good.value = Object.fromEntries(doc?.lines.map(line => [line.id, line.quantity]) ?? []); quarantined.value = Object.fromEntries(doc?.lines.map(line => [line.id, 0]) ?? []); note.value = ''; locationId.value = '' })
async function load() {
  loading.value = true
  try { [documents.value, locations.value] = await Promise.all([getInbounds(), api<Location[]>('/locations')]); if (!documents.value.some(doc => doc.id === selectedId.value)) selectedId.value = documents.value[0]?.id ?? '' }
  catch (e) { notice.value = e instanceof Error ? e.message : 'Không thể tải yêu cầu' }
  finally { loading.value = false }
}
async function perform(action: 'review' | 'receive' | 'putaway', accepted = true) {
  if (!selected.value || busy.value) return
  busy.value = true; notice.value = ''
  const payload = { version: selected.value.version, ...(action === 'review' ? { accepted, note: note.value } : action === 'receive' ? { note: note.value, lines: selected.value.lines.map(line => ({ line_id: line.id, good: Number(good.value[line.id]), quarantined: Number(quarantined.value[line.id]) })) } : { location_id: locationId.value }) }
  try { await inboundCommand(selected.value.id, action, payload); await load(); notice.value = 'Đã cập nhật yêu cầu nhập kho.' }
  catch (e) { notice.value = e instanceof Error ? e.message : 'Chưa xác định kết quả; hãy tải lại.' }
  finally { busy.value = false }
}
async function saved(id: string) { creating.value = false; selectedId.value = id; await load(); notice.value = 'Đã gửi yêu cầu nhập.' }
onMounted(load)
</script>
<template><div class="ops-page-heading"><div><h1>Nhập kho</h1><p>Tạo yêu cầu, kiểm nhận hàng và ghi nhận vị trí lưu kho.</p></div><div class="ops-actions"><button class="ops-button secondary" :disabled="loading || busy" @click="load"><RefreshCw :size="15"/> Làm mới</button><button v-if="can('inbound.create')" class="ops-button" @click="creating = true"><Plus :size="16"/> Tạo yêu cầu nhập</button></div></div><p v-if="notice" class="ops-alert" role="status">{{ notice }}</p><p v-if="loading" class="ops-loading">Đang tải yêu cầu nhập…</p><template v-else><DocumentList :documents="documents" :selected-id="selectedId" @select="selectedId = $event"/>
<section v-if="selected" class="ops-panel module-detail"><div class="ops-panel-heading"><div><h2>{{ selected.code }}</h2><p class="df-subtitle">{{ selected.supplierName }} → {{ selected.ownerName }} · {{ selected.warehouseName }}</p></div><StatusBadge :status="selected.status"/></div><div class="ops-table-wrap"><table class="ops-table"><thead><tr><th>SKU</th><th>Đơn vị</th><th>Kế hoạch</th><th>Đạt</th><th>Cách ly</th></tr></thead><tbody><tr v-for="line in selected.lines" :key="line.id"><td>{{ line.skuCode }} · {{ line.skuName }}</td><td>{{ line.unit }}</td><td>{{ line.quantity }}</td><td><input v-if="can('inbound.manage') && selected.status === 'approved'" v-model.number="good[line.id]" :aria-label="`Lượng đạt ${line.skuCode}`" type="number" min="0" :max="line.quantity" class="module-quantity"/><template v-else>{{ line.good ?? 0 }}</template></td><td><input v-if="can('inbound.manage') && selected.status === 'approved'" v-model.number="quarantined[line.id]" :aria-label="`Lượng cách ly ${line.skuCode}`" type="number" min="0" :max="line.quantity" class="module-quantity"/><template v-else>{{ line.quarantined ?? 0 }}</template></td></tr></tbody></table></div>
<div v-if="can('inbound.manage')" class="module-workflow"><label v-if="['submitted','approved'].includes(selected.status)">Ghi chú / lý do chênh lệch<textarea v-model="note" maxlength="1000" placeholder="Bắt buộc khi từ chối hoặc có hàng thiếu/cách ly"/></label><label v-if="selected.status === 'received'">Vị trí lưu kho<select v-model="locationId" aria-label="Vị trí lưu kho"><option value="">Chọn vị trí</option><option v-for="l in locations.filter(l => l.warehouseId === selected?.warehouseId)" :key="l.id" :value="l.id">{{ l.code }}</option></select></label><div class="ops-actions"><template v-if="selected.status === 'submitted'"><button class="ops-button" :disabled="busy" @click="perform('review')">Duyệt nhập</button><button class="ops-button secondary" :disabled="busy || !note.trim()" @click="perform('review',false)">Từ chối</button></template><button v-if="selected.status === 'approved'" class="ops-button" :disabled="busy" @click="perform('receive')">Ghi nhận kiểm nhận</button><button v-if="selected.status === 'received'" class="ops-button" :disabled="busy || !locationId" @click="perform('putaway')">Xác nhận vị trí & tăng tồn</button></div></div><p v-if="selected.note" class="module-note module-pad">Ghi chú: {{ selected.note }}</p></section></template><RequestEditor v-if="creating" kind="inbound" @close="creating = false" @saved="saved"/></template>
