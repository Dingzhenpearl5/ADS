import request from './request'

/**
 * 获取公告列表
 * @param {Object} params - 查询参数
 */
export const getAnnouncements = (params = {}) => {
  return request({
    url: '/api/announcements',
    method: 'get',
    params
  })
}

/**
 * 获取单个公告
 * @param {Number} id - 公告ID
 */
export const getAnnouncement = (id) => {
  return request({
    url: `/api/announcements/${id}`,
    method: 'get'
  })
}

/**
 * 创建公告
 * @param {Object} data - 公告数据
 */
export const createAnnouncement = (data) => {
  return request({
    url: '/api/announcements',
    method: 'post',
    data
  })
}

/**
 * 更新公告
 * @param {Number} id - 公告ID
 * @param {Object} data - 公告数据
 */
export const updateAnnouncement = (id, data) => {
  return request({
    url: `/api/announcements/${id}`,
    method: 'put',
    data
  })
}

/**
 * 发布公告
 * @param {Number} id - 公告ID
 */
export const publishAnnouncement = (id) => {
  return request({
    url: `/api/announcements/${id}/publish`,
    method: 'post'
  })
}

/**
 * 下架公告
 * @param {Number} id - 公告ID
 */
export const archiveAnnouncement = (id) => {
  return request({
    url: `/api/announcements/${id}/archive`,
    method: 'post'
  })
}

/**
 * 删除公告
 * @param {Number} id - 公告ID
 */
export const deleteAnnouncement = (id) => {
  return request({
    url: `/api/announcements/${id}`,
    method: 'delete'
  })
}
