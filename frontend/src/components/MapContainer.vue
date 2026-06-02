<template>
  <div id="map-container" ref="container"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import L from 'leaflet'

const props = defineProps({
  tileUrl: { type: String, default: '' },
  markers: { type: Array, default: () => [] },
  categories: { type: Array, default: () => [] },
  pickMode: { type: Boolean, default: false },
  tempMarker: { type: Object, default: null },
})

const emit = defineEmits(['marker-click', 'map-pick'])
const container = ref(null)

let map = null
let tileLayer = null
let markerLayer = null
let pickLayer = null
let pickMarker = null
let clickHandler = null

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

function initMap() {
  map = L.map(container.value, {
    center: [0, 0],
    zoom: 2,
    crs: L.CRS.Simple,
    zoomControl: true,
  })
  markerLayer = L.layerGroup().addTo(map)
  pickLayer = L.layerGroup().addTo(map)
}

function updateTileLayer(url) {
  if (tileLayer) map.removeLayer(tileLayer)
  if (!url) return
  tileLayer = L.tileLayer(url, {
    minZoom: 1, maxZoom: 6, noWrap: true,
  }).addTo(map)
}

function updateMarkers() {
  if (!markerLayer) return
  markerLayer.clearLayers()
  props.markers.forEach((m) => {
    const cat = props.categories.find((c) => c.id === m.category_id)
    const color = cat?.color || '#3388ff'
    const iconUrl = cat?.icon
    const icon = iconUrl
      ? L.icon({ iconUrl, iconSize: [24, 24], iconAnchor: [12, 12], className: '' })
      : L.divIcon({
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
    marker.on('click', () => emit('marker-click', m))
  })
}

function updatePickMode() {
  if (!map) return
  if (clickHandler) {
    map.off('click', clickHandler)
    clickHandler = null
  }
  if (props.pickMode) {
    container.value.style.cursor = 'crosshair'
    clickHandler = (e) => {
      emit('map-pick', { x: e.latlng.lat, y: e.latlng.lng })
    }
    map.on('click', clickHandler)
  } else {
    container.value.style.cursor = ''
  }
}

function updateTempMarker() {
  if (!pickLayer) return
  pickLayer.clearLayers()
  if (props.tempMarker) {
    const marker = L.marker([props.tempMarker.x, props.tempMarker.y], {
      icon: pickIcon,
      draggable: true,
    }).addTo(pickLayer)
    marker.on('dragend', () => {
      const pos = marker.getLatLng()
      emit('map-pick', { x: pos.lat, y: pos.lng })
    })
  }
}

onMounted(() => {
  initMap()
  updateTileLayer(props.tileUrl)
  updateMarkers()
  updatePickMode()
})

watch(() => props.tileUrl, (url) => updateTileLayer(url))
watch(() => props.markers, () => updateMarkers(), { deep: true })
watch(() => props.pickMode, () => updatePickMode())
watch(() => props.tempMarker, () => updateTempMarker(), { deep: true })
</script>

<style scoped>
#map-container { width: 100%; height: 100%; background: #000; }
#map-container :deep(.leaflet-container) { background: #000; }
</style>
