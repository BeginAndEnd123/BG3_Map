<template>
  <div class="review-overlay" v-if="visible" @keydown.escape="$emit('close')">
    <div class="review-card" ref="card" :style="cardStyle" role="dialog" aria-modal="true" aria-label="审核管理">
      <div class="card-header" @mousedown="onDragStart">
        <h3>审核管理</h3>
        <button class="close-btn" @click="$emit('close')" aria-label="关闭">&times;</button>
      </div>
      <p class="review-count">待审核：{{ pendingCount }} 个</p>

      <div v-if="loading" class="review-loading">加载中...</div>

      <ul v-else-if="pendingMarkers.length > 0" class="review-list">
        <li v-for="m in pendingMarkers" :key="m.id" class="review-item">
          <div class="review-info">
            <span class="review-name" @click="$emit('locate', m)">{{ m.name }}</span>
            <span class="review-meta">
              {{ m.region?.name || '' }}
              <span v-if="m.map_name">· {{ m.map_name }}</span>
              · {{ m.submitter_name || '未知' }}
            </span>
          </div>
          <div class="review-actions">
            <button class="btn-approve" @click.stop="$emit('approve', m.id)">通过</button>
            <button class="btn-reject" @click.stop="$emit('reject', m.id)">拒绝</button>
          </div>
        </li>
      </ul>
      <p v-else class="empty-text">暂无待审核标记</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onBeforeUnmount } from 'vue'

defineProps({
  visible: { type: Boolean, default: false },
  pendingMarkers: { type: Array, default: () => [] },
  pendingCount: { type: Number, default: 0 },
  loading: { type: Boolean, default: false },
})

defineEmits(['close', 'approve', 'reject', 'locate'])

const card = ref(null)
const dragging = ref(false)
const offset = reactive({ x: 0, y: 0 })
let startX = 0
let startY = 0

const cardStyle = ref({})

function onDragStart(e) {
  if (e.target.tagName === 'BUTTON') return
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

onBeforeUnmount(() => {
  document.removeEventListener('mousemove', onDragMove)
  document.removeEventListener('mouseup', onDragEnd)
})
</script>

<style scoped>
.review-overlay {
  position: fixed; inset: 0; background: rgba(8,8,18,0.5);
  z-index: 1100; display: flex; align-items: center; justify-content: center;
}
.review-card {
  background: var(--bg-surface); color: var(--text-primary);
  border: 1px solid var(--border-gold); border-radius: var(--radius-sm);
  width: 440px; max-width: 90%; max-height: 80vh;
  overflow-y: auto; box-shadow: var(--shadow-gold);
  position: relative; cursor: default;
}
.card-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 24px 0 24px; cursor: grab; user-select: none;
}
.card-header:active { cursor: grabbing; }
.card-header h3 {
  font-family: var(--font-display); font-size: 17px;
  color: var(--gold); letter-spacing: 0.06em; margin: 0;
}
.close-btn {
  background: none; border: none; color: var(--text-muted);
  font-size: 22px; cursor: pointer; line-height: 1; padding: 0;
}
.close-btn:hover { color: var(--gold); }
.review-count {
  font-size: 13px; color: var(--warning, #e8a838);
  margin: 0; padding: 8px 24px 12px 24px;
}
.review-loading {
  font-size: 13px; color: var(--text-muted); text-align: center; padding: 20px 0;
}
.review-list {
  list-style: none; padding: 0 24px 16px 24px;
}
.review-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 0; border-top: 1px solid var(--border);
}
.review-info {
  flex: 1; display: flex; flex-direction: column; gap: 3px; min-width: 0;
}
.review-name {
  color: var(--text-primary); cursor: pointer; font-size: 14px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.review-name:hover { color: var(--gold); }
.review-meta {
  color: var(--text-muted); font-size: 11px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.review-actions { display: flex; gap: 6px; flex-shrink: 0; margin-left: 10px; }
.btn-approve, .btn-reject {
  padding: 4px 14px; border: none; border-radius: var(--radius-sm);
  font-size: 12px; cursor: pointer; font-family: var(--font-body);
  transition: opacity 0.15s;
}
.btn-approve { background: #2d6a4f; color: #d8f3dc; }
.btn-approve:hover { opacity: 0.85; }
.btn-reject { background: #6b2c2c; color: #f5d6d6; }
.btn-reject:hover { opacity: 0.85; }
.empty-text { font-size: 13px; color: var(--text-muted); text-align: center; padding: 16px 0; }
</style>
