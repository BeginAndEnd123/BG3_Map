<template>
  <div class="map-page">
    <SidePanel>
      <h2>博德之门3 地图</h2>

      <div class="region-select">
        <h3>选择区域</h3>
        <select v-model="currentRegionId" @change="onRegionChange">
          <option v-for="r in mapStore.regions" :key="r.id" :value="r.id">
            {{ r.name }}
          </option>
        </select>
      </div>

      <div class="category-filter">
        <h3>分类筛选</h3>
        <label v-for="c in mapStore.categories" :key="c.id" class="category-item">
          <input
            type="checkbox"
            :value="c.id"
            v-model="selectedCategoryIds"
            @change="loadMarkers"
          />
          <span :style="{ color: c.color }">{{ c.name }}</span>
        </label>
      </div>

      <div class="search-box">
        <h3>搜索标记</h3>
        <input
          type="text"
          v-model="keyword"
          placeholder="输入标记名称..."
          @input="loadMarkers"
        />
      </div>

      <div class="stats">
        <h3>统计</h3>
        <p>标记总数：{{ mapStore.markers.length }}</p>
      </div>

      <button
        v-if="isAdmin"
        class="add-btn"
        @click="showAddForm = true"
      >
        + 新增标记
      </button>
    </SidePanel>

    <div class="map-wrapper">
      <MapContainer
        ref="mapRef"
        :tile-url="tileUrl"
        :markers="mapStore.markers"
        :categories="mapStore.categories"
        @marker-click="onMarkerClick"
      />

      <div class="loading-mask" v-if="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>
    </div>

    <MarkerPopup
      v-if="selectedMarker"
      :marker="selectedMarker"
      :category-name="selectedCategoryName"
      :category-color="selectedCategoryColor"
      @close="selectedMarker = null"
    >
      <template #actions v-if="isAdmin">
        <button class="action-btn edit" @click="onEditMarker(selectedMarker)">编辑</button>
        <button class="action-btn delete" @click="onDeleteMarker(selectedMarker.id)">删除</button>
      </template>
    </MarkerPopup>

    <MarkerForm
      v-if="showAddForm || editingMarker"
      :marker="editingMarker"
      :categories="mapStore.categories"
      :region-id="currentRegionId"
      @close="closeForm"
      @submit="onFormSubmit"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMapStore } from '../stores/map'
import { useAuthStore } from '../stores/auth'
import SidePanel from '../components/SidePanel.vue'
import MapContainer from '../components/MapContainer.vue'
import MarkerPopup from '../components/MarkerPopup.vue'
import MarkerForm from '../components/MarkerForm.vue'

const mapStore = useMapStore()
const authStore = useAuthStore()
const mapRef = ref(null)
const currentRegionId = ref(null)
const selectedCategoryIds = ref([])
const keyword = ref('')
const selectedMarker = ref(null)
const loading = ref(false)
const showAddForm = ref(false)
const editingMarker = ref(null)

const isAdmin = computed(() => authStore.user?.is_admin)

const tileUrl = computed(() => {
  return mapStore.currentRegion?.tile_url || ''
})

const selectedCategoryName = computed(() => {
  if (!selectedMarker.value) return ''
  const cat = mapStore.categories.find(c => c.id === selectedMarker.value.category_id)
  return cat?.name || ''
})

const selectedCategoryColor = computed(() => {
  if (!selectedMarker.value) return '#3388ff'
  const cat = mapStore.categories.find(c => c.id === selectedMarker.value.category_id)
  return cat?.color || '#3388ff'
})

async function loadMarkers() {
  loading.value = true
  try {
    const params = { region_id: currentRegionId.value }
    if (selectedCategoryIds.value.length > 0) {
      params.category_id = selectedCategoryIds.value.join(',')
    }
    if (keyword.value) {
      params.keyword = keyword.value
    }
    await mapStore.fetchMarkers(params)
  } catch {
    console.error('加载标记失败')
  } finally {
    loading.value = false
  }
}

function onRegionChange() {
  const region = mapStore.regions.find((r) => r.id === currentRegionId.value)
  if (region) {
    mapStore.setRegion(region)
    loadMarkers()
  }
}

function onMarkerClick(marker) {
  selectedMarker.value = marker
}

function closeForm() {
  showAddForm.value = false
  editingMarker.value = null
}

function onEditMarker(marker) {
  editingMarker.value = { ...marker }
  selectedMarker.value = null
}

async function onFormSubmit(data) {
  try {
    if (editingMarker.value) {
      await mapStore.editMarker(editingMarker.value.id, data)
    } else {
      await mapStore.addMarker(data)
    }
    closeForm()
  } catch {
    alert('操作失败，请检查权限')
  }
}

async function onDeleteMarker(id) {
  if (!confirm('确认删除该标记？')) return
  try {
    await mapStore.removeMarker(id)
    selectedMarker.value = null
  } catch {
    alert('删除失败，请检查权限')
  }
}

onMounted(async () => {
  await Promise.all([
    mapStore.fetchRegions(),
    mapStore.fetchCategories(),
  ])
  if (mapStore.regions.length > 0) {
    currentRegionId.value = mapStore.regions[0].id
    mapStore.setRegion(mapStore.regions[0])
  }
  loadMarkers()
})
</script>

<style scoped>
.map-page {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar :deep(h2) {
  font-size: 20px;
  margin-bottom: 20px;
  color: #ffd700;
}

.sidebar :deep(h3) {
  font-size: 14px;
  margin: 12px 0 6px;
  color: #aaa;
}

.region-select select {
  width: 100%;
  padding: 8px;
  border: 1px solid #444;
  border-radius: 4px;
  background: #16213e;
  color: #eee;
  font-size: 14px;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 4px 0;
  cursor: pointer;
  font-size: 13px;
}

.search-box input {
  width: 100%;
  padding: 8px;
  border: 1px solid #444;
  border-radius: 4px;
  background: #16213e;
  color: #eee;
  font-size: 13px;
}

.stats {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #333;
  font-size: 13px;
}

.add-btn {
  width: 100%;
  margin-top: 16px;
  padding: 10px;
  border: none;
  border-radius: 4px;
  background: #ffd700;
  color: #1a1a2e;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
}
.add-btn:hover { background: #ffed4a; }

.map-wrapper {
  flex: 1;
  position: relative;
}

.loading-mask {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.3);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 999;
  color: #fff;
  font-size: 14px;
  gap: 12px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255,255,255,0.3);
  border-top-color: #ffd700;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>

<style scoped>
.map-page {
  display: flex;
  width: 100%;
  height: 100vh;
}

.sidebar :deep(h2) {
  font-size: 20px;
  margin-bottom: 20px;
  color: #ffd700;
}

.sidebar :deep(h3) {
  font-size: 14px;
  margin: 12px 0 6px;
  color: #aaa;
}

.region-select select {
  width: 100%;
  padding: 8px;
  border: 1px solid #444;
  border-radius: 4px;
  background: #16213e;
  color: #eee;
  font-size: 14px;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 4px 0;
  cursor: pointer;
  font-size: 13px;
}

.search-box input {
  width: 100%;
  padding: 8px;
  border: 1px solid #444;
  border-radius: 4px;
  background: #16213e;
  color: #eee;
  font-size: 13px;
}

.stats {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #333;
  font-size: 13px;
}

.map-wrapper {
  flex: 1;
  position: relative;
}

.loading-mask {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.3);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 999;
  color: #fff;
  font-size: 14px;
  gap: 12px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255,255,255,0.3);
  border-top-color: #ffd700;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
