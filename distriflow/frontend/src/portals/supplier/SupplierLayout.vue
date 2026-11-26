<script setup lang="ts">
import { ArrowDownToLine } from 'lucide-vue-next'
import PartnerShell from '../../shared/layouts/PartnerShell.vue'
const navigation = [
  { to: '/supplier/inbounds', label: 'Yêu cầu nhập kho', permission: 'inbound.read', icon: ArrowDownToLine },
]
</script>
<template>
  <PartnerShell title="Cổng nhà cung cấp" role-label="Nhà cung cấp" :navigation="navigation"/>
</template>
