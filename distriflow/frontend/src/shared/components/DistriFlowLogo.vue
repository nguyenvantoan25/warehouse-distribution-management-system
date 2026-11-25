<script setup lang="ts">
defineProps<{ dark?: boolean; compact?: boolean }>()
</script>
<template><span class="df-logo" :class="{ 'df-logo-dark': dark }"><span class="df-logomark" aria-hidden="true"><i/><i/><i/></span><span v-if="!compact" class="df-wordmark"><b>DISTRIFLOW</b><small>DISTRIBUTION OS</small></span></span></template>
