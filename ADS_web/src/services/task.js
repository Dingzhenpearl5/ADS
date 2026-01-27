import request from './request'

export function uploadDcm(file) {
    const formData = new FormData()
    formData.append('file', file)
    return request({
        url: '/upload',
        method: 'post',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

export function downloadTemplate() {
    return request({
        url: '/download',
        method: 'get',
        responseType: 'blob'
    })
}

// 启动AI预测任务
export function startTask(data) {
    return request({
        url: '/api/predict',
        method: 'post',
        data
    })
}

// 启动病情分析 (DeepSeek)
export function analyzeCondition(data) {
    return request({
        url: '/api/analyze',
        method: 'post',
        data
    })
}
