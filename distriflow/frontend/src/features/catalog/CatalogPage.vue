<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Plus, RefreshCw } from 'lucide-vue-next'
import { useCatalog } from './useCatalog'
import { createCatalogRecord } from './api'
import { can } from '../../app/access'
const route = useRoute()
const { partners, skus, warehouses, locations, supplies, owners, suppliers, loading, error, load } = useCatalog()
const section = ref(route.path.includes('partners') ? 'partners' : 'skus')
watch(() => route.path, path => { section.value = path.includes('partners') ? 'partners' : 'skus' })
const notice = ref(''); const busy = ref(false); const search = ref('')
const form = reactive({ name: '', kind: 'SUPPLIER', code: '', owner_id: '', supplier_id: '', sku_id: '', base_unit: '', warehouse_id: '' })
const tabs = [{ id: 'warehouses', label: 'Kho' }, { id: 'partners', label: 'Đối tác' }, { id: 'skus', label: 'SKU & đơn vị tính' }, { id: 'locations', label: 'Vị trí kho' }, { id: 'supplies', label: 'Quan hệ cung ứng' }]
const nameOf = (id: string) => partners.value.find(p => p.id === id)?.name ?? id
const rows = computed(() => {
  const values = section.value === 'partners' ? partners.value.map(p => [p.name, p.kind === 'SUPPLIER' ? 'Nhà cung cấp' : 'Chủ hàng', p.active ? 'Hoạt động' : 'Đã khóa']) : section.value === 'skus' ? skus.value.map(s => [s.code, s.name, s.baseUnit, nameOf(s.ownerId)]) : section.value === 'locations' ? locations.value.map(l => [l.code, warehouses.value.find(w => w.id === l.warehouseId)?.name ?? l.warehouseId]) : supplies.value.map(s => [nameOf(s.supplier_id), nameOf(s.owner_id), skus.value.find(k => k.id === s.sku_id)?.code ?? s.sku_id])
  const visible = section.value === 'warehouses' ? warehouses.value.map(w => [w.name, w.id]) : values
  return visible.filter(row => row.join(' ').toLowerCase().includes(search.value.toLowerCase()))
})
const columns = computed(() => section.value === 'warehouses' ? ['Tên kho', 'ID kho'] : section.value === 'partners' ? ['Tên đối tác', 'Loại', 'Trạng thái'] : section.value === 'skus' ? ['Mã SKU', 'Tên hàng', 'Đơn vị', 'Chủ hàng'] : section.value === 'locations' ? ['Mã vị trí', 'Kho'] : ['Nhà cung cấp', 'Chủ hàng', 'SKU'])
async function save() {
  busy.value = true; notice.value = ''
  const path = section.value === 'supplies' ? '/supply-relationships' : `/${section.value}`
  const payload = section.value === 'warehouses' ? { name: form.name } : section.value === 'partners' ? { name: form.name, kind: form.kind } : section.value === 'skus' ? { code: form.code, name: form.name, base_unit: form.base_unit, owner_id: form.owner_id } : section.value === 'locations' ? { warehouse_id: form.warehouse_id, code: form.code } : { supplier_id: form.supplier_id, owner_id: form.owner_id, sku_id: form.sku_id }
  try { await createCatalogRecord(path, payload); await load(); notice.value = 'Đã lưu danh mục vào cơ sở dữ liệu.'; form.name = ''; form.code = '' }
  catch (e) { notice.value = e instanceof Error ? e.message : 'Không thể lưu danh mục' }
  finally { busy.value = false }
}
</script>
<template><div class="ops-page-heading"><div><h1>Danh mục & đối tác</h1><p>Quản lý chủ hàng, nhà cung cấp và danh mục hàng hóa dùng chung.</p></div><button class="ops-button secondary" :disabled="loading || busy" @click="load"><RefreshCw :size="15"/> Làm mới</button></div>
<div class="module-tabs"><button v-for="tab in tabs" :key="tab.id" :class="{ active: section === tab.id }" @click="section = tab.id; search = ''">{{ tab.label }}</button></div>
<p v-if="!loading && !warehouses.length && can('catalog.manage')" class="ops-alert">Chưa có kho được gán. <button class="ops-text-link" @click="section = 'warehouses'">Khai báo kho thật trước</button>. Sau đó gán tài khoản ở mục Tài khoản & phạm vi.</p>
<p v-if="error" class="ops-alert error" role="alert">{{ error }}</p><p v-if="notice" class="ops-alert" role="status">{{ notice }}</p><p v-if="loading" class="ops-loading">Đang tải danh mục…</p>
<div v-else class="module-grid"><section class="ops-panel"><div class="ops-panel-heading"><h2>{{ tabs.find(t => t.id === section)?.label }} ({{ rows.length }})</h2><input v-model="search" class="ops-compact-input" placeholder="Tìm kiếm…" aria-label="Tìm danh mục"/></div><div class="ops-table-wrap"><table class="ops-table"><thead><tr><th v-for="column in columns" :key="column">{{ column }}</th></tr></thead><tbody><tr v-for="(row,i) in rows" :key="i"><td v-for="(cell,j) in row" :key="j">{{ cell }}</td></tr><tr v-if="!rows.length"><td :colspan="columns.length" class="ops-empty">Chưa có dữ liệu phù hợp.</td></tr></tbody></table></div></section>
<form v-if="can('catalog.manage')" class="ops-panel module-form" @submit.prevent="save"><h2><Plus :size="17"/> Thêm {{ tabs.find(t => t.id === section)?.label.toLowerCase() }}</h2>
<template v-if="section === 'warehouses'"><label>Tên kho<input v-model="form.name" required minlength="2" aria-label="Tên kho"/></label><p class="module-note">Chỉ khai báo kho đầu tiên khi tài khoản chưa được gán kho. Không tự tạo địa chỉ hoặc dữ liệu tồn.</p></template>
<template v-if="section === 'partners'"><label>Tên đối tác<input v-model="form.name" required minlength="2"/></label><label>Loại đối tác<select v-model="form.kind"><option value="SUPPLIER">Nhà cung cấp</option><option value="RETAILER">Chủ hàng / bán lẻ</option></select></label></template>
<template v-if="section === 'skus'"><label>Mã SKU<input v-model="form.code" required/></label><label>Tên hàng<input v-model="form.name" required minlength="2"/></label><label>Đơn vị cơ sở<input v-model="form.base_unit" required/></label></template>
<label v-if="section === 'skus' || section === 'supplies'">Chủ hàng<select v-model="form.owner_id" required aria-label="Chủ hàng"><option value="">Chọn chủ hàng</option><option v-for="p in owners" :key="p.id" :value="p.id">{{ p.name }}</option></select></label>
<template v-if="section === 'supplies'"><label>Nhà cung cấp<select v-model="form.supplier_id" required aria-label="Nhà cung cấp"><option value="">Chọn nhà cung cấp</option><option v-for="p in suppliers" :key="p.id" :value="p.id">{{ p.name }}</option></select></label><label>SKU được cung ứng<select v-model="form.sku_id" required aria-label="SKU được cung ứng"><option value="">Chọn SKU</option><option v-for="s in skus.filter(s => s.ownerId === form.owner_id)" :key="s.id" :value="s.id">{{ s.code }} · {{ s.name }}</option></select></label></template>
<template v-if="section === 'locations'"><label>Kho<select v-model="form.warehouse_id" required><option value="">Chọn kho</option><option v-for="w in warehouses" :key="w.id" :value="w.id">{{ w.name }}</option></select></label><label>Mã vị trí<input v-model="form.code" required placeholder="Ví dụ: A-02"/></label></template>
<button class="ops-button" :disabled="busy">{{ busy ? 'Đang lưu…' : 'Lưu danh mục' }}</button></form></div></template>
