<template>
  <div class="marker-popup" v-if="marker">
    <h3>{{ marker.name }}</h3>
    <p v-if="marker.description">{{ marker.description }}</p>
    <p class="coords">坐标: ({{ marker.x_coord }}, {{ marker.y_coord }})</p>
    <img v-if="marker.screenshot" :src="marker.screenshot" alt="截图" class="screenshot" />
  </div>
</template>

<script setup>
defineProps({
  marker: { type: Object, default: null },
})
</script>

<style scoped>
.marker-popup { padding: 8px; max-width: 250px; }
.marker-popup h3 { font-size: 16px; margin-bottom: 8px; }
.marker-popup p { font-size: 13px; color: #666; margin: 4px 0; }
.coords { color: #999; font-size: 12px; }
.screenshot { width: 100%; margin-top: 8px; border-radius: 4px; }
</style>
