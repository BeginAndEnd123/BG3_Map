/**
 * Vue Router 路由配置
 *
 * 包含路由守卫：未登录用户只能访问登录/注册页，已登录用户自动跳转首页。
 */
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import NotFoundView from '../views/NotFoundView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/register', name: 'register', component: RegisterView },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView },
]

// 无需登录即可访问的路由
const WHITE_LIST = ['login', 'register', 'not-found']

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 全局前置守卫 — 验证 token 格式并且未登录重定向到登录页
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  const hasValidToken = token && token.split('.').length === 3
  if (WHITE_LIST.includes(to.name)) {
    if (hasValidToken) return next({ name: 'home' })
    return next()
  }
  if (!hasValidToken) return next({ name: 'login' })
  next()
})

export default router
