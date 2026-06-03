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

      <div class="map-select" v-if="mapStore.maps.length > 0">
        <h3>选择地图</h3>
        <select v-model="selectedMapName" @change="onMapChange">
          <option v-for="m in mapStore.maps" :key="m.name" :value="m.name">
            {{ m.name }}
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
          @input="onSearchInput"
          @focus="showSearchResults = true"
          @blur="onSearchBlur"
        />
        <ul v-if="showSearchResults && searchResults.length > 0" class="search-list">
          <li v-for="m in searchResults" :key="m.id" @mousedown.prevent="onSearchSelect(m)">
            <span class="sr-name">{{ m.name }}</span>
            <span class="sr-region">{{ m.region?.name || '' }}</span>
          </li>
        </ul>
      </div>

      <div class="stats">
        <h3>统计</h3>
        <p>标记总数：{{ mapStore.markers.length }}</p>
      </div>

      <div class="recent-markers" v-if="recentMarkers.length > 0">
        <h3>最新添加</h3>
        <ul>
          <li v-for="m in recentMarkers" :key="m.id">
            <span class="recent-name">{{ m.name }}</span>
            <span class="recent-region">{{ m.region?.name || '' }}</span>
          </li>
        </ul>
      </div>

      <button
        v-if="isAdmin"
        class="add-btn"
        @click="onStartAdd"
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
        :pick-mode="pickMode"
        :temp-marker="tempMarker"
        @marker-click="onMarkerClick"
        @map-pick="onMapPick"
      />

      <div class="loading-mask" v-if="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div class="pick-overlay" v-if="pickMode">
        <div class="pick-hint">拖动标记到目标位置</div>
        <button class="confirm-btn" @click="onConfirmPosition">确认位置</button>
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
      :initial-coords="pickerCoords"
      @close="closeForm"
      @submit="onFormSubmit"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useMapStore } from '../stores/map'
import { useAuthStore } from '../stores/auth'
import { getMaps } from '../api/maps'
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
const selectedMapName = ref('')
const recentMarkers = ref([])
const pickMode = ref(false)
const showSearchResults = ref(false)
const searchResults = ref([])

const DEFAULT_MAP = {
  1: '鹦鹉螺坠毁区域',
  2: '瑰晨修道院',
  3: '幽影诅咒之地',
  4: '飞龙关',
}
const tempMarker = ref(null)
const pickerCoords = ref(null)

const isAdmin = computed(() => authStore.user?.is_admin)

const tileUrl = computed(() => {
  return mapStore.currentMap?.tile_url || ''
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

async function onSearchInput() {
  showSearchResults.value = true
  if (!keyword.value) {
    searchResults.value = []
    return
  }
  try {
    const res = await getMarkers({ keyword: keyword.value })
    searchResults.value = res.data
  } catch {
    searchResults.value = []
  }
}

function onSearchBlur() {
  setTimeout(() => { showSearchResults.value = false }, 200)
}

function onSearchSelect(marker) {
  showSearchResults.value = false
  keyword.value = marker.name
  selectedMarker.value = marker
  mapRef.value?.flyTo(Number(marker.x_coord), Number(marker.y_coord), 5)
  mapRef.value?.highlightMarker(Number(marker.x_coord), Number(marker.y_coord))
}

async function fetchMaps() {
  const region = mapStore.currentRegion
  if (!region) return
  const chapterKey = mapStore.getChapterKey(region.sort_order)
  if (!chapterKey) return
  try {
    const res = await getMaps({ chapter: chapterKey })
    mapStore.maps = res.data
    if (res.data.length > 0) {
      const preferred = DEFAULT_MAP[region.sort_order]
      const mapItem = res.data.find(m => m.name === preferred) || res.data[0]
      selectedMapName.value = mapItem.name
      mapStore.setMap(mapItem)
    }
  } catch {
    console.error('加载地图列表失败')
  }
}

async function fetchRecentMarkers() {
  try {
    const res = await getMarkers({ sort_by: 'created_at', limit: 5 })
    recentMarkers.value = res.data
  } catch {
    console.error('加载最新标记失败')
  }
}

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
    fetchMaps()
    loadMarkers()
  }
}

function onMapChange() {
  const mapItem = mapStore.maps.find(m => m.name === selectedMapName.value)
  if (mapItem) mapStore.setMap(mapItem)
}

function onMarkerClick(marker) {
  selectedMarker.value = marker
}

function onStartAdd() {
  pickMode.value = true
  tempMarker.value = { x: 0, y: 0 }
  pickerCoords.value = null
  showAddForm.value = false
}

function onMapPick(coords) {
  tempMarker.value = coords
  pickerCoords.value = coords
}

function onConfirmPosition() {
  if (!tempMarker.value) return
  pickerCoords.value = { ...tempMarker.value }
  showAddForm.value = true
}

function closeForm() {
  showAddForm.value = false
  editingMarker.value = null
  pickMode.value = false
  tempMarker.value = null
  pickerCoords.value = null
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
    fetchMaps()
  }
  loadMarkers()
  fetchRecentMarkers()
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

.search-box {
  position: relative;
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
.search-list {
  position: absolute;
  top: 100%; left: 0; right: 0;
  background: #1a1a2e;
  border: 1px solid #444;
  border-top: none;
  border-radius: 0 0 4px 4px;
  list-style: none;
  max-height: 200px;
  overflow-y: auto;
  z-index: 100;
}
.search-list li {
  padding: 8px 10px;
  cursor: pointer;
  font-size: 13px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.search-list li:hover { background: #2a2a4e; }
.sr-name { color: #eee; }
.sr-region { color: #888; font-size: 11px; }

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

.recent-markers { margin-top: 16px; padding-top: 12px; border-top: 1px solid #333; }
.recent-markers ul { list-style: none; margin-top: 6px; }
.recent-markers li {
  display: flex; justify-content: space-between; align-items: center;
  padding: 4px 0; font-size: 12px; border-bottom: 1px solid #2a2a2a;
}
.recent-markers li:last-child { border-bottom: none; }
.recent-name { color: #eee; }
.recent-region { color: #888; font-size: 11px; }

.map-wrapper {
  flex: 1;
  position: relative;
  background: #000;
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

.pick-overlay {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  z-index: 1000;
}
.pick-hint {
  background: rgba(0,0,0,0.75);
  color: #ffd700;
  padding: 8px 20px;
  border-radius: 6px;
  font-size: 14px;
  white-space: nowrap;
}
.confirm-btn {
  padding: 10px 32px;
  border: none;
  border-radius: 6px;
  background: #ffd700;
  color: #1a1a2e;
  font-size: 15px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 2px 12px rgba(0,0,0,0.4);
}
.confirm-btn:hover { background: #ffed4a; }

.map-select select {
  width: 100%;
  padding: 8px;
  border: 1px solid #444;
  border-radius: 4px;
  background: #16213e;
  color: #eee;
  font-size: 14px;
  margin-top: 2px;
}
</style>
