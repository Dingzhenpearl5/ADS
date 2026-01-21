import request from './request'

/**
 * 获取首页统计数据
 * 包含诊断总数、今日诊断、准确率、平均用时、最近诊断记录等
 */
export function getStatistics() {
    return request({
        url: '/api/statistics',
        method: 'get'
    })
}

/**
 * 获取诊断历史记录
 * @param {Object} params - 查询参数
 * @param {string} params.patient_id - 患者ID（可选）
 * @param {number} params.page - 页码，默认1
 * @param {number} params.per_page - 每页数量，默认10
 */
export function getDiagnosisHistory(params = {}) {
    return request({
        url: '/api/diagnosis/history',
        method: 'get',
        params
    })
}

/**
 * 获取单条诊断记录详情
 * @param {number} id - 诊断记录ID
 */
export function getDiagnosisDetail(id) {
    return request({
        url: `/api/diagnosis/${id}`,
        method: 'get'
    })
}
