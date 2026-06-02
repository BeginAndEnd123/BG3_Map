<template>
  <div id="map-app">
    <NavBar />
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import NavBar from './components/NavBar.vue'

const authStore = useAuthStore()

onMounted(() => {
  authStore.fetchUser()
})
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app, #map-app { width: 100%; height: 100%; }
body { font-family: "Microsoft YaHei", sans-serif; }
#map-app { display: flex; flex-direction: column; }
</style>
