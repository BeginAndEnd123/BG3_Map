<template>
  <div class="side-panel">
    <slot />
  </div>
</template>

<script setup>
</script>

<style scoped>
.side-panel {
  width: 280px; min-width: 280px;
  background: var(--bg-surface);
  padding: 20px;
  overflow-y: auto;
  border-right: 1px solid var(--border);
  box-shadow: 2px 0 20px rgba(0,0,0,0.2);
}
</style>
