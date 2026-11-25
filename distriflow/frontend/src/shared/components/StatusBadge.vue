<script setup lang="ts">
defineProps<{ status: string }>()
const label: Record<string, string> = { ready_for_handover: 'Sẵn sàng bàn giao', pending_confirmations: 'Chờ đủ xác nhận', handed_over: 'Đã bàn giao', submitted: 'Chờ duyệt', approved: 'Đã duyệt', received: 'Đã kiểm nhận', stocked: 'Đã nhập kho', rejected: 'Đã từ chối', picked: 'Đã soạn hàng', packed: 'Đã đóng kiện', cancelled: 'Đã hủy' }
</script>
<template><span class="badge" :class="`badge--${status}`">{{ label[status] ?? status }}</span></template>
