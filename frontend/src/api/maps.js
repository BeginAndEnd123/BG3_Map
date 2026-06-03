/** 地图列表 API */
import api from './index'

export const getMaps = (params) => api.get('/maps', { params })
