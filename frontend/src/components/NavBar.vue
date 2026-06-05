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
  display: flex; align-items: center; justify-content: space-between;
  height: 46px; padding: 0 22px;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border);
  box-shadow: 0 1px 12px rgba(0,0,0,0.3);
}
.brand {
  font-family: var(--font-display);
  font-size: 15px; font-weight: 600; letter-spacing: 0.06em;
  color: var(--gold);
}
.nav-right { display: flex; align-items: center; gap: 16px; }
.user-info { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.user-name { color: var(--text-primary); }
.admin-badge {
  font-size: 10px; font-weight: 600; letter-spacing: 0.05em;
  background: var(--gold); color: var(--bg-deep);
  padding: 1px 7px; border-radius: 2px;
}
.logout-btn {
  padding: 4px 14px; font-size: 13px;
  border: 1px solid rgba(200,164,78,0.25); border-radius: var(--radius-sm);
  background: transparent; color: var(--text-secondary); cursor: pointer;
  transition: all var(--transition);
}
.logout-btn:hover { border-color: var(--gold); color: var(--gold); }
</style>
