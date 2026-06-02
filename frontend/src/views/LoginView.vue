<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>登录</h2>
      <form @submit.prevent="handleLogin">
        <input type="text" v-model="username" placeholder="用户名" required />
        <input type="password" v-model="password" placeholder="密码" required />
        <button type="submit">登录</button>
      </form>
      <p class="auth-link">
        没有账号？<router-link to="/register">注册</router-link>
      </p>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const username = ref('')
const password = ref('')
const error = ref('')

async function handleLogin() {
  try {
    error.value = ''
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败'
  }
}
</script>

<style scoped>
.auth-page {
  display: flex; justify-content: center; align-items: center;
  height: 100vh; background: #0f0f23;
}
.auth-card {
  background: #1a1a2e; padding: 40px; border-radius: 8px;
  width: 360px; color: #eee;
}
.auth-card h2 { text-align: center; margin-bottom: 24px; color: #ffd700; }
input {
  width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #444;
  border-radius: 4px; background: #16213e; color: #eee; font-size: 14px;
}
button {
  width: 100%; padding: 10px; margin-top: 16px; background: #e94560;
  color: #fff; border: none; border-radius: 4px; font-size: 16px; cursor: pointer;
}
button:hover { background: #d63851; }
.auth-link { text-align: center; margin-top: 16px; font-size: 13px; }
.auth-link a { color: #4ea8de; }
.error { color: #e94560; text-align: center; margin-top: 12px; }
</style>
