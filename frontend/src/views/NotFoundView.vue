<template>
  <div class="not-found">
    <h1>404</h1>
    <p>页面不存在</p>
    <router-link to="/">返回首页</router-link>
  </div>
</template>

<!-- 简单 404 页面，无逻辑 -->
<style scoped>
.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #eee;
  background: #0f0f23;
}
.not-found h1 { font-size: 72px; color: #ffd700; margin-bottom: 8px; }
.not-found p { font-size: 18px; color: #888; margin-bottom: 24px; }
.not-found a { color: #ffd700; font-size: 14px; }
</style>
