import request from './request'

/**
 * 获取所有系统设置
 */
export const getSettings = () => {
  return request({
    url: '/api/settings',
    method: 'get'
  })
}

/**
 * 更新系统设置
 * @param {Object} settings - 设置键值对
 * @param {String} category - 分类（可选）
 */
export const updateSettings = (settings, category = null) => {
  return request({
    url: '/api/settings',
    method: 'post',
    data: {
      settings,
      category
    }
  })
}

/**
 * 获取单个设置项
 * @param {String} key - 设置项的键
 */
export const getSetting = (key) => {
  return request({
    url: `/api/settings/${key}`,
    method: 'get'
  })
}

/**
 * 重置设置为默认值
 * @param {String} category - 分类（可选，不传则重置所有）
 */
export const resetSettings = (category = null) => {
  return request({
    url: '/api/settings/reset',
    method: 'post',
    data: { category }
  })
}
