<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useCatalog } from '../catalog/useCatalog'
import { getAccounts, setScope, type AccountScope } from './api'
const { warehouses, partners, error: catalogError } = useCatalog()
const accounts = ref<AccountScope[]>([]); const selected = ref(''); const warehouse = ref(''); const organization = ref('')
const busy = ref(false); const error = ref(''); const notice = ref('')
const current = computed(() => accounts.value.find(a => a.id === selected.value))
const expected = computed(() => current.value?.role === 'SUPPLIER' ? 'SUPPLIER' : current.value?.role === 'RETAILER_OWNER' ? 'RETAILER' : '')
const choices = computed(() => partners.value.filter(p => p.kind === expected.value && p.active))
watch(selected, () => { organization.value = current.value?.organizationIds[0] ?? ''; warehouse.value = warehouses.value.find(w => w.name === current.value?.warehouseName)?.id ?? warehouses.value[0]?.id ?? '' })
async function load() { try { accounts.value = await getAccounts() } catch (e) { error.value = e instanceof Error ? e.message : 'Không tải được tài khoản' } }
onMounted(load)
async function save() {
  busy.value = true; error.value = ''; notice.value = ''
  try { await setScope(selected.value, { warehouse_id: warehouse.value, organization_id: expected.value ? organization.value : null }); await load(); notice.value = 'Đã lưu phạm vi. Tài khoản được thay đổi cần đăng nhập lại.' }
  catch (e) { error.value = e instanceof Error ? e.message : 'Không lưu được phạm vi' }
  finally { busy.value = false }
}
</script>
<template>
<div class="ops-page-heading"><div><h1>Tài khoản & phạm vi</h1><p>Gán rõ kho và tổ chức trước khi sử dụng dữ liệu thật. Không thay đổi mật khẩu hoặc vai trò tại đây.</p></div><RouterLink class="ops-button secondary" to="/admin/warehouses">Thiết lập kho</RouterLink></div>
<p v-if="error || catalogError" role="alert" class="ops-alert error">{{ error || catalogError }}</p><p v-if="notice" role="status" class="ops-alert">{{ notice }}</p>
<div class="module-grid"><section class="ops-panel"><div class="ops-table-wrap"><table class="ops-table"><thead><tr><th>Tài khoản</th><th>Vai trò</th><th>Kho</th></tr></thead><tbody><tr v-for="a in accounts" :key="a.id"><td>{{ a.username }}</td><td>{{ a.role }}</td><td>{{ a.warehouseName || 'Chưa gán' }}</td></tr></tbody></table></div></section>
<form class="ops-panel module-form" @submit.prevent="save"><h2>Gán phạm vi truy cập</h2>
<label>Tài khoản<select v-model="selected" required aria-label="Tài khoản"><option value="">Chọn tài khoản</option><option v-for="a in accounts" :key="a.id" :value="a.id">{{ a.username }} · {{ a.role }}</option></select></label>
<label>Kho được phép<select v-model="warehouse" required aria-label="Kho được phép"><option value="">Chọn kho</option><option v-for="w in warehouses" :key="w.id" :value="w.id">{{ w.name }}</option></select></label>
<label v-if="expected">Tổ chức đối tác<select v-model="organization" required aria-label="Tổ chức đối tác"><option value="">Chọn tổ chức đúng vai trò</option><option v-for="p in choices" :key="p.id" :value="p.id">{{ p.name }}</option></select></label>
<p class="module-note">Chỉ hiển thị tài khoản chưa gán kho hoặc thuộc kho của bạn. Supplier phải gắn nhà cung cấp; retailer phải gắn chủ hàng.</p>
<button class="ops-button" :disabled="busy || !selected || !warehouse">{{ busy ? 'Đang lưu…' : 'Lưu phạm vi' }}</button></form></div>
</template>
