import request from '../utils/request'

export function getPatientInfo(id) {
    return request({
        url: '/api/patient',
        method: 'get',
        params: { id }
    })
}
