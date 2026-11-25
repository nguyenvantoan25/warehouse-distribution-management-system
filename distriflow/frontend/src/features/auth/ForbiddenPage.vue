<script setup lang="ts">
import { logout } from '../../app/access'
import { useRouter } from 'vue-router'
const router = useRouter()
async function leave() { await logout(); await router.replace('/login') }
</script>
<template><main class="login-shell"><section class="card"><h1>Không có quyền truy cập</h1><p>Tài khoản chưa được cấp quyền cho màn hình này.</p><button @click="leave">Đăng xuất</button></section></main></template>
