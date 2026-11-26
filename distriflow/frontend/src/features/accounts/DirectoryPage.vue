<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus, RefreshCw } from 'lucide-vue-next'
import SupplyRelations from './SupplyRelations.vue'
import { createAccount, deleteAccount, getDirectory, updateAccount, type DirectoryAccount, type DirectoryData, type ManagedRole } from './directory-api'
const groups: { key: string; role: ManagedRole; label: string }[] = [
  { key: 'shipper', role: 'SHIPPER', label: 'Shipper' },
  { key: 'supplier', role: 'SUPPLIER', label: 'Nhà cung cấp' },
  { key: 'retailer', role: 'RETAILER_OWNER', label: 'Đại lý' },
]
const route = useRoute(); const router = useRouter()
const group = computed(() => groups.find(g => g.key === route.query.group) ?? groups[0])
const data = ref<DirectoryData>({ accounts: [], unlinkedPartners: [] })
const loading = ref(true); const busy = ref(false); const error = ref(''); const notice = ref(''); const search = ref('')
const editing = ref<DirectoryAccount | null>(null)
const form = reactive({ username: '', name: '', password: '', goods: '', organization: '' })
const rows = computed(() => data.value.accounts.filter(a => a.role === group.value.role &&
  `${a.username} ${a.name} ${a.suppliedGoods ?? ''}`.toLocaleLowerCase('vi').includes(search.value.toLocaleLowerCase('vi'))))
const unlinked = computed(() => group.value.role === 'SHIPPER' ? [] : data.value.unlinkedPartners.filter(p => p.kind === (group.value.role === 'SUPPLIER' ? 'SUPPLIER' : 'RETAILER')))
function reset() { editing.value = null; form.username = ''; form.name = ''; form.password = ''; form.goods = ''; form.organization = '' }
watch(() => group.value.key, () => { reset(); search.value = ''; error.value = ''; notice.value = '' })
function edit(account: DirectoryAccount) {
  editing.value = account; form.username = account.username; form.name = account.name
  form.password = ''; form.goods = account.suppliedGoods ?? ''; form.organization = ''
  error.value = ''; notice.value = ''
}
function selectPartner() {
  const partner = unlinked.value.find(p => p.id === form.organization)
  if (partner) { form.name = partner.name; form.goods = partner.suppliedGoods ?? '' }
}
async function load() {
  loading.value = true; error.value = ''
  try { data.value = await getDirectory() }
  catch (e) { error.value = e instanceof Error ? e.message : 'Không tải được tài khoản và đối tác' }
  finally { loading.value = false }
}
async function save() {
  busy.value = true; error.value = ''; notice.value = ''
  const input = { username: form.username, name: form.name, supplied_goods: group.value.role === 'SUPPLIER' ? form.goods : null }
  try {
    if (editing.value) await updateAccount(editing.value.id, { ...input, version: editing.value.version, ...(form.password ? { password: form.password } : {}) })
    else await createAccount({ ...input, role: group.value.role, password: form.password, organization_id: form.organization || null })
    reset(); await load(); notice.value = 'Đã lưu tài khoản và thông tin đối tác.'
  } catch (e) { error.value = e instanceof Error ? e.message : 'Không lưu được tài khoản' }
  finally { form.password = ''; busy.value = false }
}
async function remove(account: DirectoryAccount) {
  if (!window.confirm(`Xóa tài khoản ${account.username}? Tài khoản sẽ ngừng đăng nhập; lịch sử và chứng từ vẫn được giữ.`)) return
  busy.value = true; error.value = ''; notice.value = ''
  try { await deleteAccount(account); reset(); await load(); notice.value = 'Đã xóa khỏi danh sách sử dụng và thu hồi phiên đăng nhập. Lịch sử được giữ nguyên.' }
  catch (e) { error.value = e instanceof Error ? e.message : 'Không xóa được tài khoản' }
  finally { busy.value = false }
}
onMounted(load)
</script>
<template>
  <div class="ops-page-heading"><div><h1>Tài khoản & đối tác</h1><p>Quản lý shipper, nhà cung cấp và đại lý trong cùng một nơi.</p></div>
    <div class="ops-actions"><RouterLink class="ops-button secondary" to="/admin/warehouses">Thiết lập kho</RouterLink><RouterLink class="ops-button secondary" to="/admin/account-scopes">Gán phạm vi</RouterLink><button class="ops-button secondary" :disabled="loading || busy" @click="load"><RefreshCw :size="15"/> Làm mới</button></div>
  </div>
  <div class="module-tabs"><button v-for="g in groups" :key="g.key" :class="{ active: group.key === g.key }" :disabled="busy" @click="router.replace({ path: '/admin/accounts', query: { group: g.key } })">{{ g.label }}</button></div>
  <p v-if="error" class="ops-alert error" role="alert">{{ error }}</p><p v-if="notice" class="ops-alert" role="status">{{ notice }}</p>
  <p v-if="loading" class="ops-loading">Đang tải tài khoản và đối tác…</p>
  <div v-else class="module-grid">
    <section class="ops-panel"><div class="ops-panel-heading"><h2>{{ group.label }} ({{ rows.length }})</h2><input v-model="search" class="ops-compact-input" aria-label="Tìm tài khoản hoặc đối tác" placeholder="Tìm tên, tài khoản…"/></div>
      <div class="ops-table-wrap"><table class="ops-table"><thead><tr><th>Tên</th><th>Tài khoản</th><th v-if="group.role === 'SUPPLIER'">Loại hàng cung cấp</th><th>Kho / trạng thái</th><th>Thao tác</th></tr></thead>
        <tbody><tr v-for="account in rows" :key="account.id"><td>{{ account.name }}</td><td>{{ account.username }}</td><td v-if="group.role === 'SUPPLIER'">{{ account.suppliedGoods || 'Chưa khai báo' }}</td><td>{{ account.warehouseName || 'Chưa gán kho' }}<small class="module-cell-note">{{ account.active ? 'Hoạt động' : 'Đã khóa' }}</small></td><td><div class="ops-actions"><button class="ops-button secondary" :aria-label="`Sửa ${account.username}`" :disabled="busy" @click="edit(account)">Sửa</button><button class="ops-button secondary" :aria-label="`Xóa ${account.username}`" :disabled="busy" @click="remove(account)">Xóa</button></div></td></tr>
          <tr v-if="!rows.length"><td :colspan="group.role === 'SUPPLIER' ? 5 : 4" class="ops-empty">Chưa có tài khoản phù hợp.</td></tr>
        </tbody></table></div>
    </section>
    <form class="ops-panel module-form" @submit.prevent="save"><h2><Plus :size="17"/> {{ editing ? 'Sửa' : 'Thêm' }} {{ group.label.toLowerCase() }}</h2>
      <label v-if="!editing && unlinked.length">Đối tác đã có, chưa có tài khoản<select v-model="form.organization" aria-label="Liên kết đối tác hiện có" @change="selectPartner"><option value="">Tạo đối tác mới cùng tài khoản</option><option v-for="p in unlinked" :key="p.id" :value="p.id">{{ p.name }}</option></select></label>
      <label>Tên<input v-model="form.name" required minlength="2" maxlength="150" aria-label="Tên"/></label>
      <label>Tài khoản<input v-model="form.username" required minlength="3" maxlength="80" pattern="[A-Za-z0-9_.\-]+" autocomplete="off" aria-label="Tài khoản"/></label>
      <label>{{ editing ? 'Mật khẩu mới' : 'Mật khẩu' }}<input v-model="form.password" type="password" :required="!editing" minlength="10" maxlength="128" autocomplete="new-password" :aria-label="editing ? 'Mật khẩu mới' : 'Mật khẩu'"/></label>
      <p v-if="editing" class="module-note">Để trống mật khẩu nếu không đổi. Sau khi sửa, tài khoản cần đăng nhập lại.</p>
      <label v-if="group.role === 'SUPPLIER'">Loại hàng cung cấp<textarea v-model="form.goods" required maxlength="1000" rows="3" aria-label="Loại hàng cung cấp"/></label>
      <p class="module-note">{{ group.role === 'SUPPLIER' ? 'Loại hàng là thông tin mô tả, không tự cấp quyền cung ứng SKU.' : group.role === 'SHIPPER' ? 'Shipper chỉ được xem và xử lý nhiệm vụ được phân.' : 'Đại lý là đối tác chủ hàng / bán lẻ trong các luồng xuất và tồn kho.' }}</p>
      <p class="module-note">Tài khoản mới thuộc phạm vi kho của quản trị viên. Nếu chưa có kho, cần thiết lập kho và gán phạm vi trước khi vận hành.</p>
      <div class="ops-actions"><button class="ops-button" :disabled="busy">{{ busy ? 'Đang lưu…' : 'Lưu tài khoản' }}</button><button v-if="editing" type="button" class="ops-button secondary" :disabled="busy" @click="reset">Hủy sửa</button></div>
    </form>
  </div>
  <details v-if="group.role === 'SUPPLIER'" class="directory-relations"><summary>Quan hệ cung ứng theo SKU</summary><SupplyRelations/></details>
</template>
<style scoped>
.module-grid>*{min-width:0}.module-tabs{flex-wrap:wrap}.ops-panel-heading{flex-wrap:wrap}.ops-compact-input{max-width:100%}
.directory-relations{margin-top:20px}.directory-relations>summary{cursor:pointer;padding:16px;border:1px solid #dbe3ed;border-radius:10px;background:white;font-size:14px;font-weight:600}.directory-relations[open]>summary{margin-bottom:12px}.module-form textarea{display:block;width:100%;margin-top:6px;border:1px solid #dbe3ed;border-radius:8px;padding:10px;font:inherit;resize:vertical}
</style>
