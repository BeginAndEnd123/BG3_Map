/** 标记点 CRUD API */
import api from './index'

export const getMarkers = (params) => api.get('/markers', { params })
export const getMarkerCount = (params) => api.get('/markers/count', { params })
export const getMarker = (id) => api.get(`/markers/${id}`)
export const createMarker = (data) => api.post('/markers', data)
export const updateMarker = (id, data) => api.put(`/markers/${id}`, data)
export const deleteMarker = (id) => api.delete(`/markers/${id}`)
