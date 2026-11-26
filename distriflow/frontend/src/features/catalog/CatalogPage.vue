<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { Plus, RefreshCw } from 'lucide-vue-next'
import { useCatalog } from './useCatalog'
import { createCatalogRecord } from './api'
import { can } from '../../app/access'

type Section = 'skus' | 'locations'
const productUnit = 'Thùng'
const { partners, skus, warehouses, locations, owners, loading, error, load } = useCatalog()
const section = ref<Section>('skus')
const notice = ref('')
const busy = ref(false)
const search = ref('')
const form = reactive({ name: '', code: '', owner_id: '', warehouse_id: '' })
const tabs: { id: Section; label: string }[] = [{ id: 'skus', label: 'Sản phẩm' }, { id: 'locations', label: 'Vị trí kho' }]
const nameOf = (id: string) => partners.value.find(p => p.id === id)?.name ?? id
const rows = computed(() => {
  const values = section.value === 'skus'
    ? skus.value.map(s => [s.code, s.name, s.baseUnit, nameOf(s.ownerId)])
    : locations.value.map(l => [l.code, warehouses.value.find(w => w.id === l.warehouseId)?.name ?? l.warehouseId])
  return values.filter(row => row.join(' ').toLowerCase().includes(search.value.toLowerCase()))
})
const columns = computed(() => section.value === 'skus' ? ['Mã SKU', 'Tên hàng', 'Đơn vị', 'Chủ hàng'] : ['Mã vị trí', 'Kho'])
async function save() {
  if (!tabs.some(tab => tab.id === section.value)) return
  busy.value = true; notice.value = ''
  const path = `/${section.value}`
  const payload = section.value === 'skus' ? { code: form.code, name: form.name, base_unit: productUnit, owner_id: form.owner_id } : { warehouse_id: form.warehouse_id, code: form.code }
  try {
    await createCatalogRecord(path, payload); await load()
    notice.value = 'Đã lưu danh mục vào cơ sở dữ liệu.'; form.name = ''; form.code = ''
  } catch (e) { notice.value = e instanceof Error ? e.message : 'Không thể lưu danh mục' }
  finally { busy.value = false }
}
</script>

<template>
  <div class="ops-page-heading">
    <div><h1>Danh mục & vị trí</h1>
      <p>Quản lý sản phẩm, đơn vị tính và vị trí lưu kho.</p>
    </div>
    <button class="ops-button secondary" :disabled="loading || busy" @click="load"><RefreshCw :size="15"/> Làm mới</button>
  </div>
  <div class="module-tabs">
    <button v-for="tab in tabs" :key="tab.id" :class="{ active: section === tab.id }" @click="section = tab.id; search = ''">{{ tab.label }}</button>
  </div>
  <p v-if="!loading && !warehouses.length && can('catalog.manage')" class="ops-alert">
    Chưa có kho được gán. <RouterLink class="ops-text-link" to="/admin/warehouses">Khai báo kho thật trước</RouterLink>. Sau đó gán phạm vi từ mục Tài khoản & đối tác.
  </p>
  <p v-if="error" class="ops-alert error" role="alert">{{ error }}</p>
  <p v-if="notice" class="ops-alert" role="status">{{ notice }}</p>
  <p v-if="loading" class="ops-loading">Đang tải danh mục…</p>
  <div v-else class="module-grid">
    <section class="ops-panel">
      <div class="ops-panel-heading"><h2>{{ tabs.find(t => t.id === section)?.label }} ({{ rows.length }})</h2>
        <input v-model="search" class="ops-compact-input" placeholder="Tìm kiếm…" aria-label="Tìm danh mục"/>
      </div>
      <div class="ops-table-wrap"><table class="ops-table">
        <thead><tr><th v-for="column in columns" :key="column">{{ column }}</th></tr></thead>
        <tbody><tr v-for="(row,i) in rows" :key="i"><td v-for="(cell,j) in row" :key="j">{{ cell }}</td></tr>
          <tr v-if="!rows.length"><td :colspan="columns.length" class="ops-empty">Chưa có dữ liệu phù hợp.</td></tr>
        </tbody>
      </table></div>
    </section>
    <form v-if="can('catalog.manage')" class="ops-panel module-form" @submit.prevent="save">
      <h2><Plus :size="17"/> Thêm {{ tabs.find(t => t.id === section)?.label.toLowerCase() }}</h2>
      <template v-if="section === 'skus'">
        <label>Mã SKU<input v-model="form.code" required/></label>
        <label>Tên hàng<input v-model="form.name" required minlength="2"/></label>
        <label>Đơn vị tính<input :value="productUnit" readonly aria-readonly="true"/></label>
      </template>
      <label v-if="section === 'skus'">Chủ hàng<select v-model="form.owner_id" required aria-label="Chủ hàng"><option value="">Chọn đối tác chủ hàng</option><option v-for="p in owners" :key="p.id" :value="p.id">{{ p.name }}</option></select></label>
      <p v-if="section === 'skus'" class="module-note">Chủ hàng lấy từ các đại lý đang hoạt động. <RouterLink v-if="!owners.length" to="/admin/accounts?group=retailer">Khai báo đại lý trước</RouterLink></p>
      <template v-if="section === 'locations'">
        <label>Kho<select v-model="form.warehouse_id" required aria-label="Kho"><option value="">Chọn kho</option><option v-for="w in warehouses" :key="w.id" :value="w.id">{{ w.name }}</option></select></label>
        <label>Mã vị trí<input v-model="form.code" required/></label>
      </template>
      <button class="ops-button" :disabled="busy">{{ busy ? 'Đang lưu…' : 'Lưu danh mục' }}</button>
    </form>
  </div>
</template>
