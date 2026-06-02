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

const WHITE_LIST = ['login', 'register']

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (WHITE_LIST.includes(to.name)) {
    if (token) return next({ name: 'home' })
    return next()
  }
  if (!token) return next({ name: 'login' })
  next()
})

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
