/**
 * useRecentMarkers — 最新标记列表 + 分页
 *
 * 从 HomeView 中抽取：最新标记加载、分页控制器。
 */
import { ref, computed } from 'vue'
import { getMarkers, getMarkerCount } from '../api/markers'

export function useRecentMarkers(pageSize = 5) {
  const recentMarkers = ref([])
  const recentPage = ref(1)
  const recentTotal = ref(0)
  const gotoPage = ref(1)

  const recentTotalPages = computed(() => Math.ceil(recentTotal.value / pageSize))

  const recentPages = computed(() => {
    const total = recentTotalPages.value
    const cur = recentPage.value
    const pages = []
    if (total <= 7) {
      for (let i = 1; i <= total; i++) pages.push(i)
    } else {
      pages.push(1)
      if (cur > 3) pages.push('…')
      for (let i = Math.max(2, cur - 1); i <= Math.min(total - 1, cur + 1); i++) pages.push(i)
      if (cur < total - 2) pages.push('…')
      pages.push(total)
    }
    return pages
  })

  async function fetchRecentMarkers() {
    try {
      const [res, countRes] = await Promise.all([
        getMarkers({ sort_by: 'created_at', limit: pageSize, offset: (recentPage.value - 1) * pageSize }),
        getMarkerCount(),
      ])
      recentMarkers.value = res.data
      recentTotal.value = countRes.data.total
    } catch {
      console.error('加载最新标记失败')
    }
  }

  function onRecentPage(page) {
    recentPage.value = page
    gotoPage.value = page
    fetchRecentMarkers()
  }

  function onGotoPage() {
    const max = recentTotalPages.value
    let p = Number(gotoPage.value)
    if (isNaN(p) || p < 1) p = 1
    if (p > max) p = max
    if (p !== recentPage.value) onRecentPage(p)
  }

  return {
    recentMarkers, recentPage, recentTotal, recentTotalPages,
    recentPages, gotoPage,
    fetchRecentMarkers, onRecentPage, onGotoPage,
  }
}
