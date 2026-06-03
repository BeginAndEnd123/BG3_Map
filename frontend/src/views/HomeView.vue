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

      <div class="recent-markers">
        <h3>最新添加</h3>
        <ul v-if="recentMarkers.length > 0">
          <li v-for="m in recentMarkers" :key="m.id" @click="onRecentClick(m)">
            <span class="recent-name">{{ m.name }}</span>
            <span class="recent-region">{{ m.region?.name || '' }}</span>
          </li>
        </ul>
        <p v-else class="empty-text">暂无标记</p>
        <div v-if="recentTotal > 0" class="pagination">
          <button :disabled="recentPage <= 1" @click="onRecentPage(recentPage - 1)">‹</button>
          <template v-for="p in recentPages" :key="p">
            <button v-if="p !== '…'" :class="{ active: p === recentPage }" @click="onRecentPage(p)">{{ p }}</button>
            <span v-else class="page-dots">…</span>
          </template>
          <button :disabled="recentPage >= recentPages.length" @click="onRecentPage(recentPage + 1)">›</button>
          <span class="page-goto">
            <input type="number" v-model.number="gotoPage" min="1" :max="recentPages.length" @keyup.enter="onGotoPage" />
            <button @click="onGotoPage">跳转</button>
          </span>
        </div>
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
        :max-zoom="mapMaxZoom"
        :markers="mapStore.markers"
        :categories="mapStore.categories"
        :pick-mode="pickMode"
        :temp-marker="tempMarker"
        @marker-click="onMarkerClick"
        @marker-teleport="onMarkerTeleport"
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
      :regions="mapStore.regions"
      :region-id="currentRegionId"
      :initial-coords="pickerCoords"
      @close="closeForm"
      @submit="onFormSubmit"
    />
  </div>
</template>

<script setup>
/**
 * 主页 — 博德之门3 交互式地图核心视图
 *
 * 组装侧边面板（区域选择、地图切换、分类筛选、搜索、最新标记列表）
 * 与 Leaflet 地图容器，提供完整的交互流程：
 * - 区域/子地图切换后重新加载标记点
 * - 标记点点击显示详情弹窗
 * - 传送标记支持跳转到其他区域/地图
 * - 管理员可新增/编辑/删除标记（含坐标拾取模式）
 */
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useMapStore } from '../stores/map'
import { useAuthStore } from '../stores/auth'
import { getMaps } from '../api/maps'
import { getMarkers, getMarkerCount } from '../api/markers'
import SidePanel from '../components/SidePanel.vue'
import MapContainer from '../components/MapContainer.vue'
import MarkerPopup from '../components/MarkerPopup.vue'
import MarkerForm from '../components/MarkerForm.vue'

const mapStore = useMapStore()
const authStore = useAuthStore()
const mapRef = ref(null)                               // MapContainer 组件引用
const currentRegionId = ref(null)                       // 当前选中的区域 ID
const selectedCategoryIds = ref([])                     // 分类筛选 (多选)
const keyword = ref('')                                 // 搜索关键词
const selectedMarker = ref(null)                        // 当前选中的标记点
const loading = ref(false)
const showAddForm = ref(false)                          // 是否显示新增表单
const editingMarker = ref(null)                         // 编辑中的标记点
const selectedMapName = ref('')                        // 当前选中的子地图名
const recentMarkers = ref([])                           // "最新添加" 列表
const recentPage = ref(1)                              // 最新标记分页页码
const recentTotal = ref(0)                             // 最新标记总数
const recentPageSize = 5
const gotoPage = ref(1)                                // 跳转页输入

/** 分页器页码计算 (含省略号逻辑) */
const recentPages = computed(() => {
  const total = Math.ceil(recentTotal.value / recentPageSize)
  const cur = recentPage.value
  const pages = []
  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (cur > 3) pages.push('…')
    const start = Math.max(2, cur - 1)
    const end = Math.min(total - 1, cur + 1)
    for (let i = start; i <= end; i++) pages.push(i)
    if (cur < total - 2) pages.push('…')
    pages.push(total)
  }
  return pages
})
const pickMode = ref(false)                            // 是否处于坐标拾取模式
const showSearchResults = ref(false)                    // 是否显示搜索下拉
const searchResults = ref([])                          // 搜索结果

// 各章节 sort_order 对应的默认子地图名
const DEFAULT_MAP = {
  1: '鹦鹉螺坠毁区域',
  2: '瑰晨修道院',
  3: '幽影诅咒之地',
  4: '飞龙关',
}
const tempMarker = ref(null)                            // 拾取模式中的临时标记
const pickerCoords = ref(null)                          // 拾取的坐标

const isAdmin = computed(() => authStore.user?.is_admin)

const tileUrl = computed(() => {
  return mapStore.currentMap?.tile_url || ''
})

const mapMaxZoom = computed(() => {
  return mapStore.currentMap?.max_zoom || 6
})

const selectedCategoryName = computed(() => {
  /** 当前选中标记的分类名称 */
  if (!selectedMarker.value) return ''
  const cat = mapStore.categories.find(c => c.id === selectedMarker.value.category_id)
  return cat?.name || ''
})

const selectedCategoryColor = computed(() => {
  /** 当前选中标记的分类颜色 */
  if (!selectedMarker.value) return '#3388ff'
  const cat = mapStore.categories.find(c => c.id === selectedMarker.value.category_id)
  return cat?.color || '#3388ff'
})

async function onSearchInput() {
  /** 输入关键词时实时搜索标记 */
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
  /** 搜索框失焦时延迟关闭下拉 (给点击事件响应时间) */
  setTimeout(() => { showSearchResults.value = false }, 200)
}

async function onSearchSelect(marker) {
  /** 选中搜索结果：切换区域/地图，飞向标记位置并高亮 */
  showSearchResults.value = false
  keyword.value = marker.name
  selectedMarker.value = marker
  const region = mapStore.regions.find(r => r.id === marker.region_id)
  const needSwitch = region && (marker.region_id !== currentRegionId.value || marker.map_name !== selectedMapName.value)
  if (region && needSwitch) {
    currentRegionId.value = marker.region_id
    mapStore.setRegion(region)
    await fetchMaps()
    if (marker.map_name) {
      const mapItem = mapStore.maps.find(m => m.name === marker.map_name)
      if (mapItem) {
        selectedMapName.value = mapItem.name
        mapStore.setMap(mapItem)
      }
    }
    await loadMarkers()
  }
  await nextTick()
  mapRef.value?.flyTo(Number(marker.x_coord), Number(marker.y_coord))
  mapRef.value?.highlightMarker(Number(marker.x_coord), Number(marker.y_coord))
}

async function fetchMaps() {
  /** 根据当前区域加载子地图列表，优先选中默认地图 */
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
  /** 加载最新添加标记列表 (分页) */
  try {
    const [res, countRes] = await Promise.all([
      getMarkers({ sort_by: 'created_at', limit: recentPageSize, offset: (recentPage.value - 1) * recentPageSize }),
      getMarkerCount(),
    ])
    recentMarkers.value = res.data
    recentTotal.value = countRes.data.total
  } catch {
    console.error('加载最新标记失败')
  }
}

function onRecentClick(marker) {
  /** 点击最新标记列表项 — 等同于搜索选中 */
  keyword.value = marker.name
  onSearchSelect(marker)
}

function onRecentPage(page) {
  recentPage.value = page
  gotoPage.value = page
  fetchRecentMarkers()
}

function onGotoPage() {
  /** 分页跳转输入 */
  const max = Math.ceil(recentTotal.value / recentPageSize)
  let p = Number(gotoPage.value)
  if (isNaN(p) || p < 1) p = 1
  if (p > max) p = max
  if (p !== recentPage.value) onRecentPage(p)
}

async function loadMarkers() {
  /** 按当前区域、地图和分类筛选加载标记点 */
  loading.value = true
  try {
    const params = { region_id: currentRegionId.value, map_name: selectedMapName.value }
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

async function onRegionChange() {
  /** 切换区域下拉框 — 重置视图、加载新区域的地图和标记 */
  const region = mapStore.regions.find((r) => r.id === currentRegionId.value)
  if (region) {
    mapStore.setRegion(region)
    await fetchMaps()
    loadMarkers()
    await nextTick()
    mapRef.value?.resetView()
  }
}

function onMapChange() {
  /** 切换子地图 — 重置视图并重新加载标记 */
  const mapItem = mapStore.maps.find(m => m.name === selectedMapName.value)
  if (mapItem) {
    mapStore.setMap(mapItem)
    mapRef.value?.resetView()
    loadMarkers()
  }
}

function onMarkerClick(marker) {
  /** 点击普通标记点 — 显示详情弹窗 */
  selectedMarker.value = marker
}

async function onMarkerTeleport(marker) {
  /** 点击传送标记 — 跳转到目标区域/地图并高亮目标坐标 */
  if (!marker.target_region_id) return
  const region = mapStore.regions.find(r => r.id === marker.target_region_id)
  if (!region) return
  currentRegionId.value = marker.target_region_id
  mapStore.setRegion(region)
  await fetchMaps()
  if (marker.target_map_name) {
    const mapItem = mapStore.maps.find(m => m.name === marker.target_map_name)
    if (mapItem) {
      selectedMapName.value = mapItem.name
      mapStore.setMap(mapItem)
    }
  }
  await loadMarkers()
  await nextTick()
  mapRef.value?.flyTo(Number(marker.target_x), Number(marker.target_y))
  mapRef.value?.highlightMarker(Number(marker.target_x), Number(marker.target_y))
}

function onStartAdd() {
  /** 管理员进入坐标拾取模式，准备新增标记 */
  pickMode.value = true
  tempMarker.value = { x: 0, y: 0 }
  pickerCoords.value = null
  showAddForm.value = false
}

function onMapPick(coords) {
  /** 地图上拖拽拾取坐标 */
  tempMarker.value = coords
  pickerCoords.value = coords
}

function onConfirmPosition() {
  /** 确认拾取位置，打开新增表单 */
  if (!tempMarker.value) return
  pickerCoords.value = { ...tempMarker.value }
  showAddForm.value = true
}

function closeForm() {
  /** 关闭表单，退出拾取模式 */
  showAddForm.value = false
  editingMarker.value = null
  pickMode.value = false
  tempMarker.value = null
  pickerCoords.value = null
}

function onEditMarker(marker) {
  /** 编辑标记 — 深拷贝后打开编辑表单 */
  editingMarker.value = { ...marker }
  selectedMarker.value = null
}

async function onFormSubmit(data) {
  /** 表单提交：根据模式执行创建或更新 */
  try {
    data.map_name = selectedMapName.value
    if (editingMarker.value) {
      await mapStore.editMarker(editingMarker.value.id, data)
    } else {
      await mapStore.addMarker(data)
    }
    closeForm()
    fetchRecentMarkers()
  } catch {
    alert('操作失败，请检查权限')
  }
}

async function onDeleteMarker(id) {
  /** 删除标记点，刷新最新列表 */
  if (!confirm('确认删除该标记？')) return
  try {
    await mapStore.removeMarker(id)
    selectedMarker.value = null
    fetchRecentMarkers()
  } catch {
    alert('删除失败，请检查权限')
  }
}

onMounted(async () => {
  /** 页面挂载：加载区域和分类，默认选中第一个区域 */
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
.recent-markers li { cursor: pointer; }
.recent-markers li:hover { background: #2a2a4e; border-radius: 3px; }
.recent-name { color: #eee; }
.recent-region { color: #888; font-size: 11px; }
.pagination { display: flex; align-items: center; justify-content: center; gap: 4px; margin-top: 8px; }
.pagination button {
  background: #2a2a4e; color: #eee; border: 1px solid #444;
  min-width: 26px; height: 26px; border-radius: 3px; cursor: pointer; font-size: 13px;
}
.pagination button:disabled { opacity: 0.3; cursor: default; }
.pagination button.active { background: #ffd700; color: #1a1a2e; border-color: #ffd700; font-weight: bold; }
.page-dots { color: #888; font-size: 13px; min-width: 20px; text-align: center; }
.page-goto { display: flex; align-items: center; gap: 2px; margin-left: 6px; }
.page-goto input { width: 36px; height: 24px; padding: 0 4px; border: 1px solid #444; border-radius: 3px; background: #16213e; color: #eee; font-size: 12px; text-align: center; }
.page-goto button { min-width: 24px; height: 24px; font-size: 12px; background: #ffd700; color: #1a1a2e; border: none; border-radius: 3px; cursor: pointer; font-weight: bold; }
.empty-text { font-size: 12px; color: #555; margin-top: 4px; }

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
