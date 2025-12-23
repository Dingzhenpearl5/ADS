import request from '../utils/request'

export function login(data) {
    return request({
        url: '/api/login',
        method: 'post',
        data
    })
}

export function checkAuth() {
    return request({
        url: '/api/check-auth',
        method: 'get'
    })
}
