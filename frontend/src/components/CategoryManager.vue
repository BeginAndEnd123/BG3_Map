<template>
  <div class="overlay" v-if="visible" @click.self="onOverlayClose" @keydown.escape="onOverlayClose">
    <div class="card" ref="card" :style="cardStyle" role="dialog" aria-modal="true" aria-label="分类管理">
      <div class="card-header" @mousedown="onDragStart">
        <h3>分类管理</h3>
        <button class="close-btn" @click="$emit('close')" aria-label="关闭">&times;</button>
      </div>

      <form @submit.prevent="onAdd" class="add-form">
        <div class="form-row">
          <input v-model="form.name" placeholder="名称，如：商人、宝箱、NPC" required class="name-input" />
        </div>
        <div class="form-row">
          <label class="upload-btn">
            <input type="file" accept="image/svg+xml,image/png" hidden @change="onIconUpload" />
            {{ uploadingIcon ? '上传中...' : (form.icon ? '更换图标' : '上传图标（SVG/PNG，≤256KB）') }}
          </label>
        </div>
        <p v-if="!form.icon" class="icon-hint">请上传图标（SVG 或 PNG）</p>
        <p v-if="form.icon" class="icon-preview">
          <img :src="form.icon" class="preview-img" />
          <button type="button" class="clear-icon" @click="form.icon = ''">&times;</button>
        </p>
        <div class="form-row">
          <button type="submit" class="btn-add" :disabled="submitting || !form.icon">
            {{ submitting ? '提交中...' : (editingId ? '保存修改' : '添加分类') }}
          </button>
          <button v-if="editingId" type="button" class="btn-cancel-edit" @click="cancelEdit">取消</button>
        </div>
        <p v-if="error" class="error">{{ error }}</p>
      </form>

      <ul class="cat-list">
        <li v-for="c in categories" :key="c.id" class="cat-item">
          <span class="cat-name">{{ c.name }}</span>
          <span class="cat-icon">{{ c.icon || '—' }}</span>
          <button class="btn-edit" @click="startEdit(c)">编辑</button>
          <button class="btn-del" @click="onDelete(c)" :disabled="deleting === c.id">
            {{ deleting === c.id ? '...' : '删除' }}
          </button>
        </li>
      </ul>
      <p v-if="categories.length === 0" class="empty">暂无分类</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onBeforeUnmount } from 'vue'
import { createCategory, updateCategory, deleteCategory } from '../api/categories'
import api from '../api/index'

const props = defineProps({
  visible: { type: Boolean, default: false },
  categories: { type: Array, default: () => [] },
})

const emit = defineEmits(['close', 'refresh'])

const form = reactive({ name: '', icon: '' })
const error = ref('')
const submitting = ref(false)
const deleting = ref(null)
const uploadingIcon = ref(false)
const editingId = ref(null)

async function onAdd() {
  if (submitting.value) return
  error.value = ''
  if (!form.name.trim()) return
  if (!form.icon) {
    error.value = '请选择或上传图标'
    return
  }
  submitting.value = true
  try {
    if (editingId.value) {
      await updateCategory(editingId.value, { name: form.name.trim(), icon: form.icon })
    } else {
      await createCategory({ name: form.name.trim(), icon: form.icon, sort_order: props.categories.length })
    }
    cancelEdit()
    emit('refresh')
  } catch (e) {
    error.value = e.response?.data?.detail || '操作失败'
  } finally {
    submitting.value = false
  }
}

function startEdit(cat) {
  editingId.value = cat.id
  form.name = cat.name
  form.icon = cat.icon || ''
}

function cancelEdit() {
  editingId.value = null
  form.name = ''
  form.icon = ''
}

function onOverlayClose() {
  if (dragging.value) onDragEnd()
  emit('close')
}

async function onDelete(cat) {
  if (!confirm(`确认删除分类「${cat.name}」？`)) return
  deleting.value = cat.id
  try {
    await deleteCategory(cat.id)
    emit('refresh')
  } catch (e) {
    alert(e.response?.data?.detail || '删除失败')
  } finally {
    deleting.value = null
  }
}

async function onIconUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return
  if (file.size > 256 * 1024) {
    error.value = '图标文件不能超过 256KB'
    return
  }
  uploadingIcon.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const res = await api.post('/upload', fd)
    form.icon = res.data.url
  } catch {
    error.value = '图标上传失败'
  } finally {
    uploadingIcon.value = false
    e.target.value = ''
  }
}

// 拖拽
const card = ref(null)
const cardStyle = ref({})
const dragging = ref(false)
const offset = reactive({ x: 0, y: 0 })
let startX = 0, startY = 0

function onDragStart(e) {
  if (e.target.closest('button') || e.target.closest('input') || e.target.closest('select')) return
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

onBeforeUnmount(() => {
  document.removeEventListener('mousemove', onDragMove)
  document.removeEventListener('mouseup', onDragEnd)
})
</script>

<style scoped>
.overlay {
  position: fixed; inset: 0; background: rgba(8,8,18,0.5);
  z-index: 1100; display: flex; align-items: center; justify-content: center;
}
.card {
  background: var(--bg-surface); color: var(--text-primary);
  border: 1px solid var(--border-gold); border-radius: var(--radius-sm);
  width: 380px; max-width: 90%; max-height: 80vh;
  overflow-y: auto; box-shadow: var(--shadow-gold); position: relative;
}
.card-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px 0 20px; cursor: grab; user-select: none;
}
.card-header:active { cursor: grabbing; }
.card-header h3 {
  font-family: var(--font-display); font-size: 16px;
  color: var(--gold); letter-spacing: 0.06em; margin: 0;
}
.close-btn {
  background: none; border: none; color: var(--text-muted);
  font-size: 20px; cursor: pointer; padding: 0;
}
.close-btn:hover { color: var(--gold); }

.add-form { padding: 12px 20px; border-bottom: 1px solid var(--border); }
.form-row { display: flex; gap: 8px; margin-bottom: 8px; }
.name-input {
  width: 100%; padding: 5px 8px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  background: var(--bg-input); color: var(--text-primary);
  font-size: 13px; font-family: var(--font-body); outline: none;
}
.name-input:focus { border-color: var(--gold-dim); }
.btn-add {
  padding: 5px 16px; border: none; border-radius: var(--radius-sm);
  background: var(--gold); color: var(--bg-deep);
  font-size: 12px; font-weight: 600; cursor: pointer; font-family: var(--font-body);
}
.btn-add:hover { background: var(--gold-light); }
.btn-add:disabled { opacity: 0.4; cursor: not-allowed; }
.upload-btn {
  padding: 7px 10px; border: 1px dashed var(--border); border-radius: var(--radius-sm);
  color: var(--text-muted); font-size: 12px; cursor: pointer; font-family: var(--font-body);
  text-align: center; display: block;
  transition: all var(--transition);
}
.upload-btn:hover { border-color: var(--gold-dim); color: var(--gold); }
.icon-preview {
  display: flex; align-items: center; gap: 8px;
  font-size: 12px; color: var(--text-muted); margin: 4px 0;
}
.preview-img { width: 20px; height: 20px; object-fit: contain; }
.clear-icon {
  background: none; border: none; color: var(--text-muted);
  font-size: 16px; cursor: pointer; padding: 0; line-height: 1;
}
.clear-icon:hover { color: var(--danger); }
.icon-hint { font-size: 11px; color: var(--text-muted); margin: 2px 0 4px 0; }
.error { color: var(--danger); font-size: 12px; margin: 4px 0 0 0; }

.cat-list { list-style: none; padding: 8px 20px 16px 20px; }
.cat-item {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 0; border-top: 1px solid var(--border);
}
.cat-color {
  width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0;
  border: 1px solid rgba(255,255,255,0.2);
}
.cat-name { flex: 1; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cat-icon { font-size: 11px; color: var(--text-muted); max-width: 80px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.btn-del {
  padding: 2px 8px; border: none; border-radius: var(--radius-sm);
  background: transparent; color: var(--danger);
  font-size: 11px; cursor: pointer; font-family: var(--font-body);
}
.btn-del:hover { background: var(--danger); color: #fff; }
.btn-del:disabled { opacity: 0.3; cursor: not-allowed; }
.btn-edit {
  padding: 2px 8px; border: none; border-radius: var(--radius-sm);
  background: transparent; color: var(--gold-dim);
  font-size: 11px; cursor: pointer; font-family: var(--font-body);
}
.btn-edit:hover { color: var(--gold); }
.btn-cancel-edit {
  padding: 5px 12px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  background: transparent; color: var(--text-secondary);
  font-size: 12px; cursor: pointer; font-family: var(--font-body);
}
.btn-cancel-edit:hover { border-color: var(--text-secondary); color: var(--text-primary); }
.empty { font-size: 13px; color: var(--text-muted); text-align: center; padding: 16px 0; }
</style>
