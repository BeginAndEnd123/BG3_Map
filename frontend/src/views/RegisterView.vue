<template>
  <AuthForm title="注册" :submitting="submitting" :error="error" submit-label="注册中..."
    link-text="已有账号？" link-label="登录" link-to="/login"
    @submit="handleRegister">
    <input type="text" v-model="username" placeholder="用户名（至少2个字符）" required minlength="2" />
    <input type="password" v-model="password" placeholder="密码（至少6个字符）" required minlength="6" />
    <input type="password" v-model="confirmPassword" placeholder="确认密码" required />
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
const confirmPassword = ref('')
const error = ref('')
const submitting = ref(false)

async function handleRegister() {
  if (submitting.value) return
  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }
  submitting.value = true
  try {
    error.value = ''
    await authStore.register(username.value, password.value, confirmPassword.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '注册失败'
  } finally {
    submitting.value = false
  }
}
</script>
