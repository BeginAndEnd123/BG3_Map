/**
 * usePickMode — 坐标拾取模式
 *
 * 从 HomeView 中抽取：管理员新增标记时的坐标选择逻辑。
 */
import { ref } from 'vue'

export function usePickMode() {
  const pickMode = ref(false)
  const tempMarker = ref(null)
  const pickerCoords = ref(null)

  function onStartAdd() {
    pickMode.value = true
    tempMarker.value = null
    pickerCoords.value = null
  }

  function onMapPick(coords) {
    tempMarker.value = coords
    pickerCoords.value = coords
  }

  function onConfirmPosition() {
    if (!tempMarker.value) return false
    pickerCoords.value = { ...tempMarker.value }
    return true
  }

  function reset() {
    pickMode.value = false
    tempMarker.value = null
    pickerCoords.value = null
  }

  return {
    pickMode, tempMarker, pickerCoords,
    onStartAdd, onMapPick, onConfirmPosition, reset,
  }
}
