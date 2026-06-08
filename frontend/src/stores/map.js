/**
 * 地图数据状态管理 (Pinia)
 *
 * 集中管理区域、分类、标记点、当前地图等核心数据，以及对应的异步加载和变更方法。
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/index'
import { getMarkers, createMarker, updateMarker, deleteMarker, userSubmitMarker, reviewMarker as apiReviewMarker } from '../api/markers'

// 章节索引到目录名的映射，按 sort_order 顺序
export const CHAPTER_KEYS = ['chapter0', 'chapter1', 'chapter2', 'chapter3', 'chapter4']

export const useMapStore = defineStore('map', () => {
  const regions = ref([])              // 区域列表
  const categories = ref([])           // 分类列表
  const markers = ref([])              // 当前显示的标记点
  const maps = ref([])                 // 当前区域下的子地图列表
  const currentRegion = ref(null)      // 当前选中区域
  const currentMap = ref(null)         // 当前选中子地图

  async function fetchRegions() {
    try {
      const res = await api.get('/regions')
      regions.value = res.data
      if (!currentRegion.value && regions.value.length > 0) {
        currentRegion.value = regions.value[0]
      }
    } catch (e) {
      console.error('获取区域列表失败:', e)
    }
  }

  async function fetchCategories() {
    try {
      const res = await api.get('/categories')
      categories.value = res.data
    } catch (e) {
      console.error('获取分类列表失败:', e)
    }
  }

  async function fetchMarkers(params = {}) {
    try {
      const res = await getMarkers(params)
      markers.value = res.data
    } catch (e) {
      console.error('获取标记列表失败:', e)
      markers.value = []
    }
  }

  async function addMarker(data) {
    try {
      const res = await createMarker(data)
      markers.value.push(res.data)
      return res.data
    } catch (e) {
      console.error('新增标记失败:', e)
      throw e
    }
  }

  async function editMarker(id, data) {
    try {
      const res = await updateMarker(id, data)
      const idx = markers.value.findIndex(m => m.id === id)
      if (idx !== -1) markers.value[idx] = res.data
      return res.data
    } catch (e) {
      console.error('编辑标记失败:', e)
      throw e
    }
  }

  async function removeMarker(id) {
    try {
      await deleteMarker(id)
      markers.value = markers.value.filter(m => m.id !== id)
    } catch (e) {
      console.error('删除标记失败:', e)
      throw e
    }
  }

  async function submitUserMarker(data) {
    try {
      const res = await userSubmitMarker(data)
      return res.data
    } catch (e) {
      console.error('提交标记失败:', e)
      throw e
    }
  }

  async function approveMarker(id) {
    try {
      const res = await apiReviewMarker(id, 'approve')
      const idx = markers.value.findIndex(m => m.id === id)
      if (idx !== -1) {
        markers.value[idx] = res.data
      } else {
        markers.value.push(res.data)
      }
      return res.data
    } catch (e) {
      console.error('审核通过失败:', e)
      throw e
    }
  }

  async function rejectMarker(id) {
    try {
      const res = await apiReviewMarker(id, 'reject')
      const idx = markers.value.findIndex(m => m.id === id)
      if (idx !== -1) markers.value[idx] = res.data
      return res.data
    } catch (e) {
      console.error('审核拒绝失败:', e)
      throw e
    }
  }

  function setRegion(region) {
    currentRegion.value = region
    currentMap.value = null
    maps.value = []
  }

  function setMap(mapItem) {
    currentMap.value = mapItem
  }

  /** 根据区域的 sort_order 获取对应的章节目录名 */
  function getChapterKey(regionSortOrder) {
    return CHAPTER_KEYS[regionSortOrder] || ''
  }

  return {
    regions, categories, markers, maps, currentRegion, currentMap,
    fetchRegions, fetchCategories, fetchMarkers, setRegion, setMap,
    addMarker, editMarker, removeMarker, getChapterKey,
    submitUserMarker, approveMarker, rejectMarker,
  }
})
