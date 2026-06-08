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
  background: linear-gradient(180deg, #141425 0%, #0e0e1d 100%);
  padding: 18px 16px;
  overflow-y: auto;
  border-right: 1px solid var(--border);
  box-shadow: 3px 0 30px rgba(0,0,0,0.4), inset -1px 0 0 rgba(200,164,78,0.04);
  display: flex; flex-direction: column; gap: 2px;
}</style>
