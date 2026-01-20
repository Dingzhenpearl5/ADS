import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'
import { refreshToken as apiRefreshToken } from './auth'

const service = axios.create({
    baseURL: process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:5003',
    timeout: 60000 // AI预测可能较慢，设置较长超时
})

let isRefreshing = false // 是否正在刷新token

// 请求拦截器
service.interceptors.request.use(
    async config => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`
            
            // 跳过刷新token接口本身的检查，避免递归
            // 同时跳过登录后 1 分钟内的刷新检查（登录后 token 不会立即过期）
            const loginTime = localStorage.getItem('token_login_time')
            const skipRefreshCheck = config.url.includes('/refresh-token') 
                || config.url.includes('/login')
                || (loginTime && (Date.now() - parseInt(loginTime) < 60000)) // 1分钟内
            
            if (!skipRefreshCheck) {
                // 检查token是否即将过期(剩余1小时内)
                const expireTime = localStorage.getItem('token_expire_time')
                if (expireTime) {
                    const timeLeft = new Date(expireTime) - new Date()
                    const oneHour = 60 * 60 * 1000
                    
                    // Token即将过期且不在刷新中,自动刷新
                    if (timeLeft < oneHour && timeLeft > 0 && !isRefreshing) {
                        isRefreshing = true
                        try {
                            const res = await apiRefreshToken()
                            if (res.status === 1) {
                                localStorage.setItem('token', res.data.token)
                                localStorage.setItem('token_expire_time', res.data.expire_time)
                                config.headers['Authorization'] = `Bearer ${res.data.token}`
                                console.log('[Token] 自动刷新成功')
                            }
                        } catch (error) {
                            console.error('[Token] 自动刷新失败:', error)
                            // 刷新失败，清除token（但不显示错误提示，由响应拦截器处理）
                            if (error.response?.status === 401) {
                                localStorage.removeItem('token')
                                localStorage.removeItem('userInfo')
                                localStorage.removeItem('token_expire_time')
                                localStorage.removeItem('token_login_time')
                            }
                        } finally {
                            isRefreshing = false
                        }
                    }
                }
            }
        }
        return config
    },
    error => {
        console.error('请求错误:', error)
        return Promise.reject(error)
    }
)

// 响应拦截器
service.interceptors.response.use(
    response => {
        return response.data
    },
    error => {
        console.error('响应错误:', error)
        
        // 静默处理 Token 刷新失败
        if (error.config?.url?.includes('/refresh-token')) {
            console.error('[Token] 刷新失败，但不显示错误提示')
            return Promise.reject(error)
        }
        
        // 只有在确实是 401 认证错误时才跳转登录页
        if (error.response && error.response.status === 401) {
            // 避免在登录页面重复跳转
            if (router.currentRoute.value.path !== '/login') {
                localStorage.removeItem('token')
                localStorage.removeItem('userInfo')
                localStorage.removeItem('token_expire_time')
                ElMessage.error('登录已过期，请重新登录')
                router.push('/login')
            }
        } else if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
            ElMessage.error('请求超时，请稍后重试')
        } else if (error.message === 'Network Error') {
            // 只在非登录接口时显示网络错误
            if (!error.config?.url?.includes('/login')) {
                ElMessage.error('网络连接失败，请检查后端服务是否启动')
            }
        } else {
            ElMessage.error(error.response?.data?.error || error.message || '请求失败')
        }
        return Promise.reject(error)
    }
)

export default service
