import request from '../utils/request'

export function getPatientInfo(id) {
    const params = id ? { id } : {}
    return request({
        url: '/api/patient',
        method: 'get',
        params
    })
}
