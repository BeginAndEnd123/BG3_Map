<template>
  <div class="marker-overlay" :class="{ transparent: transparent }" v-if="marker" @click.self="onOverlayClose" @keydown.escape="onOverlayClose">
    <div class="marker-card" :class="{ floating: transparent }" ref="card" :style="cardStyle" role="dialog" aria-modal="true" :aria-label="marker.name">
      <div class="popup-header" @mousedown="onDragStart">
        <h3>{{ marker.name }}</h3>
        <button class="close-btn" @click="$emit('close')" aria-label="关闭">&times;</button>
      </div>
      <span class="category-tag" :style="{ background: categoryColor }">
        {{ categoryName }}
      </span>
      <span v-if="marker.status === 'pending'" class="status-tag pending">待审核</span>
      <span v-else-if="marker.status === 'rejected'" class="status-tag rejected">已拒绝</span>
      <span v-if="isGenericWaypoint" class="status-tag waypoint-hint">通用传送点</span>
      <p v-if="marker.description" class="desc">{{ marker.description }}</p>
      <p class="coords">坐标: ({{ marker.x_coord }}, {{ marker.y_coord }})</p>
      <p v-if="marker.submitter_name" class="submitter">提交者: {{ marker.submitter_name }}</p>
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
import { ref, computed, reactive, watch, onBeforeUnmount } from 'vue'

const props = defineProps({
  marker: { type: Object, default: null },
  categoryName: { type: String, default: '' },
  categoryColor: { type: String, default: '#3388ff' },
  transparent: { type: Boolean, default: false },
  position: { type: Object, default: () => ({ left: '0px', top: '0px' }) },
})

const emit = defineEmits(['close'])

const enlarged = ref(null)
const images = computed(() => props.marker?.images || [])

const isGenericWaypoint = computed(() => {
  return props.categoryName === '传送点' && !props.marker?.target_region_id
})

const card = ref(null)
const cardStyle = ref({})
const dragging = ref(false)
const offset = reactive({ x: 0, y: 0 })
let startX = 0, startY = 0

watch(() => props.position, (pos) => {
  if (props.transparent && pos) {
    cardStyle.value = { left: pos.left, top: pos.top }
  }
}, { deep: true, immediate: true })

function onDragStart(e) {
  if (e.target.closest('button')) return
  e.preventDefault()
  dragging.value = true
  startX = e.clientX - offset.x
  startY = e.clientY - offset.y
  document.addEventListener('mousemove', onDragMove)
  document.addEventListener('mouseup', onDragEnd)
}

function onDragMove(e) {
  if (!dragging.value) return
  offset.x = e.clientX - startX
  offset.y = e.clientY - startY
  cardStyle.value = { transform: `translate(${offset.x}px, ${offset.y}px)` }
}

function onDragEnd() {
  dragging.value = false
  document.removeEventListener('mousemove', onDragMove)
  document.removeEventListener('mouseup', onDragEnd)
}

function onOverlayClose() {
  if (dragging.value) onDragEnd()
  emit('close')
}

onBeforeUnmount(() => {
  document.removeEventListener('mousemove', onDragMove)
  document.removeEventListener('mouseup', onDragEnd)
})
</script>

<style scoped>
.marker-overlay {
  position: fixed; inset: 0; background: rgba(8,8,18,0.5);
  z-index: 1000; display: flex; align-items: center; justify-content: center;
}
.marker-overlay.transparent { background: transparent; pointer-events: none; }
.marker-overlay.transparent .marker-card { pointer-events: auto; }
.marker-card.floating {
  position: fixed; margin: 0; z-index: 2000;
}
.marker-card {
  background: var(--bg-surface); color: var(--text-primary);
  border: 1px solid var(--border-gold); border-radius: var(--radius-sm);
  padding: 24px; max-width: 360px; width: 90%; position: relative;
  box-shadow: var(--shadow-gold); cursor: default;
}
.popup-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 8px; cursor: grab; user-select: none;
}
.popup-header:active { cursor: grabbing; }
.close-btn {
  background: none; border: none; color: var(--text-muted);
  font-size: 22px; cursor: pointer; line-height: 1; padding: 0; margin-left: 12px;
}
.close-btn:hover { color: var(--gold); }
.marker-card h3 { font-family: var(--font-display); font-size: 17px; color: var(--gold); letter-spacing: 0.04em; margin: 0; }
.category-tag {
  display: inline-block; font-size: 11px; padding: 2px 10px;
  border-radius: 2px; color: #fff; margin-bottom: 10px;
  font-weight: 600; letter-spacing: 0.05em;
}
.status-tag {
  display: inline-block; font-size: 10px; padding: 2px 8px;
  border-radius: 2px; margin-left: 6px; margin-bottom: 10px;
  font-weight: 600; letter-spacing: 0.05em; vertical-align: top;
}
.status-tag.pending { background: #6b4c1e; color: #e8a838; border: 1px solid #e8a838; }
.status-tag.rejected { background: #5c1a1a; color: #e06060; border: 1px solid #e06060; }
.status-tag.waypoint-hint { background: #1e3a5c; color: #60a0c0; border: 1px solid #60a0c0; }
.desc { font-size: 14px; color: var(--text-secondary); margin: 8px 0; line-height: 1.6; white-space: pre-wrap; }
.coords { font-size: 12px; color: var(--text-muted); margin-top: 6px; }
.submitter { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
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
.action-bar :deep(.action-btn.edit):hover { opacity: 0.85; }
.action-bar :deep(.action-btn.delete) { background: var(--danger); color: #fff; }
.action-bar :deep(.action-btn.delete):hover { background: var(--danger-hover); }
.action-bar :deep(.action-btn.teleport) { background: var(--magic, #8b67c0); color: #fff; }
.action-bar :deep(.action-btn.teleport):hover { opacity: 0.85; }
</style>
