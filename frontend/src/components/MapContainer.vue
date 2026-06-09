<template>
  <div id="map-container" ref="container" role="application" aria-label="交互式地图" tabindex="0"></div>
</template>

<script setup>
/**
 * Leaflet 地图容器组件
 *
 * 使用 CRS.Simple 坐标系渲染瓦片地图，支持：
 * - 标记点渲染（含自定义图标和分类颜色）
 * - 坐标拾取模式（管理员新增标记时拖拽定位）
 * - 传送标记点高亮动画
 * - 通过 defineExpose 暴露 flyTo/highlightMarker/resetView 方法
 */
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import L from 'leaflet'

const props = defineProps({
  tileUrl: { type: String, default: '' },
  maxZoom: { type: Number, default: 6 },
  markers: { type: Array, default: () => [] },
  categories: { type: Array, default: () => [] },
  pickMode: { type: Boolean, default: false },
  tempMarker: { type: Object, default: null },
  isAdmin: { type: Boolean, default: false },
})

const emit = defineEmits(['marker-click', 'marker-teleport', 'map-pick'])
const container = ref(null)

// Leaflet 实例引用
let map = null
let tileLayer = null              // 瓦片图层
let markerLayer = null            // 标记点图层组
let pickLayer = null              // 拾取模式图层组
let highlightLayer = null         // 高亮动画图层组
let pickMarker = null
let highlightTimer = null

// 拾取模式下的标记图标
const pickIcon = L.divIcon({
  html: `<div style="
    width: 20px; height: 20px; border-radius: 50%;
    background: #ff4444; border: 3px solid #fff;
    box-shadow: 0 2px 8px rgba(0,0,0,0.5);
    cursor: grab;
  "></div>`,
  iconSize: [20, 20],
  iconAnchor: [10, 10],
  className: '',
})

function _onMapClick(e) {
  if (!props.pickMode) return
  if (pickMarker) return
  const pos = e.latlng
  pickMarker = L.marker([pos.lat, pos.lng], {
    icon: pickIcon,
    draggable: true,
  }).addTo(pickLayer)
  pickMarker.on('dragend', () => {
    const p = pickMarker.getLatLng()
    emit('map-pick', { x: p.lat, y: p.lng })
  })
  emit('map-pick', { x: pos.lat, y: pos.lng })
}

function initMap() {
  /** 初始化 Leaflet 地图实例，使用 CRS.Simple 坐标系 */
  map = L.map(container.value, {
    center: [0, 0],
    zoom: 2,
    crs: L.CRS.Simple,
    zoomControl: true,
  })
  markerLayer = L.layerGroup().addTo(map)
  highlightLayer = L.layerGroup().addTo(map)
  pickLayer = L.layerGroup().addTo(map)
}

function updateTileLayer(url) {
  /** 切换瓦片图层 */
  if (tileLayer) map.removeLayer(tileLayer)
  if (!url) return
  tileLayer = L.tileLayer(url, {
    minZoom: 1, maxZoom: props.maxZoom, noWrap: true,
  }).addTo(map)
}

/** 重置地图视图到原点 */
function resetView() {
  if (map) map.setView([0, 0], 2, { animate: false })
}

function updateMarkers() {
  /** 根据 props.markers 重新渲染所有标记点 */
  if (!markerLayer) return
  markerLayer.clearLayers()
  props.markers.forEach((m) => {
    const cat = props.categories.find((c) => c.id === m.category_id)
    const iconUrl = cat?.icon || m.category?.icon
    const isPending = m.status === 'pending'
    const fallbackColors = ['#3388ff', '#e06060', '#60c060', '#e8a838', '#c060e0', '#60c0c0']
    const fallbackColor = fallbackColors[m.id % fallbackColors.length]
    const icon = iconUrl
      ? L.icon({ iconUrl, iconSize: [24, 24], iconAnchor: [12, 12], className: isPending ? 'marker-pending' : '' })
      : L.divIcon({
          html: `<div style="
            width: 12px; height: 12px; border-radius: 50%;
            background: ${fallbackColor}; border: 2px solid ${isPending ? '#e8a838' : '#fff'};
            box-shadow: 0 1px 3px rgba(0,0,0,0.3);
          "></div>`,
          iconSize: [12, 12],
          iconAnchor: [6, 6],
          className: '',
        })
    const marker = L.marker([m.x_coord, m.y_coord], { icon }).addTo(markerLayer)

    marker.bindTooltip(m.name, {
      direction: 'top',
      offset: [0, -16],
      opacity: 0.9,
      className: 'marker-tooltip',
    })

    // 管理员点击有传送目标的标记 → 弹出详情（可选传送或编辑）
    // 非管理员点击有传送目标的标记 → 直接传送
    marker.on('click', () => {
      if (m.target_region_id && !props.isAdmin) {
        emit('marker-teleport', m)
      } else {
        emit('marker-click', m)
      }
    })
  })
}

function updatePickMode() {
  /** 切换拾取模式：绑定/解绑地图点击事件，切换光标样式 */
  if (!map) return
  if (props.pickMode) {
    map.on('click', _onMapClick)
    container.value.style.cursor = 'crosshair'
  } else {
    map.off('click', _onMapClick)
    container.value.style.cursor = ''
    if (pickMarker) {
      pickLayer.clearLayers()
      pickMarker = null
    }
  }
}

function updateTempMarker() {
  /** 拾取模式：由地图点击事件管理标记创建和拖拽，此处仅处理清理 */
  if (!pickLayer) return
  if (!props.tempMarker && pickMarker) {
    pickLayer.clearLayers()
    pickMarker = null
  }
}

onMounted(() => {
  initMap()
  updateTileLayer(props.tileUrl)
  updateMarkers()
  updatePickMode()
})

onBeforeUnmount(() => {
  if (highlightTimer) clearTimeout(highlightTimer)
  if (map) {
    map.off('click', _onMapClick)
    if (pickMarker) {
      pickMarker.off('dragend')
      pickMarker = null
    }
    map.remove()
    map = null
  }
})

/** 平滑飞行到指定坐标 (使用 props.maxZoom 而非 map.getMaxZoom) */
function flyTo(lat, lng, zoom) {
  if (!map) return
  const targetZoom = zoom != null ? zoom : Math.max(1, props.maxZoom - 1)
  map.flyTo([lat, lng], targetZoom, { duration: 0.5 })
}

/** 在指定坐标显示脉冲高亮动画（3 秒后自动消失） */
function highlightMarker(lat, lng) {
  if (!highlightLayer) return
  highlightLayer.clearLayers()
  const pulseIcon = L.divIcon({
    html: '<div class="pulse-marker"></div>',
    iconSize: [40, 40],
    iconAnchor: [20, 20],
    className: '',
  })
  L.marker([lat, lng], { icon: pulseIcon, interactive: false }).addTo(highlightLayer)
  if (highlightTimer) clearTimeout(highlightTimer)
  highlightTimer = setTimeout(() => highlightLayer.clearLayers(), 3000)
}

function clearHighlight() {
  if (highlightTimer) clearTimeout(highlightTimer)
  if (highlightLayer) highlightLayer.clearLayers()
}

// 暴露给父组件调用的方法
defineExpose({ flyTo, highlightMarker, clearHighlight, resetView })

// 监听 props 变化，自动更新地图
watch(() => props.tileUrl, (url) => updateTileLayer(url))
watch(() => props.markers, () => updateMarkers())
watch(() => props.pickMode, () => updatePickMode())
watch(() => props.tempMarker, () => updateTempMarker(), { deep: true })
</script>

<style scoped>
#map-container { width: 100%; height: 100%; background: #000; }
#map-container :deep(.leaflet-container) { background: #000; }
</style>

<style>
.pulse-marker {
  width: 40px; height: 40px; border-radius: 50%;
  background: rgba(200, 164, 78, 0.25);
  border: 3px solid #c8a44e;
  animation: pulse-ring 1.5s ease-out infinite;
}
@keyframes pulse-ring {
  0% { transform: scale(0.5); opacity: 1; }
  100% { transform: scale(1.5); opacity: 0; }
}

.marker-tooltip {
  background: var(--bg-surface, #12121f);
  border: 1px solid var(--border-gold, rgba(200,164,78,0.25));
  border-radius: 2px;
  color: var(--gold, #c8a44e);
  font-family: 'Crimson Text', serif;
  font-size: 13px;
  padding: 4px 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.5);
}
.marker-tooltip::before {
  border-top-color: var(--border-gold, rgba(200,164,78,0.25));
}

.leaflet-control-zoom a {
  background: var(--bg-surface, #12121f) !important;
  border: 1px solid var(--border, #2a2840) !important;
  color: var(--text-secondary, #8a8578) !important;
  width: 30px !important; height: 30px !important;
  line-height: 28px !important; font-size: 16px !important;
  border-radius: 2px !important;
}
.leaflet-control-zoom a:hover {
  background: var(--bg-card, #1a1a2c) !important;
  color: var(--gold, #c8a44e) !important;
  border-color: var(--gold-dim, #8a6d30) !important;
}
</style>
