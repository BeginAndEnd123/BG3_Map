/**
 * 认证状态管理 (Pinia)
 *
 * 管理用户 token 和用户信息，提供登录/注册/登出/自动恢复方法。
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as apiLogin, register as apiRegister, getMe } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)                                     // 当前用户信息
  const token = ref(localStorage.getItem('token') || '')     // JWT 令牌

  async function login(username, password) {
    const res = await apiLogin({ username, password })
    token.value = res.data.access_token
    user.value = res.data.user
    localStorage.setItem('token', token.value)
  }

  async function register(username, password, confirmPassword) {
    const res = await apiRegister({ username, password, confirm_password: confirmPassword })
    token.value = res.data.access_token
    user.value = res.data.user
    localStorage.setItem('token', token.value)
  }

  async function fetchUser() {
    /** 尝试用本地 token 恢复登录态，仅 401 时登出 */
    if (!token.value) return
    try {
      const res = await getMe()
      user.value = res.data
    } catch (e) {
      if (e.response?.status === 401) {
        logout()
      }
    }
  }

  function logout() {
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
  }

  return { user, token, login, register, fetchUser, logout }
})
