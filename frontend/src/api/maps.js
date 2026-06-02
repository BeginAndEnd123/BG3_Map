import api from './index'

export const getMaps = (params) => api.get('/maps', { params })
