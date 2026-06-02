import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getRegions } from '../api/regions'
import { getCategories } from '../api/categories'
import { getMarkers, createMarker, updateMarker, deleteMarker } from '../api/markers'

export const useMapStore = defineStore('map', () => {
  const regions = ref([])
  const categories = ref([])
  const markers = ref([])
  const currentRegion = ref(null)
  const selectedCategory = ref(null)

  async function fetchRegions() {
    const res = await getRegions()
    regions.value = res.data
    if (!currentRegion.value && regions.value.length > 0) {
      currentRegion.value = regions.value[0]
    }
  }

  async function fetchCategories() {
    const res = await getCategories()
    categories.value = res.data
  }

  async function fetchMarkers(params = {}) {
    const res = await getMarkers(params)
    markers.value = res.data
  }

  async function addMarker(data) {
    const res = await createMarker(data)
    markers.value.push(res.data)
    return res.data
  }

  async function editMarker(id, data) {
    const res = await updateMarker(id, data)
    const idx = markers.value.findIndex(m => m.id === id)
    if (idx !== -1) markers.value[idx] = res.data
    return res.data
  }

  async function removeMarker(id) {
    await deleteMarker(id)
    markers.value = markers.value.filter(m => m.id !== id)
  }

  function setRegion(region) {
    currentRegion.value = region
  }

  function setCategory(categoryId) {
    selectedCategory.value = categoryId
  }

  return {
    regions, categories, markers, currentRegion, selectedCategory,
    fetchRegions, fetchCategories, fetchMarkers, setRegion, setCategory,
    addMarker, editMarker, removeMarker,
  }
})
