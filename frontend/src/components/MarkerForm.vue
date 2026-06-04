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
        <div class="coord-info">
          坐标：{{ form.x_coord.toFixed(2) }}, {{ form.y_coord.toFixed(2) }}
        </div>
        <label>
          截图
          <input type="file" multiple accept="image/jpeg,image/png,image/gif,image/webp" @change="onFileSelect" />
          <div v-if="uploading" class="upload-status">上传中... ({{ uploadProgress }})</div>
          <div v-if="form.images.length > 0" class="image-grid">
            <div v-for="(url, i) in form.images" :key="i" class="image-item">
              <img :src="url" class="upload-preview" />
              <button type="button" class="img-remove" @click="removeImage(i)">&times;</button>
            </div>
          </div>
          <div v-if="uploadError" class="form-error">{{ uploadError }}</div>
        </label>

        <div class="target-section">
          <label class="target-toggle">
            <input type="checkbox" v-model="hasTarget" />
            传送目标（点击时跳转）
          </label>
          <template v-if="hasTarget">
            <label>
              目标区域
              <select v-model="form.target_region_id" @change="onTargetRegionChange">
                <option v-for="r in regions" :key="r.id" :value="r.id">{{ r.name }}</option>
              </select>
            </label>
            <label>
              目标地图
              <select v-model="form.target_map_name">
                <option v-for="m in targetMaps" :key="m.name" :value="m.name">{{ m.name }}</option>
              </select>
            </label>
            <div class="coord-row">
              <label>目标 X <input type="number" step="0.01" v-model.number="form.target_x" /></label>
              <label>目标 Y <input type="number" step="0.01" v-model.number="form.target_y" /></label>
            </div>
          </template>
        </div>

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
/**
 * 标记点表单 — 支持新增/编辑模式
 *
 * 功能：
 * - 填写名称、分类、描述、坐标
 * - 上传截图（逐个文件异步上传）
 * - 配置传送目标（选择目标区域和地图，输入坐标）
 * - 编辑模式下预填充已有数据
 */
import { ref, reactive, onMounted, watch } from 'vue'
import api from '../api/index'
import { getMaps } from '../api/maps'

const props = defineProps({
  marker: { type: Object, default: null },           // 编辑时传入的标记对象
  categories: { type: Array, default: () => [] },
  regions: { type: Array, default: () => [] },
  regionId: { type: Number, default: null },          // 当前区域 ID
  initialCoords: { type: Object, default: null },     // 拾取模式选择的坐标
})

const emit = defineEmits(['close', 'submit'])

const isEdit = !!props.marker                           // 是否为编辑模式
const submitting = ref(false)
const error = ref('')
const uploading = ref(false)
const uploadProgress = ref('')
const uploadError = ref('')
const targetMaps = ref([])                              // 目标区域下的子地图列表
const hasTarget = ref(false)                            // 是否启用传送目标配置
const chapterKeys = ['chapter0', 'chapter1', 'chapter2', 'chapter3', 'chapter4']

const form = reactive({
  name: '',
  category_id: props.categories[0]?.id || '',
  description: '',
  x_coord: 0,
  y_coord: 0,
  images: [],
  target_region_id: null,
  target_map_name: '',
  target_x: null,
  target_y: null,
})

onMounted(async () => {
  /** 编辑模式预填充已有数据，新增模式则使用拾取坐标 */
  if (props.marker) {
    form.name = props.marker.name
    form.category_id = props.marker.category_id
    form.description = props.marker.description || ''
    form.x_coord = Number(props.marker.x_coord)
    form.y_coord = Number(props.marker.y_coord)
    form.images = props.marker.images || []
    form.target_region_id = props.marker.target_region_id
    form.target_map_name = props.marker.target_map_name || ''
    form.target_x = props.marker.target_x
    form.target_y = props.marker.target_y
    hasTarget.value = !!props.marker.target_region_id
    if (hasTarget.value) await fetchTargetMaps()
  } else if (props.initialCoords) {
    form.x_coord = props.initialCoords.x
    form.y_coord = props.initialCoords.y
  }
})

watch(() => props.initialCoords, (coords) => {
  /** 拾取坐标变化时同步更新表单 */
  if (coords && !props.marker) {
    form.x_coord = coords.x
    form.y_coord = coords.y
  }
}, { deep: true })

async function onFileSelect(e) {
  /** 逐个上传选择的截图文件，追加到 images 列表 */
  const files = e.target.files
  if (!files || files.length === 0) return
  uploadError.value = ''
  for (let i = 0; i < files.length; i++) {
    uploading.value = true
    uploadProgress.value = `${i + 1}/${files.length}`
    const fd = new FormData()
    fd.append('file', files[i])
    try {
      const res = await api.post('/upload', fd)
      form.images.push(res.data.url)
    } catch (err) {
      uploadError.value = `${files[i].name} 上传失败`
    }
  }
  uploading.value = false
  uploadProgress.value = ''
}

async function fetchTargetMaps() {
  /** 根据目标区域加载其下的子地图列表 */
  if (!form.target_region_id) return
  const region = props.regions.find(r => r.id === form.target_region_id)
  if (!region) return
  const chapterKey = chapterKeys[region.sort_order] || ''
  if (!chapterKey) return
  try {
    const res = await getMaps({ chapter: chapterKey })
    targetMaps.value = res.data
  } catch {
    targetMaps.value = []
  }
}

async function onTargetRegionChange() {
  /** 切换目标区域时重置地图和坐标选择 */
  form.target_map_name = ''
  form.target_x = null
  form.target_y = null
  await fetchTargetMaps()
}

function removeImage(index) {
  /** 从 images 列表中移除指定索引的图片 */
  form.images.splice(index, 1)
}

async function onSubmit() {
  /** 提交表单，触发父组件处理创建或更新逻辑 */
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
.coord-info {
  font-size: 12px;
  color: #888;
  margin-bottom: 14px;
  padding: 6px 10px;
  background: #16213e;
  border-radius: 4px;
}
.upload-status { color: #888; font-size: 12px; margin-top: 4px; }
.image-grid { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.image-item { position: relative; width: 80px; height: 80px; }
.upload-preview { width: 100%; height: 100%; object-fit: cover; border-radius: 4px; }
.img-remove {
  position: absolute; top: -6px; right: -6px;
  width: 20px; height: 20px; border-radius: 50%;
  background: #ff4444; color: #fff; border: none;
  font-size: 14px; line-height: 1; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
}
.target-section { border-top: 1px solid #333; padding-top: 14px; margin-top: 14px; }
.target-toggle { display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 13px; color: #ffd700; }
.target-toggle input { width: auto; margin: 0; }
.coord-row { display: flex; gap: 10px; }
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
