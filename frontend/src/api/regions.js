import api from './index'

export const getRegions = () => api.get('/regions')
export const getRegion = (id) => api.get(`/regions/${id}`)
