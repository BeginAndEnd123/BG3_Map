<template>
  <div class="map-page">
    <div class="sidebar">
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
            @change="onFilterChange"
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
          @input="onSearch"
        />
      </div>

      <div class="stats">
        <h3>统计</h3>
        <p>标记总数：{{ mapStore.markers.length }}</p>
      </div>
    </div>

    <div class="map-container" ref="mapRef"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useMapStore } from '../stores/map'
import L from 'leaflet'

const mapStore = useMapStore()
const mapRef = ref(null)
const currentRegionId = ref(null)
const selectedCategoryIds = ref([])
const keyword = ref('')

let map = null
let markerLayer = null

function initMap() {
  map = L.map(mapRef.value, {
    center: [0, 0],
    zoom: 2,
    crs: L.CRS.Simple,
    zoomControl: true,
  })
  markerLayer = L.layerGroup().addTo(map)
}

function loadTileLayer(region) {
  if (!map || !region) return
  map.eachLayer((layer) => {
    if (layer instanceof L.TileLayer) {
      map.removeLayer(layer)
    }
  })
  const url = region.tile_url || '/TileMap/chapter1/{z}/{x}/{y}.png'
  L.tileLayer(url, {
    minZoom: 1,
    maxZoom: 6,
    noWrap: true,
    attribution: 'BG3 Map',
  }).addTo(map)
}

function loadMarkers() {
  if (!markerLayer) return
  markerLayer.clearLayers()
  const params = { region_id: currentRegionId.value }
  if (selectedCategoryIds.value.length > 0) {
    params.category_id = selectedCategoryIds.value.join(',')
  }
  if (keyword.value) {
    params.keyword = keyword.value
  }

  mapStore.fetchMarkers(params).then(() => {
    mapStore.markers.forEach((m) => {
      const cat = mapStore.categories.find((c) => c.id === m.category_id)
      const color = cat?.color || '#3388ff'
      const icon = L.divIcon({
        html: `<div style="
          width: 12px; height: 12px; border-radius: 50%;
          background: ${color}; border: 2px solid #fff;
          box-shadow: 0 1px 3px rgba(0,0,0,0.3);
        "></div>`,
        iconSize: [12, 12],
        iconAnchor: [6, 6],
        className: '',
      })
      const marker = L.marker([m.x_coord, m.y_coord], { icon }).addTo(markerLayer)
      marker.bindPopup(`<b>${m.name}</b><br>${m.description || ''}`)
    })
  })
}

function onRegionChange() {
  const region = mapStore.regions.find((r) => r.id === currentRegionId.value)
  if (region) {
    mapStore.setRegion(region)
    loadTileLayer(region)
    loadMarkers()
  }
}

function onFilterChange() {
  loadMarkers()
}

function onSearch() {
  loadMarkers()
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
  initMap()
  loadTileLayer(mapStore.currentRegion)
  loadMarkers()
})
</script>

<style scoped>
.map-page {
  display: flex;
  width: 100%;
  height: 100vh;
}

.sidebar {
  width: 280px;
  min-width: 280px;
  background: #1a1a2e;
  color: #eee;
  padding: 20px;
  overflow-y: auto;
}

.sidebar h2 {
  font-size: 20px;
  margin-bottom: 20px;
  color: #ffd700;
}

.sidebar h3 {
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

.map-container {
  flex: 1;
  height: 100vh;
}
</style>
