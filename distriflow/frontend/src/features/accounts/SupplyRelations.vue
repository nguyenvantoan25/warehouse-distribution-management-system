<script setup lang="ts">
import { ref } from 'vue'
import { useCatalog } from '../catalog/useCatalog'
import { createCatalogRecord } from '../catalog/api'
const { partners, skus, supplies, owners, suppliers, load, error } = useCatalog()
const supplier = ref(''); const owner = ref(''); const sku = ref(''); const notice = ref(''); const busy = ref(false)
const nameOf = (id: string) => partners.value.find(p => p.id === id)?.name ?? id
async function save() {
  busy.value = true; notice.value = ''
  try {
    await createCatalogRecord('/supply-relationships', { supplier_id: supplier.value, owner_id: owner.value, sku_id: sku.value })
    await load(); notice.value = 'Đã lưu quan hệ cung ứng theo SKU.'
  } catch (e) { notice.value = e instanceof Error ? e.message : 'Không lưu được quan hệ cung ứng' }
  finally { busy.value = false }
}
</script>
<template>
  <section class="ops-panel module-form">
    <h2>Quan hệ cung ứng theo SKU</h2><p class="module-note">Loại hàng là mô tả. Chỉ quan hệ dưới đây mới cho phép nhà cung cấp tạo yêu cầu nhập cho SKU/chủ hàng tương ứng.</p>
    <p v-if="error" class="ops-alert" role="alert">{{ error }}</p><p v-if="notice" class="ops-alert" role="status">{{ notice }}</p>
    <form @submit.prevent="save"><div class="module-fields">
      <label>Nhà cung cấp<select v-model="supplier" required aria-label="Nhà cung cấp"><option value="">Chọn nhà cung cấp</option><option v-for="p in suppliers.filter(p => p.active)" :key="p.id" :value="p.id">{{ p.name }}</option></select></label>
      <label>Chủ hàng<select v-model="owner" required aria-label="Chủ hàng" @change="sku = ''"><option value="">Chọn đại lý / chủ hàng</option><option v-for="p in owners" :key="p.id" :value="p.id">{{ p.name }}</option></select></label>
      <label>SKU được cung ứng<select v-model="sku" required aria-label="SKU được cung ứng"><option value="">Chọn SKU</option><option v-for="s in skus.filter(s => s.ownerId === owner)" :key="s.id" :value="s.id">{{ s.code }} · {{ s.name }}</option></select></label>
    </div><button class="ops-button" :disabled="busy">Lưu quan hệ cung ứng</button></form>
    <div class="ops-table-wrap"><table class="ops-table"><thead><tr><th>Nhà cung cấp</th><th>Đại lý / chủ hàng</th><th>SKU</th></tr></thead><tbody><tr v-for="s in supplies" :key="s.id"><td>{{ nameOf(s.supplier_id) }}</td><td>{{ nameOf(s.owner_id) }}</td><td>{{ skus.find(k => k.id === s.sku_id)?.code ?? s.sku_id }}</td></tr></tbody></table></div>
  </section>
</template>
