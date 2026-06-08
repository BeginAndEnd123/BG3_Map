/**
 * 认证状态管理 (Pinia)
 *
 * 管理用户 token 和用户信息，提供登录/注册/登出/自动恢复方法。
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/index'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')

  async function login(username, password) {
    try {
      const res = await api.post('/auth/login', { username, password })
      token.value = res.data.access_token
      user.value = res.data.user
      localStorage.setItem('token', token.value)
    } catch (e) {
      console.error('登录失败:', e.response?.status, e.message)
      throw e
    }
  }

  async function register(username, password, confirmPassword) {
    try {
      const res = await api.post('/auth/register', {
        username, password, confirm_password: confirmPassword,
      })
      token.value = res.data.access_token
      user.value = res.data.user
      localStorage.setItem('token', token.value)
    } catch (e) {
      console.error('注册失败:', e.response?.status, e.message)
      throw e
    }
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const res = await api.get('/auth/me')
      user.value = res.data
    } catch (e) {
      if (e.response?.status === 401) {
        logout()
      } else {
        console.warn('fetchUser 非 401 错误:', e.response?.status, e.message)
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
