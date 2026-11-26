<script setup lang="ts">
import { computed, ref, type Component } from 'vue'
import { useRouter } from 'vue-router'
import { Menu, LogOut, X } from 'lucide-vue-next'
import { auth, can, logout } from '../../app/access'
import DistriFlowLogo from '../components/DistriFlowLogo.vue'
const props = defineProps<{
  title: string
  roleLabel: string
  navigation: readonly { to: string; label: string; permission: string; icon: Component }[]
}>()
const navigation = computed(() => props.navigation.filter(item => can(item.permission)))
const open = ref(false)
const router = useRouter()
async function leave() { await logout(); await router.replace('/login') }
</script>
<template>
  <div class="ops-shell" :class="{ 'sidebar-open': open }">
    <button v-if="open" class="ops-mobile-overlay" aria-label="Đóng menu bên ngoài" @click="open = false"/>
    <aside class="ops-sidebar">
      <div class="ops-brand partner-brand">
        <DistriFlowLogo/>
        <button v-if="open" class="ops-icon-button ops-mobile-menu" aria-label="Đóng menu" @click="open = false"><X :size="20"/></button>
      </div>
      <nav class="ops-nav" :aria-label="title">
        <span class="ops-nav-label">{{ title }}</span>
        <RouterLink v-for="item in navigation" :key="item.to" :to="item.to" class="ops-nav-item" active-class="selected" @click="open = false">
          <component :is="item.icon" :size="17"/> {{ item.label }}
        </RouterLink>
      </nav>
      <div class="ops-sidebar-user">
        <span class="ops-user-square">{{ auth.user?.username.slice(0, 2).toUpperCase() }}</span>
        <div><b>{{ auth.user?.username }}</b><small>{{ roleLabel }}</small></div>
      </div>
    </aside>
    <div class="ops-workspace">
      <header class="ops-topbar">
        <button class="ops-icon-button ops-mobile-menu" aria-label="Mở menu" @click="open = true"><Menu :size="20"/></button>
        <div class="ops-header-title"><p>DistriFlow / {{ roleLabel }}</p><h1>{{ title }}</h1></div>
        <button class="ops-button secondary" @click="leave"><LogOut :size="15"/> Đăng xuất</button>
      </header>
      <main class="ops-main"><RouterView/></main>
    </div>
  </div>
</template>
<style scoped>
.partner-brand { display: flex; justify-content: space-between; gap: 8px; }
/* Isolate the sidebar from the legacy shipper bottom-navigation element rule. */
.ops-nav { position: static; inset: auto; transform: none; width: auto; display: block; border-top: 0; text-align: left; }
</style>
