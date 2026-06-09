/**
 * Vue Router 路由配置
 *
 * 路由守卫：登录/注册页已登录用户自动跳转首页；其余页面允许所有人访问（游客模式）。
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

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  const hasValidToken = token && token.split('.').length === 3

  // 登录/注册页：已登录用户自动跳转首页
  if (to.name === 'login' || to.name === 'register') {
    if (hasValidToken) return next({ name: 'home' })
    return next()
  }

  // 其他页面（首页、404）：允许所有人访问
  next()
})

export default router
