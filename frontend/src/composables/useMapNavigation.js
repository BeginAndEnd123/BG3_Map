/**
 * useMapNavigation — 地图区域切换逻辑
 *
 * 从 HomeView 中抽取：区域/子地图的选择、地图加载、传送跳转。
 */
import { ref, nextTick } from 'vue'
import { useMapStore } from '../stores/map'
import api from '../api/index'

const DEFAULT_MAP = {
  1: '鹦鹉螺坠毁区域',
  2: '瑰晨修道院',
  3: '幽影诅咒之地',
  4: '飞龙关',
}

export function useMapNavigation() {
  const mapStore = useMapStore()
  const currentRegionId = ref(null)
  const selectedMapName = ref('')
  const loading = ref(false)
  let _requestId = 0

  async function fetchMaps() {
    const region = mapStore.currentRegion
    if (!region) return
    const chapterKey = mapStore.getChapterKey(region.sort_order)
    if (!chapterKey) return
    try {
      const res = await api.get('/maps', { params: { chapter: chapterKey } })
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

  async function loadMarkers(params = {}) {
    const reqId = ++_requestId
    loading.value = true
    try {
      await mapStore.fetchMarkers({
        region_id: currentRegionId.value,
        map_name: selectedMapName.value,
        ...params,
      })
    } catch {
      console.error('加载标记失败')
    } finally {
      if (reqId === _requestId) loading.value = false
    }
  }

  async function switchToRegion(regionId, mapName, coordX, coordY, mapRef) {
    const region = mapStore.regions.find(r => r.id === regionId)
    if (!region) return
    const needSwitch = regionId !== currentRegionId.value || mapName !== selectedMapName.value
    if (needSwitch) {
      currentRegionId.value = regionId
      mapStore.setRegion(region)
      await fetchMaps()
      if (mapName) {
        const mapItem = mapStore.maps.find(m => m.name === mapName)
        if (mapItem) {
          selectedMapName.value = mapItem.name
          mapStore.setMap(mapItem)
        }
      }
      await loadMarkers()
    }
    await nextTick()
    if (coordX != null && coordY != null && mapRef?.value) {
      mapRef.value.flyTo(Number(coordX), Number(coordY))
      mapRef.value.highlightMarker(Number(coordX), Number(coordY))
    }
  }

  async function onRegionChange(resetViewFn) {
    const region = mapStore.regions.find(r => r.id === currentRegionId.value)
    if (!region) return
    mapStore.setRegion(region)
    await fetchMaps()
    await loadMarkers()
    await nextTick()
    resetViewFn?.()
  }

  async function onMapChange() {
    const mapItem = mapStore.maps.find(m => m.name === selectedMapName.value)
    if (!mapItem) return
    mapStore.setMap(mapItem)
    await loadMarkers()
  }

  return {
    currentRegionId, selectedMapName, loading,
    fetchMaps, loadMarkers, switchToRegion,
    onRegionChange, onMapChange,
  }
}
