import request from './request'

/**
 * 获取诊断历史列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.per_page - 每页数量
 * @param {string} params.patient_id - 患者ID（可选）
 */
export function getDiagnosisHistory(params = {}) {
    return request({
        url: '/api/diagnosis/history',
        method: 'get',
        params: {
            page: params.page || 1,
            per_page: params.per_page || 10,
            patient_id: params.patient_id || undefined
        }
    })
}

/**
 * 获取诊断详情
 * @param {number} id - 诊断记录ID
 */
export function getDiagnosisDetail(id) {
    return request({
        url: `/api/diagnosis/${id}`,
        method: 'get'
    })
}

/**
 * 获取统计数据
 */
export function getStatistics() {
    return request({
        url: '/api/statistics',
        method: 'get'
    })
}

/**
 * 健康检查
 */
export function healthCheck() {
    return request({
        url: '/api/health',
        method: 'get'
    })
}
