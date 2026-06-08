/**
 * Axios 实例封装
 *
 * - 自动从 localStorage 注入 Bearer Token
 * - 401 响应时清除 token 并跳转登录页 (防重复跳转)
 */
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

let isRedirecting = false

// 请求拦截器 — 自动附加 Authorization 头
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 — 401 时重置登录态
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && !isRedirecting) {
      isRedirecting = true
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  },
)

export default api
