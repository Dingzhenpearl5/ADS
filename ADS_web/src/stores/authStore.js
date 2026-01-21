import { defineStore } from 'pinia'
import { login as apiLogin, logout as apiLogout, checkAuth as apiCheckAuth } from '../services/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: JSON.parse(localStorage.getItem('userInfo') || '{}')
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    userRole: (state) => state.userInfo.role || 'user',
    userPermissions: (state) => state.userInfo.permissions || ['rectum']
  },
  
  actions: {
    async login(credentials) {
      try {
        const res = await apiLogin(credentials)
        if (res.status === 1) {
          this.token = res.data.token
          this.userInfo = res.data
          localStorage.setItem('token', this.token)
          localStorage.setItem('userInfo', JSON.stringify(this.userInfo))
          // 存储过期时间
          if (res.data.expire_time) {
            localStorage.setItem('token_expire_time', res.data.expire_time)
          }
          // 记录登录时间，用于跳过刷新检查
          localStorage.setItem('token_login_time', Date.now().toString())
          return res
        }
        throw new Error(res.error || '登录失败')
      } catch (error) {
        console.error('Login error:', error)
        throw error
      }
    },
    
    async logout() {
      try {
        await apiLogout()
      } finally {
        this.token = ''
        this.userInfo = {}
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        localStorage.removeItem('token_expire_time')
        localStorage.removeItem('token_login_time')
      }
    },
    
    async checkAuth() {
      if (!this.token) return false
      try {
        const res = await apiCheckAuth()
        if (res.status === 1) {
          this.userInfo = res.data
          localStorage.setItem('userInfo', JSON.stringify(this.userInfo))
          return true
        }
        this.logout()
        return false
      } catch (error) {
        this.logout()
        return false
      }
    }
  }
})
