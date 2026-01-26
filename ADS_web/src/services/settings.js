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

// ==================== 模型管理 ====================

/**
 * 获取所有可用模型列表
 */
export const getModels = () => {
  return request({
    url: '/api/models',
    method: 'get'
  })
}

/**
 * 获取当前使用的模型信息
 */
export const getCurrentModel = () => {
  return request({
    url: '/api/models/current',
    method: 'get'
  })
}

/**
 * 切换模型
 * @param {String} modelName - 模型名称
 */
export const switchModel = (modelName) => {
  return request({
    url: '/api/models/switch',
    method: 'post',
    data: { model_name: modelName }
  })
}

/**
 * 上传新模型
 * @param {FormData} formData - 包含 file 和可选的 model_name
 */
export const uploadModel = (formData) => {
  return request({
    url: '/api/models/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 删除模型
 * @param {String} modelName - 模型名称
 */
export const deleteModel = (modelName) => {
  return request({
    url: `/api/models/${modelName}`,
    method: 'delete'
  })
}
