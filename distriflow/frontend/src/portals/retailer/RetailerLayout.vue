<script setup lang="ts">
import { ArrowUpRight, Warehouse } from 'lucide-vue-next'
import PartnerShell from '../../shared/layouts/PartnerShell.vue'
const navigation = [
  { to: '/retailer/outbounds', label: 'Yêu cầu xuất kho', permission: 'outbound.read', icon: ArrowUpRight },
  { to: '/retailer/inventory', label: 'Tồn kho của tôi', permission: 'inventory.read', icon: Warehouse },
]
</script>
<template>
  <PartnerShell title="Cổng nhà bán lẻ" role-label="Nhà bán lẻ / chủ hàng" :navigation="navigation"/>
</template>
