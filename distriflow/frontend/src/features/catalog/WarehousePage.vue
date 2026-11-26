<script setup lang="ts">
import { ref } from 'vue'
import { useCatalog } from './useCatalog'
import { createCatalogRecord } from './api'
const { warehouses, loading, error, load } = useCatalog()
const name = ref(''); const busy = ref(false); const notice = ref('')
async function save() {
  busy.value = true; notice.value = ''
  try {
    await createCatalogRecord('/warehouses', { name: name.value }); await load()
    notice.value = 'Đã khai báo kho. Có thể tạo vị trí và gán phạm vi tài khoản.'; name.value = ''
  } catch (e) { notice.value = e instanceof Error ? e.message : 'Không thể khai báo kho' }
  finally { busy.value = false }
}
</script>
<template>
  <div class="ops-page-heading"><div><h1>Thiết lập kho</h1><p>Khai báo kho đầu tiên trước khi gán phạm vi và quản lý vị trí.</p></div>
    <RouterLink class="ops-button secondary" to="/admin/accounts">Tài khoản & đối tác</RouterLink>
  </div>
  <p v-if="error" class="ops-alert error" role="alert">{{ error }}</p>
  <p v-if="notice" class="ops-alert" role="status">{{ notice }}</p>
  <p v-if="loading" class="ops-loading">Đang tải kho…</p>
  <div v-else class="module-grid">
    <section class="ops-panel"><div class="ops-table-wrap"><table class="ops-table">
      <thead><tr><th>Tên kho</th><th>ID kho</th></tr></thead>
      <tbody><tr v-for="warehouse in warehouses" :key="warehouse.id"><td>{{ warehouse.name }}</td><td>{{ warehouse.id }}</td></tr>
        <tr v-if="!warehouses.length"><td colspan="2" class="ops-empty">Chưa có kho được gán.</td></tr>
      </tbody>
    </table></div></section>
    <form v-if="!warehouses.length" class="ops-panel module-form" @submit.prevent="save">
      <h2>Khai báo kho thật</h2><label>Tên kho<input v-model="name" required minlength="2" maxlength="150"/></label>
      <p class="module-note">Chỉ khai báo kho đầu tiên khi tài khoản chưa được gán kho. Không tự tạo địa chỉ hoặc hàng tồn.</p>
      <button class="ops-button" :disabled="busy">{{ busy ? 'Đang lưu…' : 'Lưu kho' }}</button>
    </form>
    <section v-else class="ops-panel module-form"><h2>Kho đã được khai báo</h2><p>Tiếp tục quản lý sản phẩm/vị trí hoặc khai báo 800 vị trí kệ đơn.</p>
      <RouterLink class="ops-button" to="/admin/catalog">Sản phẩm & vị trí</RouterLink>
      <RouterLink class="ops-button secondary" to="/admin/inventory">Bản đồ tồn kho</RouterLink>
    </section>
  </div>
</template>
