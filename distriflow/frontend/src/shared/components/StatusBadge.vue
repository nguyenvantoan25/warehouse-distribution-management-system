<script setup lang="ts">
defineProps<{ status: string }>()
const label: Record<string, string> = { ready_for_handover: 'Sẵn sàng bàn giao', pending_confirmations: 'Chờ đủ xác nhận', handed_over: 'Đã bàn giao' }
</script>
<template><span class="badge" :class="`badge--${status}`">{{ label[status] ?? status }}</span></template>
