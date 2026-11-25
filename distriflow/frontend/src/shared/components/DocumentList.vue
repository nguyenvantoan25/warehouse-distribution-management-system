<script setup lang="ts">
import type { StockDocument } from '../types/documents'
import StatusBadge from './StatusBadge.vue'
defineProps<{ documents: StockDocument[]; selectedId: string }>()
const emit = defineEmits<{ select: [id: string] }>()
</script>
<template><section class="ops-panel"><div class="ops-panel-heading"><h2>Danh sách yêu cầu ({{ documents.length }})</h2></div><div class="ops-table-wrap"><table class="ops-table"><thead><tr><th>Mã yêu cầu</th><th>Chủ hàng</th><th>Trạng thái</th><th>Tạo lúc</th></tr></thead><tbody><tr v-for="doc in documents" :key="doc.id" :class="{ 'row-selected': selectedId === doc.id }"><td><button class="module-code-button" @click="emit('select',doc.id)">{{ doc.code }}</button></td><td>{{ doc.ownerName }}</td><td><StatusBadge :status="doc.status"/></td><td>{{ new Date(doc.createdAt).toLocaleString('vi-VN') }}</td></tr><tr v-if="!documents.length"><td colspan="4" class="ops-empty">Chưa có yêu cầu trong phạm vi được cấp.</td></tr></tbody></table></div></section></template>
