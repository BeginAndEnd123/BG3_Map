<template>
  <div class="side-panel">
    <slot />
  </div>
</template>

<script setup>
/**
 * 侧边面板容器 — 为左侧栏提供统一的样式和滚动支持
 * 通过默认插槽接收子内容。
 */
</script>

<style scoped>
.side-panel {
  width: 280px;
  min-width: 280px;
  background: #1a1a2e;
  color: #eee;
  padding: 20px;
  overflow-y: auto;
}
</style>
