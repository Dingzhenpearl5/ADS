<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-header">
        <div class="logo-container">
          <el-icon class="logo-icon" :size="40" color="#409EFF"><Monitor /></el-icon>
        </div>
        <h1 class="system-title">肿瘤辅助诊断系统</h1>
        <p class="system-subtitle">Tumor Aided Diagnosis System</p>
      </div>
      
      <el-card class="login-card" shadow="hover">
        <h2 class="login-title">用户登录</h2>
        <el-form :model="loginForm" :rules="rules" ref="loginFormRef" size="large" class="login-form">
          <el-form-item prop="username">
            <el-input 
              v-model="loginForm.username" 
              placeholder="请输入用户名"
              :prefix-icon="User">
            </el-input>
          </el-form-item>
          <el-form-item prop="password">
            <el-input 
              type="password" 
              v-model="loginForm.password" 
              placeholder="请输入密码" 
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin">
            </el-input>
          </el-form-item>
          
          <div class="form-options">
            <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            <el-link type="primary" :underline="false">忘记密码?</el-link>
          </div>
          
          <el-form-item>
            <el-button type="primary" @click="handleLogin" :loading="loading" class="login-button" round>
              {{ loading ? '登录中...' : '立即登录' }}
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="login-footer">
          <div class="account-info">
            <p><span>管理员:</span> admin / 123456</p>
            <p><span>医生:</span> doctor / doctor123</p>
          </div>
        </div>
      </el-card>
    </div>
    
    <div class="copyright">
      <p> 2023 肿瘤辅助诊断系统 | CTAI System</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Monitor } from '@element-plus/icons-vue'
import { login, checkAuth } from '../api/auth'

const router = useRouter()
const loginFormRef = ref(null)
const loading = ref(false)
const rememberMe = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 4, max: 30, message: '密码长度在 4 到 30 个字符', trigger: 'blur' }
  ]
}

const checkLoginStatus = async () => {
  const token = localStorage.getItem('token')
  if (token) {
    try {
      const res = await checkAuth()
      if (res.status === 1) {
        router.push('/home')
      }
    } catch (error) {
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
    }
  }
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const res = await login({
          username: loginForm.username,
          password: loginForm.password
        })
        
        if (res.status === 1) {
          const { token, user } = res
          localStorage.setItem('token', token)
          localStorage.setItem('userInfo', JSON.stringify(user))
          
          if (rememberMe.value) {
            localStorage.setItem('rememberedUsername', loginForm.username)
          } else {
            localStorage.removeItem('rememberedUsername')
          }
          
          ElMessage.success(`欢迎回来，${user.name}！`)
          router.push('/home')
        } else {
          ElMessage.error(res.error || '登录失败')
        }
      } catch (error) {
        console.error('登录请求失败:', error)
      } finally {
        loading.value = false
      }
    }
  })
}

onMounted(() => {
  checkLoginStatus()
  const savedUsername = localStorage.getItem('rememberedUsername')
  if (savedUsername) {
    loginForm.username = savedUsername
    rememberMe.value = true
  }
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  background-image: url('https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80');
  background-size: cover;
  background-position: center;
  position: relative;
}

.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 0;
}

.login-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 450px;
  padding: 20px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
  color: #fff;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.logo-container {
  background: rgba(255, 255, 255, 0.9);
  width: 70px;
  height: 70px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 auto 15px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.2);
}

.system-title {
  font-size: 28px;
  margin: 0 0 5px;
  font-weight: 600;
  letter-spacing: 1px;
}

.system-subtitle {
  font-size: 14px;
  margin: 0;
  opacity: 0.9;
  font-weight: 300;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.login-card {
  width: 100%;
  border-radius: 16px;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  border: none;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.login-title {
  text-align: center;
  color: #303133;
  margin: 10px 0 25px;
  font-size: 20px;
  font-weight: 500;
}

.login-form {
  padding: 0 10px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  font-size: 16px;
  padding: 12px 0;
  letter-spacing: 2px;
  background: linear-gradient(90deg, #409EFF 0%, #3a8ee6 100%);
  border: none;
  transition: all 0.3s;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

.login-footer {
  margin-top: 10px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.account-info {
  background: #f0f9eb;
  padding: 10px;
  border-radius: 6px;
  font-size: 12px;
  color: #67c23a;
}

.account-info p {
  margin: 3px 0;
  display: flex;
  justify-content: space-between;
}

.account-info span {
  font-weight: bold;
}

.copyright {
  position: absolute;
  bottom: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  z-index: 1;
}

@media (max-width: 480px) {
  .login-content {
    padding: 15px;
  }
  
  .system-title {
    font-size: 24px;
  }
}
</style>
