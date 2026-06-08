/**
 * Vue 应用入口
 *
 * 挂载 Pinia 状态管理、Vue Router 路由，并导入 Leaflet 地图样式。
 * 渲染根组件 App.vue 到 #app 容器。
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import 'leaflet/dist/leaflet.css'
import App from './App.vue'
import router from './router'
import { setAxiosRouter } from './api/index'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
setAxiosRouter(router)
app.mount('#app')
