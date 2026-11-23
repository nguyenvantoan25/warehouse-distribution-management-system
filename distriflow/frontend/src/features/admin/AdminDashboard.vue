<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../../shared/api/client'
import type { Dashboard } from '../../shared/types/domain'
import StatusBadge from '../../shared/components/StatusBadge.vue'
const dashboard = ref<Dashboard | null>(null); const error = ref('')
onMounted(async () => { try { dashboard.value = await api<Dashboard>('/dashboard') } catch (e) { error.value = e instanceof Error ? e.message : 'Lỗi không xác định' } })
</script>
<template>
  <main class="desktop-shell"><aside><strong>DistriFlow</strong><p>Quản trị kho</p><a class="active">Tổng quan</a><a>Tồn kho</a><a>Yêu cầu xuất</a><a>Bàn giao tại kho</a><a>Điều phối</a></aside>
  <section class="content"><header><div><p class="eyebrow">UI01 · M09.01</p><h1>Tổng quan kho</h1><p>Theo dõi tồn kho và hàng đợi bàn giao tại kho.</p></div><button>Xuất báo cáo</button></header>
  <p v-if="error" class="error">{{ error }}</p><p v-else-if="!dashboard">Đang tải dữ liệu…</p>
  <template v-else><div class="stats"><article><span>Khả dụng</span><b>{{ dashboard.available }}</b><small>đơn vị hàng</small></article><article><span>Đã giữ cho đơn</span><b>{{ dashboard.reserved }}</b><small>không thể dùng cho đơn mới</small></article><article><span>Yêu cầu chờ xử lý</span><b>{{ dashboard.pendingOutbound }}</b><small>chưa tác động tồn</small></article><article><span>Sẵn sàng bàn giao</span><b>{{ dashboard.readyHandover }}</b><small>cần xác nhận hai bên</small></article></div>
  <article class="card"><h2>Hàng đợi bàn giao</h2><table><thead><tr><th>Mã nhiệm vụ</th><th>Kho</th><th>Kiện</th><th>Trạng thái</th></tr></thead><tbody><tr v-for="task in dashboard.tasks" :key="task.id"><td>{{ task.code }}</td><td>{{ task.warehouseName }}</td><td>{{ task.packages.length }}</td><td><StatusBadge :status="task.status"/></td></tr></tbody></table></article></template></section></main>
</template>
