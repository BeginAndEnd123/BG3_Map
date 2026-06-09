<template>
  <div class="review-overlay" v-if="visible" @keydown.escape="onOverlayClose">
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
            <button class="btn-approve" :disabled="reviewingId === m.id" @click.stop="onReview(m.id, 'approve')">通过</button>
            <button class="btn-reject" :disabled="reviewingId === m.id" @click.stop="onReview(m.id, 'reject')">拒绝</button>
          </div>
        </li>
      </ul>
      <p v-else class="empty-text">暂无待审核标记</p>

      <div v-if="totalPages > 1" class="pagination">
        <div class="page-row">
          <button :disabled="currentPage <= 1" @click="onPage(currentPage - 1)">‹</button>
          <template v-for="p in pages" :key="p">
            <button v-if="p !== '…'" :class="{ active: p === currentPage }" @click="onPage(p)">{{ p }}</button>
            <span v-else class="page-dots">…</span>
          </template>
          <button :disabled="currentPage >= totalPages" @click="onPage(currentPage + 1)">›</button>
        </div>
        <div class="page-goto">
          <input type="number" v-model.number="gotoPage" min="1" :max="totalPages" aria-label="跳转到指定页码" @keyup.enter="onGoto" />
          <button @click="onGoto">跳转</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onBeforeUnmount } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  pendingMarkers: { type: Array, default: () => [] },
  pendingCount: { type: Number, default: 0 },
  loading: { type: Boolean, default: false },
  currentPage: { type: Number, default: 1 },
  pageSize: { type: Number, default: 10 },
})

const emit = defineEmits(['close', 'approve', 'reject', 'locate', 'page-change'])

const reviewingId = ref(null)

function onReview(id, action) {
  if (reviewingId.value) return
  reviewingId.value = id
  emit(action, id)
}

const totalPages = computed(() => Math.max(1, Math.ceil(props.pendingCount / props.pageSize)))

const pages = computed(() => {
  const total = totalPages.value
  const cur = props.currentPage
  const result = []
  if (total <= 5) {
    for (let i = 1; i <= total; i++) result.push(i)
    return result
  }
  if (cur <= 3) {
    result.push(1); result.push(2); result.push(3); result.push(4)
    result.push('…'); result.push(total)
  } else if (cur >= total - 2) {
    result.push(1); result.push('…')
    for (let i = total - 3; i <= total; i++) result.push(i)
  } else {
    result.push(1); result.push('…')
    result.push(cur - 1); result.push(cur); result.push(cur + 1)
    result.push('…'); result.push(total)
  }
  return result
})

const gotoPage = ref(1)

function onPage(page) {
  if (page === props.currentPage) return
  gotoPage.value = page
  emit('page-change', page)
}

function onGoto() {
  const max = totalPages.value
  let p = Number(gotoPage.value)
  if (isNaN(p) || p < 1) p = 1
  if (p > max) p = max
  if (p !== props.currentPage) onPage(p)
}

defineExpose({ resetReview: () => { reviewingId.value = null } })

const card = ref(null)
const dragging = ref(false)
const offset = reactive({ x: 0, y: 0 })
let startX = 0
let startY = 0

const cardStyle = ref({})

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
  list-style: none; padding: 0 24px 4px 24px;
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

.pagination { margin: 8px 24px 16px 24px; }
.page-row { display: flex; align-items: center; justify-content: center; gap: 3px; }
.page-row button {
  background: var(--bg-input); color: var(--text-secondary);
  border: 1px solid var(--border); min-width: 24px; height: 24px;
  border-radius: var(--radius-sm); cursor: pointer; font-size: 12px;
  font-family: var(--font-body); transition: all var(--transition);
}
.page-row button:hover:not(:disabled):not(.active) { border-color: var(--gold-dim); color: var(--gold); }
.page-row button:disabled { opacity: 0.25; cursor: default; }
.page-row button.active { background: var(--gold); color: var(--bg-deep); border-color: var(--gold); font-weight: 600; }
.page-dots { color: var(--text-muted); font-size: 12px; min-width: 16px; text-align: center; }
.page-goto { display: flex; align-items: center; justify-content: flex-end; gap: 3px; margin-top: 3px; }
.page-goto input {
  width: 48px; height: 22px; padding: 0 3px;
  border: 1px solid var(--border); border-radius: var(--radius-sm);
  background: var(--bg-input); color: var(--text-primary);
  font-size: 11px; font-family: var(--font-body); text-align: center; outline: none;
}
.page-goto input:focus { border-color: var(--gold-dim); }
.page-goto input::-webkit-outer-spin-button,
.page-goto input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
.page-goto input[type="number"] { -moz-appearance: textfield; }
.page-goto button {
  min-width: 28px; height: 22px; font-size: 11px;
  background: var(--gold); color: var(--bg-deep);
  border: none; border-radius: var(--radius-sm); cursor: pointer;
  font-weight: 600; font-family: var(--font-body);
  transition: background var(--transition);
}
.page-goto button:hover { background: var(--gold-light); }
</style>
