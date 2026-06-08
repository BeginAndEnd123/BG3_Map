/**
 * useMarkerSearch — 标记搜索
 *
 * 从 HomeView 中抽取：搜索框输入、防抖、结果列表、选中跳转。
 */
import { ref } from 'vue'
import { getMarkers } from '../api/markers'

export function useMarkerSearch() {
  const keyword = ref('')
  const showSearchResults = ref(false)
  const searchResults = ref([])
  let searchDebounce = null
  let blurTimer = null

  async function onSearchInput() {
    showSearchResults.value = true
    if (!keyword.value) {
      searchResults.value = []
      return
    }
    if (searchDebounce) clearTimeout(searchDebounce)
    searchDebounce = setTimeout(async () => {
      try {
        const res = await getMarkers({ keyword: keyword.value })
        searchResults.value = res.data
      } catch (err) {
        console.warn('搜索请求失败:', err)
        searchResults.value = []
      }
    }, 300)
  }

  function onSearchBlur() {
    if (blurTimer) clearTimeout(blurTimer)
    blurTimer = setTimeout(() => { showSearchResults.value = false }, 200)
  }

  function onSearchSelect(marker, switchToRegionFn) {
    showSearchResults.value = false
    if (marker.region_id && switchToRegionFn) {
      switchToRegionFn(marker.region_id, marker.map_name, marker.x_coord, marker.y_coord)
    }
    return marker
  }

  function cleanup() {
    if (searchDebounce) clearTimeout(searchDebounce)
    if (blurTimer) clearTimeout(blurTimer)
  }

  return {
    keyword, showSearchResults, searchResults,
    onSearchInput, onSearchBlur, onSearchSelect, cleanup,
  }
}
