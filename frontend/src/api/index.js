/**
 * Axios 实例封装
 *
 * - 自动从 localStorage 注入 Bearer Token
 * - 401 响应时清除 token 并通过 router 跳转登录页 (防重复跳转)
 * - 成功响应时自动重置重定向标志
 */
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

let isRedirecting = false
let _router = null

export function setAxiosRouter(router) {
  _router = router
}

// 请求拦截器 — 自动附加 Authorization 头
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 — 成功重置标志，401 时跳转登录
api.interceptors.response.use(
  (res) => {
    isRedirecting = false
    return res
  },
  (err) => {
    if (err.response?.status === 401 && !isRedirecting) {
      isRedirecting = true
      localStorage.removeItem('token')
      if (_router) {
        _router.push('/login')
      } else {
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  },
)

export default api
