<script setup lang="ts">
import { Eye, ArrowUpDown } from 'lucide-vue-next'
import StatusBadge from '../../shared/components/StatusBadge.vue'
import type { Task } from '../../shared/types/domain'
defineProps<{ tasks: Task[] }>()
</script>
<template><div class="ops-table-wrap"><table class="ops-table"><thead><tr><th>Mã phiếu <ArrowUpDown :size="12"/></th><th>Kho xuất</th><th>Người nhận</th><th class="numeric">Số kiện</th><th>Trạng thái</th><th class="align-center">Thao tác</th></tr></thead><tbody><tr v-for="task in tasks" :key="task.id"><td><RouterLink class="ops-code" :to="`/admin/handovers/${task.id}`">{{ task.code }}</RouterLink></td><td>{{ task.warehouseName }}</td><td>{{ task.shipperName }}</td><td class="numeric">{{ task.packages.length }}</td><td><StatusBadge :status="task.status"/></td><td class="align-center"><RouterLink class="ops-eye" :to="`/admin/handovers/${task.id}`" aria-label="Xem chi tiết phiếu"><Eye :size="17"/></RouterLink></td></tr><tr v-if="!tasks.length"><td colspan="6" class="ops-empty">Không có phiếu phù hợp với bộ lọc.</td></tr></tbody></table></div></template>
