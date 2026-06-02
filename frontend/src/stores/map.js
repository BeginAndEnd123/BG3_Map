import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getRegions } from '../api/regions'
import { getCategories } from '../api/categories'
import { getMarkers } from '../api/markers'

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

  function setRegion(region) {
    currentRegion.value = region
  }

  function setCategory(categoryId) {
    selectedCategory.value = categoryId
  }

  return {
    regions, categories, markers, currentRegion, selectedCategory,
    fetchRegions, fetchCategories, fetchMarkers, setRegion, setCategory,
  }
})
