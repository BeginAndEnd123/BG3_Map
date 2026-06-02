<template>
  <div class="form-overlay" @click.self="$emit('close')">
    <div class="form-card">
      <h3>{{ isEdit ? '编辑标记' : '新增标记' }}</h3>
      <form @submit.prevent="onSubmit">
        <label>
          名称
          <input v-model="form.name" required placeholder="标记名称" />
        </label>
        <label>
          分类
          <select v-model="form.category_id" required>
            <option v-for="c in categories" :key="c.id" :value="c.id">
              {{ c.name }}
            </option>
          </select>
        </label>
        <label>
          描述
          <textarea v-model="form.description" placeholder="可选描述" rows="3"></textarea>
        </label>
        <div class="coord-row">
          <label>
            X 坐标
            <input v-model.number="form.x_coord" type="number" step="0.01" required />
          </label>
          <label>
            Y 坐标
            <input v-model.number="form.y_coord" type="number" step="0.01" required />
          </label>
        </div>
        <label>
          截图 URL
          <input v-model="form.screenshot" placeholder="可选截图链接" />
        </label>
        <p v-if="error" class="form-error">{{ error }}</p>
        <div class="form-actions">
          <button type="button" class="btn-cancel" @click="$emit('close')">取消</button>
          <button type="submit" class="btn-submit" :disabled="submitting">
            {{ submitting ? '提交中...' : (isEdit ? '保存' : '创建') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

const props = defineProps({
  marker: { type: Object, default: null },
  categories: { type: Array, default: () => [] },
  regionId: { type: Number, default: null },
})

const emit = defineEmits(['close', 'submit'])

const isEdit = !!props.marker
const submitting = ref(false)
const error = ref('')

const form = reactive({
  name: '',
  category_id: props.categories[0]?.id || '',
  description: '',
  x_coord: 0,
  y_coord: 0,
  screenshot: '',
})

onMounted(() => {
  if (props.marker) {
    form.name = props.marker.name
    form.category_id = props.marker.category_id
    form.description = props.marker.description || ''
    form.x_coord = Number(props.marker.x_coord)
    form.y_coord = Number(props.marker.y_coord)
    form.screenshot = props.marker.screenshot || ''
  }
})

async function onSubmit() {
  submitting.value = true
  error.value = ''
  try {
    const payload = { ...form, region_id: props.regionId }
    emit('submit', payload)
  } catch {
    error.value = '提交失败，请重试'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.form-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 1100;
  display: flex;
  align-items: center;
  justify-content: center;
}
.form-card {
  background: #1a1a2e;
  color: #eee;
  border-radius: 8px;
  padding: 28px;
  width: 420px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}
.form-card h3 { font-size: 18px; margin-bottom: 20px; color: #ffd700; }
label {
  display: block;
  font-size: 13px;
  color: #aaa;
  margin-bottom: 14px;
}
label input, label select, label textarea {
  width: 100%;
  margin-top: 4px;
  padding: 8px;
  border: 1px solid #444;
  border-radius: 4px;
  background: #16213e;
  color: #eee;
  font-size: 14px;
}
label textarea { resize: vertical; }
.coord-row { display: flex; gap: 12px; }
.coord-row label { flex: 1; }
.form-error { color: #ff6b6b; font-size: 13px; margin: 8px 0; }
.form-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px; }
.btn-cancel, .btn-submit {
  padding: 8px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}
.btn-cancel { background: #444; color: #ccc; }
.btn-submit { background: #ffd700; color: #1a1a2e; font-weight: bold; }
.btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
