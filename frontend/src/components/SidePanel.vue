<template>
  <div class="side-panel">
    <slot />
  </div>
</template>

<script setup>
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
