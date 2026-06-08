<template>
  <div id="map-app">
    <NavBar />
    <router-view />
    <div v-if="hasError" class="global-error-overlay">
      <div class="global-error-card">
        <p>应用发生错误，请尝试刷新页面</p>
        <button @click="hasError = false">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 根组件 — 布置导航栏和路由视图
 *
 * 挂载时自动发起 fetchUser 请求恢复登录状态。
 */
import { onMounted, onErrorCaptured, ref } from 'vue'
import { useAuthStore } from './stores/auth'
import NavBar from './components/NavBar.vue'

const authStore = useAuthStore()
const hasError = ref(false)

onErrorCaptured((err) => {
  console.error('全局错误捕获:', err)
  hasError.value = true
  return false
})

onMounted(() => {
  authStore.fetchUser()
})
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app, #map-app { width: 100%; height: 100%; }
#map-app { display: flex; flex-direction: column; }

.global-error-overlay {
  position: fixed; inset: 0; background: rgba(8,8,18,0.7); z-index: 9999;
  display: flex; align-items: center; justify-content: center;
}
.global-error-card {
  background: var(--bg-surface); border: 1px solid var(--border-gold);
  border-radius: var(--radius-sm); padding: 32px 40px; text-align: center;
  box-shadow: var(--shadow-gold);
}
.global-error-card p {
  color: var(--text-primary); font-size: 16px; margin-bottom: 20px;
}
.global-error-card button {
  padding: 8px 24px; border: 1px solid var(--gold); border-radius: var(--radius-sm);
  background: transparent; color: var(--gold); cursor: pointer;
  font-family: var(--font-body); font-size: 14px;
  transition: all var(--transition);
}
.global-error-card button:hover { background: var(--gold); color: var(--bg-deep); }
</style>
