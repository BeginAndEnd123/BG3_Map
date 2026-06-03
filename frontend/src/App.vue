<template>
  <div id="map-app">
    <NavBar />
    <router-view />
  </div>
</template>

<script setup>
/**
 * 根组件 — 布置导航栏和路由视图
 *
 * 挂载时自动发起 fetchUser 请求恢复登录状态。
 */
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import NavBar from './components/NavBar.vue'

const authStore = useAuthStore()

onMounted(() => {
  authStore.fetchUser()  // 刷新用户 token，恢复登录态
})
</script>

<style>
/* 全局重置：填充视口、flex 列布局、统一字体 */
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app, #map-app { width: 100%; height: 100%; }
body { font-family: "Microsoft YaHei", sans-serif; }
#map-app { display: flex; flex-direction: column; }
</style>
