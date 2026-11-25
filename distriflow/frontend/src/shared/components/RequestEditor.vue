<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { Plus, Trash2, X } from 'lucide-vue-next'
import { useCatalog } from '../../features/catalog/useCatalog'
import { command } from '../api/commands'
import { api } from '../api/client'
const props = defineProps<{ kind: 'inbound' | 'outbound' }>()
const emit = defineEmits<{ saved: [id: string]; close: [] }>()
const { owners, suppliers, skus, warehouses, supplies, loading, error } = useCatalog()
const owner = ref(''); const supplier = ref(''); const warehouse = ref(''); const mode = ref('DISTRIFLOW'); const shipper = ref('')
const shippers = ref<{ id: string; name: string }[]>([])
const lines = ref([{ sku_id: '', quantity: 1 }]); const busy = ref(false); const notice = ref('')
watch(owners, value => { if (!owner.value) owner.value = value[0]?.id ?? '' })
watch(suppliers, value => { if (!supplier.value) supplier.value = value[0]?.id ?? '' })
watch(warehouses, value => { if (!warehouse.value) warehouse.value = value[0]?.id ?? '' })
const availableSkus = computed(() => skus.value.filter(sku => sku.ownerId === owner.value && (props.kind === 'outbound' || supplies.value.some(s => s.supplier_id === supplier.value && s.owner_id === owner.value && s.sku_id === sku.id))))
watch([owner, supplier], () => { lines.value = [{ sku_id: '', quantity: 1 }] })
onMounted(async () => { if (props.kind === 'outbound') { try { shippers.value = await api('/shippers') } catch (e) { notice.value = e instanceof Error ? e.message : 'Không thể tải shipper' } } })
async function save() {
  if (new Set(lines.value.map(line => line.sku_id)).size !== lines.value.length) { notice.value = 'Mỗi SKU chỉ xuất hiện một dòng.'; return }
  busy.value = true; notice.value = ''
  const body = { owner_id: owner.value, warehouse_id: warehouse.value, lines: lines.value, ...(props.kind === 'inbound' ? { supplier_id: supplier.value } : { shipper_mode: mode.value, shipper_id: mode.value === 'OWNER_ASSIGNED' ? shipper.value : '' }) }
  try { const result = await command<{ id: string }>(props.kind === 'inbound' ? '/inbound-requests' : '/outbound-requests', body); emit('saved', result.id) }
  catch (e) { notice.value = e instanceof Error ? e.message : 'Không thể tạo chứng từ' }
  finally { busy.value = false }
}
</script>
<template><div class="module-modal" role="dialog" aria-modal="true" :aria-label="kind === 'inbound' ? 'Tạo yêu cầu nhập' : 'Tạo yêu cầu xuất'"><form class="ops-panel module-editor" @submit.prevent="save"><div class="ops-panel-heading"><h2>{{ kind === 'inbound' ? 'Tạo yêu cầu nhập kho' : 'Tạo yêu cầu xuất kho' }}</h2><button type="button" class="ops-icon-button" aria-label="Đóng" :disabled="busy" @click="emit('close')"><X :size="19"/></button></div><div class="module-editor-body"><p v-if="error || notice" class="ops-alert error" role="alert">{{ error || notice }}</p><p v-if="loading">Đang tải danh mục…</p><template v-else><div class="module-fields"><label>Chủ hàng<select v-model="owner" required aria-label="Chủ hàng"><option value="">Chọn chủ hàng</option><option v-for="p in owners" :key="p.id" :value="p.id">{{ p.name }}</option></select></label><label>Kho<select v-model="warehouse" required aria-label="Kho"><option value="">Chọn kho</option><option v-for="w in warehouses" :key="w.id" :value="w.id">{{ w.name }}</option></select></label><label v-if="kind === 'inbound'">Nhà cung cấp<select v-model="supplier" required aria-label="Nhà cung cấp"><option value="">Chọn nhà cung cấp</option><option v-for="p in suppliers" :key="p.id" :value="p.id">{{ p.name }}</option></select></label><template v-else><label>Phương án nhận hàng<select v-model="mode"><option value="DISTRIFLOW">DistriFlow điều phối</option><option value="OWNER_ASSIGNED">Chủ hàng chỉ định</option></select></label><label v-if="mode === 'OWNER_ASSIGNED'">Shipper chỉ định<select v-model="shipper" required><option value="">Chọn shipper</option><option v-for="person in shippers" :key="person.id" :value="person.id">{{ person.name }}</option></select></label></template></div>
<div class="module-line-head"><h2>Chi tiết hàng hóa</h2><button type="button" class="ops-button secondary" @click="lines.push({ sku_id: '', quantity: 1 })"><Plus :size="14"/> Thêm dòng</button></div><div v-for="(line,index) in lines" :key="index" class="module-request-line"><label>SKU<select v-model="line.sku_id" required aria-label="SKU"><option value="">Chọn SKU</option><option v-for="sku in availableSkus" :key="sku.id" :value="sku.id">{{ sku.code }} · {{ sku.name }} ({{ sku.baseUnit }})</option></select></label><label>Số lượng<input v-model.number="line.quantity" type="number" min="1" max="10000000" step="1" required/></label><button class="ops-icon-button" type="button" :disabled="lines.length === 1" :aria-label="`Xóa dòng ${index+1}`" @click="lines.splice(index,1)"><Trash2 :size="16"/></button></div><p v-if="!availableSkus.length" class="module-note">Chưa có SKU hợp lệ. Kho cần khai báo SKU và quan hệ cung ứng trước.</p><p class="module-note">{{ kind === 'inbound' ? 'Tồn chỉ tăng sau khi kho kiểm nhận và xác nhận vị trí.' : 'Gửi yêu cầu chưa giữ hàng. Kho kiểm tra và giữ khi duyệt.' }}</p></template></div><div class="module-editor-footer"><button type="button" class="ops-button secondary" :disabled="busy" @click="emit('close')">Hủy</button><button class="ops-button" :disabled="busy || loading || !availableSkus.length">{{ busy ? 'Đang gửi…' : 'Gửi yêu cầu' }}</button></div></form></div></template>
