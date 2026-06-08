<template>
  <div class="marker-overlay" v-if="marker" @click.self="$emit('close')" @keydown.escape="$emit('close')">
    <div class="marker-card" role="dialog" aria-modal="true" :aria-label="marker.name">
      <button class="close-btn" @click="$emit('close')" aria-label="关闭">&times;</button>
      <h3>{{ marker.name }}</h3>
      <span class="category-tag" :style="{ background: categoryColor }">
        {{ categoryName }}
      </span>
      <p v-if="marker.description" class="desc">{{ marker.description }}</p>
      <p class="coords">坐标: ({{ marker.x_coord }}, {{ marker.y_coord }})</p>
      <div v-if="images.length > 0" class="image-gallery">
        <img v-for="(url, i) in images" :key="i" :src="url" :alt="marker.name + ' 截图'" class="screenshot" @click="enlarged = enlarged === i ? null : i" />
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
/**
 * 标记点详情弹窗
 *
 * 显示标记名称、分类、描述、坐标及截图画廊。
 * 支持截图点击放大预览。
 * 通过 actions 插槽接收外部操作按钮（如编辑/删除）。
 */
import { ref, computed } from 'vue'

const props = defineProps({
  marker: { type: Object, default: null },
  categoryName: { type: String, default: '' },
  categoryColor: { type: String, default: '#3388ff' },
})

defineEmits(['close'])

const enlarged = ref(null)                      // 当前放大的截图索引（null=未放大）
const images = computed(() => props.marker?.images || [])
</script>

<style scoped>
.marker-overlay {
  position: fixed; inset: 0; background: rgba(8,8,18,0.5);
  z-index: 1000; display: flex; align-items: center; justify-content: center;
}
.marker-card {
  background: var(--bg-surface); color: var(--text-primary);
  border: 1px solid var(--border-gold); border-radius: var(--radius-sm);
  padding: 24px; max-width: 360px; width: 90%; position: relative;
  box-shadow: var(--shadow-gold);
}
.close-btn {
  position: absolute; top: 8px; right: 12px;
  background: none; border: none; color: var(--text-muted);
  font-size: 22px; cursor: pointer; line-height: 1;
}
.close-btn:hover { color: var(--gold); }
.marker-card h3 { font-family: var(--font-display); font-size: 17px; margin-bottom: 8px; color: var(--gold); letter-spacing: 0.04em; }
.category-tag {
  display: inline-block; font-size: 11px; padding: 2px 10px;
  border-radius: 2px; color: #fff; margin-bottom: 10px;
  font-weight: 600; letter-spacing: 0.05em;
}
.desc { font-size: 14px; color: var(--text-secondary); margin: 8px 0; line-height: 1.6; }
.coords { font-size: 12px; color: var(--text-muted); margin-top: 6px; }
.image-gallery { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
.screenshot { width: calc(50% - 3px); height: 80px; object-fit: cover; border-radius: var(--radius-sm); cursor: pointer; border: 1px solid var(--border); }
.screenshot:hover { opacity: 0.85; }
.enlarged-overlay {
  position: fixed; inset: 0; background: rgba(8,8,18,0.9);
  display: flex; align-items: center; justify-content: center;
  z-index: 2000; cursor: pointer;
}
.enlarged-img { max-width: 90vw; max-height: 90vh; border-radius: var(--radius-sm); }
.action-bar { display: flex; gap: 8px; margin-top: 16px; justify-content: flex-end; }
.action-bar :deep(.action-btn) {
  padding: 6px 16px; border: none; border-radius: var(--radius-sm);
  font-size: 13px; cursor: pointer; font-family: var(--font-body);
  transition: opacity var(--transition);
}
.action-bar :deep(.action-btn.edit) { background: var(--gold); color: var(--bg-deep); }
.action-bar :deep(.action-btn.edit):hover { opacity: 0.85; }
.action-bar :deep(.action-btn.delete) { background: var(--danger); color: #fff; }
.action-bar :deep(.action-btn.delete):hover { background: var(--danger-hover); }
</style>
