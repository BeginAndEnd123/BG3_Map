/**
 * useMarkerForm — 标记表单管理
 *
 * 从 HomeView 中抽取：新增/编辑表单的显示控制、提交、删除。
 */
import { ref } from 'vue'
import { useMapStore } from '../stores/map'

export function useMarkerForm() {
  const mapStore = useMapStore()
  const showAddForm = ref(false)
  const editingMarker = ref(null)
  const formSubmitting = ref(false)

  function onEditMarker(marker) {
    editingMarker.value = { ...marker }
  }

  function closeForm() {
    showAddForm.value = false
    editingMarker.value = null
    formSubmitting.value = false
  }

  async function onFormSubmit(data, selectedMapName, isAdmin = true) {
    formSubmitting.value = true
    try {
      const payload = { ...data, map_name: selectedMapName }
      if (editingMarker.value) {
        await mapStore.editMarker(editingMarker.value.id, payload)
      } else if (isAdmin) {
        await mapStore.addMarker(payload)
      } else {
        await mapStore.submitUserMarker(payload)
      }
      closeForm()
      return true
    } catch (e) {
      const msg = e.response?.data?.detail
      if (e.response?.status === 403) {
        alert('需要管理员权限')
      } else if (msg) {
        alert(msg)
      } else {
        alert('操作失败，请稍后重试')
      }
      return false
    } finally {
      formSubmitting.value = false
    }
  }

  async function onDeleteMarker(id) {
    if (!confirm('确认删除该标记？')) return false
    try {
      await mapStore.removeMarker(id)
      return true
    } catch (e) {
      const msg = e.response?.data?.detail
      if (e.response?.status === 403) {
        alert('需要管理员权限')
      } else if (msg) {
        alert(msg)
      } else {
        alert('删除失败，请稍后重试')
      }
      return false
    }
  }

  return {
    showAddForm, editingMarker, formSubmitting,
    onEditMarker, closeForm, onFormSubmit, onDeleteMarker,
  }
}
