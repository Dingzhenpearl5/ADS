import { defineStore } from 'pinia'
import { login as apiLogin, logout as apiLogout, checkAuth as apiCheckAuth } from '../services/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: JSON.parse(localStorage.getItem('userInfo') || '{}')
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    userRole: (state) => state.userInfo.role || 'user'
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
