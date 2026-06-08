<template>
  <AuthForm title="登录" :submitting="submitting" :error="error"
    link-text="没有账号？" link-label="注册" link-to="/register"
    @submit="handleLogin">
    <input type="text" v-model="username" placeholder="用户名" required />
    <input type="password" v-model="password" placeholder="密码" required />
  </AuthForm>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import AuthForm from '../components/AuthForm.vue'

const router = useRouter()
const authStore = useAuthStore()
const username = ref('')
const password = ref('')
const error = ref('')
const submitting = ref(false)

async function handleLogin() {
  if (submitting.value) return
  submitting.value = true
  try {
    error.value = ''
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败'
  } finally {
    submitting.value = false
  }
}
</script>
