<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login, homePath } from '../../app/access'
import DistriFlowLogo from '../../shared/components/DistriFlowLogo.vue'
import { ArrowRight, ShieldCheck } from 'lucide-vue-next'
const username = ref(''); const password = ref(''); const busy = ref(false); const error = ref('')
const router = useRouter()
async function submit() {
  busy.value = true; error.value = ''
  try { await login(username.value, password.value); password.value = ''; await router.replace(homePath()) }
  catch (e) { error.value = e instanceof Error ? e.message : 'Không thể đăng nhập' }
  finally { busy.value = false }
}
</script>
<template><main class="login-shell"><form class="card" @submit.prevent="submit">
  <DistriFlowLogo/><h1>Chào mừng trở lại</h1><p>Đăng nhập để tiếp tục công việc tại kho.</p>
  <label for="username">Tên đăng nhập</label><input id="username" v-model="username" required autocomplete="username" />
  <label for="password">Mật khẩu</label><input id="password" v-model="password" type="password" required autocomplete="current-password" />
  <p v-if="error" role="alert" class="error">{{ error }}</p>
  <button :disabled="busy" type="submit">{{ busy ? 'Đang đăng nhập…' : 'Đăng nhập' }} <ArrowRight :size="16"/></button>
  <div class="df-login-note"><ShieldCheck :size="14"/> Phiên làm việc được bảo vệ bằng xác thực tài khoản</div>
</form></main></template>
