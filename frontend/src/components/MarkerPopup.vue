<template>
  <div class="marker-overlay" v-if="marker" @click.self="$emit('close')">
    <div class="marker-card">
      <button class="close-btn" @click="$emit('close')">&times;</button>
      <h3>{{ marker.name }}</h3>
      <span class="category-tag" :style="{ background: categoryColor }">
        {{ categoryName }}
      </span>
      <p v-if="marker.description" class="desc">{{ marker.description }}</p>
      <p class="coords">坐标: ({{ marker.x_coord }}, {{ marker.y_coord }})</p>
      <div v-if="images.length > 0" class="image-gallery">
        <img v-for="(url, i) in images" :key="i" :src="url" alt="截图" class="screenshot" @click="enlarged = enlarged === i ? null : i" />
        <div v-if="enlarged !== null" class="enlarged-overlay" @click="enlarged = null">
          <img :src="images[enlarged]" class="enlarged-img" />
        </div>
      </div>
      <div class="action-bar" v-if="$slots.actions">
        <slot name="actions" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'



const props = defineProps({
  marker: { type: Object, default: null },
  categoryName: { type: String, default: '' },
  categoryColor: { type: String, default: '#3388ff' },
})

defineEmits(['close'])

const enlarged = ref(null)
const images = computed(() => props.marker?.images || [])
</script>

<style scoped>
.marker-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.marker-card {
  background: #1a1a2e;
  color: #eee;
  border-radius: 8px;
  padding: 24px;
  max-width: 360px;
  width: 90%;
  position: relative;
  box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}
.close-btn {
  position: absolute;
  top: 8px; right: 12px;
  background: none;
  border: none;
  color: #888;
  font-size: 24px;
  cursor: pointer;
}
.close-btn:hover { color: #fff; }
.marker-card h3 { font-size: 18px; margin-bottom: 8px; color: #ffd700; }
.category-tag {
  display: inline-block;
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 10px;
  color: #fff;
  margin-bottom: 8px;
}
.desc { font-size: 14px; color: #ccc; margin: 8px 0; line-height: 1.5; }
.coords { font-size: 12px; color: #888; }
.image-gallery { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.screenshot { width: calc(50% - 3px); height: 80px; object-fit: cover; border-radius: 4px; cursor: pointer; }
.screenshot:hover { opacity: 0.85; }
.enlarged-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.85);
  display: flex; align-items: center; justify-content: center;
  z-index: 2000; cursor: pointer;
}
.enlarged-img { max-width: 90vw; max-height: 90vh; border-radius: 8px; }
.action-bar { display: flex; gap: 8px; margin-top: 16px; justify-content: flex-end; }
.action-bar :deep(.action-btn) {
  padding: 6px 16px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
}
.action-bar :deep(.action-btn.edit) { background: #ffd700; color: #1a1a2e; }
.action-bar :deep(.action-btn.delete) { background: #ff4444; color: #fff; }
</style>
