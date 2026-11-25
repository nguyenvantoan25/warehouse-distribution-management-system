<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, ApiError } from '../../shared/api/client'
import { getMyTasks, taskCommand } from './api'
import { auth, can, logout } from '../../app/access'
import type { Task } from '../../shared/types/domain'
import StatusBadge from '../../shared/components/StatusBadge.vue'
import DistriFlowLogo from '../../shared/components/DistriFlowLogo.vue'
import { ClipboardList, QrCode, History, UserRound, RefreshCw } from 'lucide-vue-next'

const router = useRouter()
const tasks = ref<Task[]>([])
const activeId = ref('')
const active = computed(() => tasks.value.find(task => task.id === activeId.value) ?? null)
const scanCode = ref('')
const message = ref('')
const busy = ref(false)
const loading = ref(true)
const tab = ref('Nhiệm vụ')
const tabs = ['Nhiệm vụ', 'Quét mã', 'Lịch sử', 'Tài khoản']
const tabIcons = [ClipboardList, QrCode, History, UserRound]
const allScanned = computed(() => !!active.value && active.value.scannedCodes.length === active.value.packages.length)
const history = computed(() => tasks.value.filter(task => task.status === 'handed_over'))
const permissions = { respond: 'tasks.respond', arrive: 'tasks.arrive', scan: 'packages.scan', 'shipper-confirm': 'handover.receive' }
async function load() {
  loading.value = true
  try {
    tasks.value = await getMyTasks()
    if (!tasks.value.some(task => task.id === activeId.value)) activeId.value = tasks.value[0]?.id ?? ''
    message.value = ''
  } catch (error) { message.value = error instanceof Error ? error.message : 'Không thể tải nhiệm vụ' }
  finally { loading.value = false }
}
async function command(action: keyof typeof permissions, payload: Record<string, unknown> = {}) {
  if (!active.value || busy.value || !can(permissions[action])) return
  busy.value = true; message.value = 'Đang kiểm tra với máy chủ…'
  try {
    const task = await taskCommand(active.value.id, action, { version: active.value.version, ...payload })
    tasks.value = tasks.value.map(item => item.id === task.id ? task : item)
    message.value = task.status === 'pending_confirmations' ? 'Đã xác nhận nhận hàng. Đang chờ kho xác nhận bàn giao.' : 'Máy chủ đã ghi nhận thao tác.'
    if (action === 'scan') scanCode.value = ''
  } catch (error) { message.value = error instanceof ApiError ? error.message : 'Chưa đồng bộ — hãy tải lại để kiểm tra kết quả.' }
  finally { busy.value = false }
}
async function leave() { await logout(); await router.replace('/login') }
onMounted(load)
</script>
<template>
  <main class="mobile-shell">
    <header class="shipper-topbar"><DistriFlowLogo dark/><span class="shipper-avatar">{{ auth.user?.username.slice(0,2).toUpperCase() }}</span></header>
    <div class="shipper-page-heading"><div><p>Chào {{ auth.user?.username }},</p><h1>{{ tab }}</h1></div><button class="shipper-refresh" :disabled="loading || busy" aria-label="Tải lại nhiệm vụ" @click="load"><RefreshCw :size="18"/></button></div>
    <p v-if="message" class="notice" role="status">{{ message }}</p>
    <p v-if="loading">Đang tải dữ liệu…</p>
    <section v-else-if="tab === 'Tài khoản'" class="task">
      <h2>{{ auth.user?.username }}</h2><p>{{ auth.user?.role }}</p><button @click="leave">Đăng xuất</button>
    </section>
    <section v-else-if="tab === 'Lịch sử'" class="task">
      <p v-if="!history.length">Chưa có nhiệm vụ đã bàn giao.</p>
      <p v-for="task in history" :key="task.id">{{ task.code }} · <StatusBadge :status="task.status" /></p>
    </section>
    <template v-else>
      <label v-if="tasks.length" for="task">Nhiệm vụ được phân công</label>
      <select v-if="tasks.length" id="task" v-model="activeId" :disabled="busy">
        <option v-for="task in tasks" :key="task.id" :value="task.id">{{ task.code }}</option>
      </select>
      <section v-if="active" class="task">
        <div class="row"><div><small>{{ active.code }}</small><h2>{{ active.warehouseName }}</h2></div><StatusBadge :status="active.status" /></div>
        <p>{{ active.packages.length }} kiện cần đối chiếu tại kho.</p>
        <div class="progress">Đã quét {{ active.scannedCodes.length }}/{{ active.packages.length }} kiện</div>
        <button v-if="can('tasks.respond') && !active.shipperAccepted" :disabled="busy" @click="command('respond', { accepted: true })">Nhận nhiệm vụ</button>
        <button v-else-if="can('tasks.arrive') && !active.arrivedAtWarehouse" :disabled="busy" @click="command('arrive')">Tôi đã đến kho</button>
        <template v-else-if="active.status === 'ready_for_handover'">
          <form v-if="can('packages.scan')" @submit.prevent="command('scan', { package_code: scanCode })">
            <label for="scan">Mã kiện</label><input id="scan" v-model="scanCode" required placeholder="Nhập mã trên kiện" />
            <button :disabled="busy || !scanCode.trim()">Đối chiếu kiện</button>
          </form>
          <button v-if="can('handover.receive')" class="outline" :disabled="busy || !allScanned" @click="command('shipper-confirm')">Xác nhận nhận hàng</button>
          <small v-if="!allScanned">Cần đối chiếu đủ kiện trước khi xác nhận.</small>
        </template>
        <p v-else>{{ active.status === 'handed_over' ? 'Kho và shipper đã hoàn tất bàn giao.' : 'Đang chờ kho xác nhận. Tải lại để cập nhật.' }}</p>
      </section>
      <section v-else class="empty">Chưa có nhiệm vụ được phân công.</section>
    </template>
    <nav aria-label="Shipper"><button v-for="(item,index) in tabs" :key="item" :disabled="busy" :aria-current="tab === item ? 'page' : undefined" @click="tab = item"><component :is="tabIcons[index]" :size="19"/>{{ item }}</button></nav>
  </main>
</template>
