<template>
  <div class="not-found">
    <h1>404</h1>
    <p>页面不存在</p>
    <router-link to="/">返回首页</router-link>
  </div>
</template>

<style scoped>
.not-found {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  flex: 1; background: var(--bg-deep); gap: 8px;
}
.not-found h1 {
  font-family: var(--font-display); font-size: 96px; color: var(--gold);
  text-shadow: 0 0 40px rgba(200,164,78,0.2);
}
.not-found p { font-size: 18px; color: var(--text-secondary); }
.not-found a {
  color: var(--gold); font-size: 15px; text-decoration: none;
  margin-top: 16px; padding: 8px 24px;
  border: 1px solid var(--border-gold); border-radius: var(--radius-sm);
  transition: all var(--transition);
}
.not-found a:hover { background: var(--gold); color: var(--bg-deep); }
</style>
