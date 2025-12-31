import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router' // 稍后我们会重构路由到独立文件

const service = axios.create({
    baseURL: process.env.VUE_APP_API_BASE_URL,
    timeout: 60000 // AI预测可能较慢，设置较长超时
})

// 请求拦截器
service.interceptors.request.use(
    config => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`
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
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('token')
            localStorage.removeItem('userInfo')
            router.push('/login')
            ElMessage.error('登录已过期，请重新登录')
        } else {
            ElMessage.error(error.message || '网络请求失败')
        }
        return Promise.reject(error)
    }
)

export default service
