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
