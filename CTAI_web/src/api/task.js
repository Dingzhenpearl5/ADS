import request from '../utils/request'

export function uploadDcm(data) {
    return request({
        url: '/api/upload',
        method: 'post',
        data,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

export function downloadTemplate() {
    return request({
        url: '/api/download_template',
        method: 'get',
        responseType: 'blob'
    })
}

export function startTask(patientId) {
    return request({
        url: '/api/predict',
        method: 'post',
        data: { id: patientId }
    })
}
