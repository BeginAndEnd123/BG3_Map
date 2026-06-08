<template>
  <div class="map-page">
    <SidePanel>
      <h2>博德之门3 地图</h2>

      <div class="region-select">
        <h3>选择区域</h3>
        <select v-model="nav.currentRegionId.value" @change="onRegionChange">
          <option v-for="r in mapStore.regions" :key="r.id" :value="r.id">{{ r.name }}</option>
        </select>
      </div>

      <div class="map-select" v-if="mapStore.maps.length > 0">
        <h3>选择地图</h3>
        <select v-model="nav.selectedMapName.value" @change="onMapChange">
          <option v-for="m in mapStore.maps" :key="m.name" :value="m.name">{{ m.name }}</option>
        </select>
      </div>

      <div class="category-filter">
        <h3>分类筛选</h3>
        <label v-for="c in mapStore.categories" :key="c.id" class="category-item">
          <input type="checkbox" :value="c.id" v-model="selectedCategoryIds" @change="reloadMarkers" />
          <span :style="{ color: c.color }">{{ c.name }}</span>
        </label>
      </div>

      <div class="search-box">
        <h3>搜索标记</h3>
        <input type="text" v-model="search.keyword.value" placeholder="输入标记名称..."
          aria-label="搜索标记" @input="search.onSearchInput()"
          @focus="search.showSearchResults.value = true" @blur="search.onSearchBlur()" />
        <ul v-if="search.showSearchResults.value && search.searchResults.value.length" class="search-list" role="listbox">
          <li v-for="m in search.searchResults.value" :key="m.id" role="option" tabindex="0"
            @mousedown.prevent="onSearchClick(m)" @keydown.enter.prevent="onSearchClick(m)" @keydown.space.prevent="onSearchClick(m)">
            <span class="sr-name">{{ m.name }}</span>
            <span class="sr-region">{{ m.region?.name || '' }}</span>
          </li>
        </ul>
      </div>

      <div class="stats">
        <h3>统计</h3>
        <p>标记总数：{{ recent.recentTotal.value }}</p>
      </div>

      <div class="recent-markers">
        <h3>最新添加</h3>
        <ul v-if="recent.recentMarkers.value.length > 0">
          <li v-for="m in recent.recentMarkers.value" :key="m.id" role="button" tabindex="0"
            @click="onRecentClick(m)" @keydown.enter.prevent="onRecentClick(m)" @keydown.space.prevent="onRecentClick(m)">
            <span class="recent-name">{{ m.name }}</span>
            <span class="recent-region">{{ m.region?.name || '' }}</span>
          </li>
        </ul>
        <p v-else class="empty-text">暂无标记</p>
        <div v-if="recent.recentTotal.value > 0" class="pagination">
          <div class="page-row">
            <button :disabled="recent.recentPage.value <= 1" @click="recent.onRecentPage(recent.recentPage.value - 1)">‹</button>
            <template v-for="p in recent.recentPages.value" :key="p">
              <button v-if="p !== '…'" :class="{ active: p === recent.recentPage.value }" @click="recent.onRecentPage(p)">{{ p }}</button>
              <span v-else class="page-dots">…</span>
            </template>
            <button :disabled="recent.recentPage.value >= recent.recentTotalPages.value" @click="recent.onRecentPage(recent.recentPage.value + 1)">›</button>
          </div>
          <div class="page-goto">
            <input type="number" v-model.number="recent.gotoPage.value" min="1" :max="recent.recentTotalPages.value" aria-label="跳转到指定页码" @keyup.enter="recent.onGotoPage()" />
            <button @click="recent.onGotoPage()">跳转</button>
          </div>
        </div>
      </div>

      <button v-if="authStore.user" class="add-btn" @click="onStartAdd">
        + {{ isAdmin ? '新增标记' : '提交标记' }}
      </button>

      <div v-if="isAdmin" class="review-section">
        <h3>审核管理</h3>
        <p class="review-count">待审核：{{ pendingCount }} 个</p>
        <button class="review-toggle-btn" @click="openReviewModal">
          打开审核面板
        </button>
      </div>
    </SidePanel>

    <ReviewModal
      :visible="showReviewModal"
      :pending-markers="pendingMarkers"
      :pending-count="pendingCount"
      :loading="reviewLoading"
      @close="closeReviewModal"
      @approve="onApprove"
      @reject="onReject"
      @locate="onLocatePending"
    />

    <div class="map-wrapper">
      <MapContainer ref="mapRef" :tile-url="tileUrl" :max-zoom="mapMaxZoom"
        :markers="mapStore.markers" :categories="mapStore.categories"
        :pick-mode="pick.pickMode.value" :temp-marker="pick.tempMarker.value"
        @marker-click="selectedMarker = $event"
        @marker-teleport="onMarkerTeleport"
        @map-pick="pick.onMapPick($event)" />

      <div class="loading-mask" v-if="nav.loading.value">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div class="pick-overlay" v-if="pick.pickMode.value">
        <div class="pick-hint">点击地图放置标记，拖动微调位置</div>
        <button class="confirm-btn" @click="onConfirmPick">确认位置</button>
      </div>
    </div>

    <MarkerPopup v-if="selectedMarker" :marker="selectedMarker"
      :category-name="selectedCategoryName" :category-color="selectedCategoryColor"
      @close="selectedMarker = null">
      <template #actions v-if="isAdmin">
        <button class="action-btn edit" @click="onEdit(selectedMarker)">编辑</button>
        <button class="action-btn delete" @click="onDelete(selectedMarker.id)">删除</button>
      </template>
    </MarkerPopup>

    <MarkerForm v-if="form.showAddForm.value || form.editingMarker.value"
      :marker="form.editingMarker.value" :categories="mapStore.categories"
      :regions="mapStore.regions" :region-id="nav.currentRegionId.value"
      :initial-coords="pick.pickerCoords.value" :submitting="form.formSubmitting.value"
      @close="onFormClose" @submit="onFormSubmit" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useMapStore } from '../stores/map'
import { useAuthStore } from '../stores/auth'
import SidePanel from '../components/SidePanel.vue'
import MapContainer from '../components/MapContainer.vue'
import MarkerPopup from '../components/MarkerPopup.vue'
import MarkerForm from '../components/MarkerForm.vue'
import ReviewModal from '../components/ReviewModal.vue'
import { useMapNavigation } from '../composables/useMapNavigation'
import { useMarkerSearch } from '../composables/useMarkerSearch'
import { useRecentMarkers } from '../composables/useRecentMarkers'
import { usePickMode } from '../composables/usePickMode'
import { useMarkerForm } from '../composables/useMarkerForm'
import { getMarkers, getPendingCount } from '../api/markers'

const mapStore = useMapStore()
const authStore = useAuthStore()
const mapRef = ref(null)
const selectedMarker = ref(null)
const selectedCategoryIds = ref([])

const nav = useMapNavigation()
const search = useMarkerSearch()
const recent = useRecentMarkers(5)
const pick = usePickMode()
const form = useMarkerForm()

const isAdmin = computed(() => authStore.user?.is_admin)
const tileUrl = computed(() => mapStore.currentMap?.tile_url || '')
const mapMaxZoom = computed(() => mapStore.currentMap?.max_zoom || 6)
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

const pendingMarkers = ref([])
const pendingCount = ref(0)
const showReviewModal = ref(false)
const reviewLoading = ref(false)

async function fetchPendingMarkers() {
  reviewLoading.value = true
  try {
    const [listRes, countRes] = await Promise.all([
      getMarkers({ status: 'pending', limit: 100 }),
      getPendingCount(),
    ])
    pendingMarkers.value = listRes.data
    pendingCount.value = countRes.data.total
  } catch {
    pendingMarkers.value = []
    pendingCount.value = 0
  } finally {
    reviewLoading.value = false
  }
}

async function onApprove(id) {
  try {
    await mapStore.approveMarker(id)
    pendingMarkers.value = pendingMarkers.value.filter(m => m.id !== id)
    pendingCount.value = Math.max(0, pendingCount.value - 1)
    await recent.fetchRecentMarkers()
  } catch (e) {
    alert(e.response?.data?.detail || '审核失败')
  }
}

async function onReject(id) {
  if (!confirm('确认拒绝该标记？')) return
  try {
    await mapStore.rejectMarker(id)
    mapStore.markers = mapStore.markers.filter(m => m.id !== id)
    pendingMarkers.value = pendingMarkers.value.filter(m => m.id !== id)
    pendingCount.value = Math.max(0, pendingCount.value - 1)
  } catch (e) {
    alert(e.response?.data?.detail || '审核失败')
  }
}

async function onLocatePending(marker) {
  selectedMarker.value = marker
  await nav.switchToRegion(
    marker.region_id, marker.map_name,
    marker.x_coord, marker.y_coord, mapRef,
  )
  closeReviewModal()
}

// ── 分类筛选 ──
function reloadMarkers() {
  nav.loadMarkers({ category_id: selectedCategoryIds.value.join(',') })
}

// ── 搜索选中 ──
function onSearchClick(marker) {
  selectedMarker.value = search.onSearchSelect(marker,
    (rid, mn, x, y) => nav.switchToRegion(rid, mn, x, y, mapRef)
  )
}

// ── 最新标记点击 ──
function onRecentClick(marker) { onSearchClick(marker) }

// ── 传送 ──
async function onMarkerTeleport(marker) {
  if (!marker.target_region_id) return
  await nav.switchToRegion(marker.target_region_id, marker.target_map_name,
    marker.target_x, marker.target_y, mapRef)
}

// ── 拾取模式 ──
function onStartAdd() {
  pick.onStartAdd()
  form.showAddForm.value = false
}
function onConfirmPick() {
  if (pick.onConfirmPosition()) form.showAddForm.value = true
}

// ── 表单 ──
async function onFormSubmit(data) {
  const ok = await form.onFormSubmit(data, nav.selectedMapName.value, isAdmin.value)
  if (ok) {
    pick.reset()
    await recent.fetchRecentMarkers()
    if (!isAdmin.value) {
      alert('标记已提交，等待管理员审核')
    }
  }
}
function onFormClose() {
  form.closeForm()
  pick.reset()
}
function onEdit(marker) {
  form.onEditMarker(marker)
  selectedMarker.value = null
}
async function onDelete(id) {
  const ok = await form.onDeleteMarker(id)
  if (ok) {
    selectedMarker.value = null
    await recent.fetchRecentMarkers()
  }
}

// ── 区域/地图切换 ──
async function onRegionChange() {
  selectedCategoryIds.value = []
  search.keyword.value = ''
  await nav.onRegionChange(() => mapRef.value?.resetView())
}
async function onMapChange() {
  selectedCategoryIds.value = []
  search.keyword.value = ''
  mapRef.value?.resetView()
  await nav.onMapChange()
}

// ── 初始化 ──
onMounted(async () => {
  try {
    await Promise.all([mapStore.fetchRegions(), mapStore.fetchCategories()])
  } catch {
    console.error('初始化加载失败')
  }
  if (mapStore.regions.length > 0) {
    nav.currentRegionId.value = mapStore.regions[0].id
    mapStore.setRegion(mapStore.regions[0])
    await nav.fetchMaps()
  }
  await nav.loadMarkers()
  recent.fetchRecentMarkers()
  if (isAdmin.value) {
    fetchPendingMarkers()
  }
})

onBeforeUnmount(() => {
  search.cleanup()
})

function mergePendingToMap() {
  const existingIds = new Set(mapStore.markers.map(m => m.id))
  pendingMarkers.value.forEach(m => {
    if (!existingIds.has(m.id)) mapStore.markers.push(m)
  })
}

function removePendingFromMap() {
  const pendingIds = new Set(pendingMarkers.value.map(m => m.id))
  mapStore.markers = mapStore.markers.filter(m => !pendingIds.has(m.id))
}

async function openReviewModal() {
  showReviewModal.value = true
  await fetchPendingMarkers()
  mergePendingToMap()
}

function closeReviewModal() {
  showReviewModal.value = false
  removePendingFromMap()
}
</script>

<style scoped>
.map-page { display: flex; flex: 1; overflow: hidden; }

:deep(h2) {
  font-size: 17px; margin-bottom: 14px; color: var(--gold);
  text-align: center; letter-spacing: 0.08em;
  padding-bottom: 10px; border-bottom: 1px solid var(--border-gold);
}
:deep(h3) {
  font-size: 11px; margin: 10px 0 4px; color: var(--text-secondary);
  font-family: var(--font-display); font-weight: 600; letter-spacing: 0.08em;
  text-transform: uppercase;
}

.region-select select, .map-select select {
  width: 100%; padding: 5px 10px;
  border: 1px solid var(--border); border-radius: var(--radius-sm);
  background: var(--bg-input); color: var(--text-primary);
  font-size: 13px; font-family: var(--font-body);
  cursor: pointer; outline: none; transition: border var(--transition);
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%238a8578'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 10px center;
}
.region-select select:focus, .map-select select:focus { border-color: var(--gold-dim); }

.category-item {
  display: flex; align-items: center; gap: 5px;
  margin: 2px 0; cursor: pointer; font-size: 13px;
  padding: 1px 4px; border-radius: var(--radius-sm);
  transition: background var(--transition);
}
.category-item:hover { background: rgba(200,164,78,0.06); }
.category-item input[type="checkbox"] { accent-color: var(--gold); }

.search-box { position: relative; }
.search-box input {
  width: 100%; padding: 5px 10px;
  border: 1px solid var(--border); border-radius: var(--radius-sm);
  background: var(--bg-input); color: var(--text-primary);
  font-size: 13px; font-family: var(--font-body);
  outline: none; transition: border var(--transition);
}
.search-box input:focus { border-color: var(--gold-dim); }
.search-box input::placeholder { color: var(--text-muted); }
.search-list {
  position: absolute; top: 100%; left: 0; right: 0;
  background: var(--bg-card); border: 1px solid var(--border-gold);
  border-top: none; border-radius: 0 0 var(--radius-md) var(--radius-md);
  list-style: none; max-height: 160px; overflow-y: auto; z-index: 100;
}
.search-list li {
  padding: 6px 10px; cursor: pointer; font-size: 13px;
  display: flex; justify-content: space-between; align-items: center;
  transition: background var(--transition);
}
.search-list li:hover { background: rgba(200,164,78,0.08); }
.sr-name { color: var(--text-primary); }
.sr-region { color: var(--text-muted); font-size: 11px; }

.stats {
  margin-top: 12px; padding-top: 10px;
  border-top: 1px solid var(--border);
  font-size: 13px; color: var(--text-secondary);
}

.recent-markers { margin-top: 10px; padding-top: 8px; border-top: 1px solid var(--border); }
.recent-markers ul { list-style: none; margin-top: 2px; height: 110px; }
.recent-markers li {
  display: flex; justify-content: space-between; align-items: center;
  padding: 2px 4px; font-size: 12px;
  border-radius: var(--radius-sm); cursor: pointer;
  transition: background var(--transition);
}
.recent-markers li:hover { background: rgba(200,164,78,0.06); }
.recent-markers li + li { border-top: 1px solid rgba(42,40,64,0.5); }
.recent-name { color: var(--text-primary); }
.recent-region { color: var(--text-muted); font-size: 11px; }
.empty-text { font-size: 13px; color: var(--text-muted); margin-top: 2px; height: 110px; }

.pagination { margin-top: 4px; }
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
  width: 34px; height: 22px; padding: 0 3px;
  border: 1px solid var(--border); border-radius: var(--radius-sm);
  background: var(--bg-input); color: var(--text-primary);
  font-size: 11px; font-family: var(--font-body); text-align: center; outline: none;
}
.page-goto input:focus { border-color: var(--gold-dim); }
.page-goto button {
  min-width: 28px; height: 22px; font-size: 11px;
  background: var(--gold); color: var(--bg-deep);
  border: none; border-radius: var(--radius-sm); cursor: pointer;
  font-weight: 600; font-family: var(--font-body);
  transition: background var(--transition);
}
.page-goto button:hover { background: var(--gold-light); }

.add-btn {
  width: 100%; margin-top: 12px; padding: 8px;
  border: 1px solid var(--gold); border-radius: var(--radius-sm);
  background: transparent; color: var(--gold);
  font-family: var(--font-display); font-size: 12px;
  font-weight: 600; letter-spacing: 0.06em;
  cursor: pointer; transition: all var(--transition);
}
.add-btn:hover { background: var(--gold); color: var(--bg-deep); }

.map-wrapper { flex: 1; position: relative; background: #000; }

.loading-mask {
  position: absolute; inset: 0;
  background: rgba(8,8,18,0.5); display: flex;
  flex-direction: column; align-items: center; justify-content: center;
  z-index: 999; color: var(--text-secondary); font-size: 14px; gap: 12px;
}
.spinner {
  width: 28px; height: 28px;
  border: 2px solid rgba(200,164,78,0.2);
  border-top-color: var(--gold); border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.pick-overlay {
  position: absolute; top: 16px; left: 50%; transform: translateX(-50%);
  display: flex; flex-direction: column; align-items: center; gap: 8px; z-index: 1000;
}
.pick-hint {
  background: rgba(8,8,18,0.85); color: var(--gold);
  padding: 8px 24px; border-radius: var(--radius-sm); font-size: 13px;
  border: 1px solid var(--border-gold); white-space: nowrap;
}
.confirm-btn {
  padding: 10px 32px; border: none; border-radius: var(--radius-sm);
  background: var(--gold); color: var(--bg-deep);
  font-family: var(--font-display); font-size: 14px;
  font-weight: 600; letter-spacing: 0.06em;
  cursor: pointer; box-shadow: var(--shadow-gold);
  transition: background var(--transition);
}
.confirm-btn:hover { background: var(--gold-light); }

.review-section {
  margin-top: 8px; padding-top: 6px;
  border-top: 1px solid var(--border);
}
.review-count {
  font-size: 12px; color: var(--warning, #e8a838); margin: 3px 0;
}
.review-toggle-btn {
  width: 100%; padding: 4px;
  border: 1px solid var(--gold-dim); border-radius: var(--radius-sm);
  background: transparent; color: var(--gold);
  font-family: var(--font-body); font-size: 11px;
  cursor: pointer; transition: all var(--transition);
}
.review-toggle-btn:hover { background: var(--gold); color: var(--bg-deep); }
</style>
