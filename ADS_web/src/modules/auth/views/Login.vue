<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-header">
        <div class="logo-container">
          <el-icon class="logo-icon" :size="40" color="#409EFF"><Monitor /></el-icon>
        </div>
        <h1 class="system-title">直肠肿瘤辅助诊断系统</h1>
        <p class="system-subtitle">Rectal Tumor Aided Diagnosis System</p>
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
      <p>© {{ new Date().getFullYear() }} 直肠肿瘤辅助诊断系统</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Monitor } from '@element-plus/icons-vue'
import { useAuthStore } from '../../../stores/authStore'

const router = useRouter()
const authStore = useAuthStore()
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
  if (authStore.isLoggedIn) {
    const isValid = await authStore.checkAuth()
    if (isValid) {
      router.push('/home')
    }
  }
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await authStore.login({
          username: loginForm.username,
          password: loginForm.password
        })
        
        if (rememberMe.value) {
          localStorage.setItem('rememberedUsername', loginForm.username)
        } else {
          localStorage.removeItem('rememberedUsername')
        }
        
        ElMessage.success({
          message: `欢迎回来，${authStore.userInfo.name || authStore.userInfo.username || '用户'}！`,
          duration: 2000
        })
        
        // 延迟跳转，让用户看到成功消息
        setTimeout(() => {
          router.push('/home')
        }, 500)
      } catch (error) {
        // 优化错误提示
        const errorMsg = error.response?.data?.error || error.message || '登录失败，请稍后重试'
        ElMessage.error({
          message: errorMsg,
          duration: 3000,
          showClose: true
        })
        console.error('[Login] 登录错误:', error)
      } finally {
        loading.value = false
      }
    } else {
      ElMessage.warning('请正确填写登录信息')
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