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
const WHITE_LIST = ['login', 'register']

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 全局前置守卫 — 未登录重定向到登录页
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (WHITE_LIST.includes(to.name)) {
    if (token) return next({ name: 'home' })   // 已登录则跳转首页
    return next()
  }
  if (!token) return next({ name: 'login' })
  next()
})

export default router
