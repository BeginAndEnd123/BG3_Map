<template>
  <div class="navbar">
    <span class="brand">BG3 交互式地图</span>
    <div class="nav-right" v-if="authStore.user">
      <span class="user-info">
        <span class="user-name">{{ authStore.user.username }}</span>
        <span v-if="authStore.user.is_admin" class="admin-badge">管理员</span>
      </span>
      <button class="logout-btn" @click="onLogout">登出</button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

function onLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px;
  padding: 0 20px;
  background: #0f0f23;
  color: #eee;
  border-bottom: 1px solid #2a2a4a;
}
.brand { font-size: 15px; font-weight: bold; color: #ffd700; }
.nav-right { display: flex; align-items: center; gap: 16px; }
.user-info { display: flex; align-items: center; gap: 8px; font-size: 13px; }
.user-name { color: #eee; }
.admin-badge {
  font-size: 11px;
  background: #ffd700;
  color: #1a1a2e;
  padding: 2px 8px;
  border-radius: 8px;
  font-weight: bold;
}
.logout-btn {
  padding: 4px 14px;
  border: 1px solid #555;
  border-radius: 4px;
  background: transparent;
  color: #ccc;
  font-size: 13px;
  cursor: pointer;
}
.logout-btn:hover { background: #333; color: #fff; }
</style>
