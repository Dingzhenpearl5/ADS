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
      <p>© 2023 肿瘤辅助诊断系统 | CTAI System</p>
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
        console.log('Already logged in, redirecting to /home')
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
        console.log('Attempting login for:', loginForm.username)
        const res = await login({
          username: loginForm.username,
          password: loginForm.password
        })
        
        console.log('Login response:', res)
        
        if (res.status === 1) {
          const { token } = res.data
          const user = res.data
          
          localStorage.setItem('token', token)
          localStorage.setItem('userInfo', JSON.stringify(user))
          
          if (rememberMe.value) {
            localStorage.setItem('rememberedUsername', loginForm.username)
          } else {
            localStorage.removeItem('rememberedUsername')
          }
          
          ElMessage.success(`欢迎回来，${user.name || user.username || '用户'}！`)
          console.log('Login successful, pushing to /home')
          router.push('/home')
        } else {
          ElMessage.error(res.error || '登录失败')
        }
      } catch (error) {
        console.error('登录请求失败:', error)
        ElMessage.error('登录请求失败，请检查网络或后端服务')
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
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.login-content {
  width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo-container {
  margin-bottom: 10px;
}

.system-title {
  font-size: 28px;
  color: #303133;
  margin: 10px 0;
  font-weight: 600;
}

.system-subtitle {
  font-size: 14px;
  color: #909399;
  letter-spacing: 1px;
}

.login-card {
  border-radius: 15px;
  padding: 20px;
  border: none;
}

.login-title {
  text-align: center;
  font-size: 22px;
  color: #409EFF;
  margin-bottom: 30px;
}

.login-form {
  margin-top: 20px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  margin-top: 10px;
}

.login-footer {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.account-info {
  font-size: 13px;
  color: #909399;
  line-height: 1.8;
}

.account-info span {
  font-weight: bold;
  margin-right: 5px;
}

.copyright {
  margin-top: 50px;
  font-size: 12px;
  color: #909399;
}
</style>