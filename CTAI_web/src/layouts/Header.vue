<template>
  <header class="app-header">
    <div class="header-content">
      <!-- Logo & Title -->
      <div class="brand">
        <div class="logo-box">
          <el-icon :size="24" color="#fff"><Monitor /></el-icon>
        </div>
        <h1 class="title">{{ msg }}</h1>
      </div>

      <!-- Navigation -->
      <nav class="nav-section">
        <el-menu
          :default-active="activeIndex"
          mode="horizontal"
          class="custom-menu"
          @select="handleSelect"
        >
          <el-menu-item index="1">首页</el-menu-item>
          <el-menu-item index="2">工作台</el-menu-item>
          <el-menu-item index="3">历史记录</el-menu-item>
          <el-menu-item index="4" v-if="isAdmin">统计分析</el-menu-item>
        </el-menu>
      </nav>

      <!-- Actions & User -->
      <div class="actions">
        <div class="header-btns">
          <el-button type="primary" plain size="default" @click="$emit('download-template')">
            <el-icon><Download /></el-icon>
            <span>下载测试数据</span>
          </el-button>
          <el-button type="primary" size="default" @click="triggerUpload">
            <el-icon><Upload /></el-icon>
            <span>上传CT图像</span>
          </el-button>
        </div>

        <input
          type="file"
          ref="fileInput"
          style="display: none"
          accept=".dcm"
          @change="handleFileChange"
        />

        <div class="user-profile">
          <el-dropdown @command="handleCommand">
            <div class="user-info-wrapper">
              <el-avatar :size="36" :icon="UserFilled" class="user-avatar" />
              <div class="user-details">
                <span class="username">{{ authStore.userInfo.name || '用户' }}</span>
                <span class="role">{{ authStore.userInfo.role === 'admin' ? '管理员' : '医生' }}</span>
              </div>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item :icon="User">个人中心</el-dropdown-item>
                <el-dropdown-item :icon="Setting">系统设置</el-dropdown-item>
                <el-dropdown-item :icon="SwitchButton" command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  UserFilled,
  ArrowDown,
  User,
  Setting,
  SwitchButton,
  Download,
  Upload,
  Monitor
} from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/authStore'

defineProps({
  msg: {
    type: String,
    default: '直肠肿瘤辅助诊断系统'
  }
})

const emit = defineEmits(['download-template', 'upload-file'])

const router = useRouter()
const authStore = useAuthStore()
const activeIndex = ref('1')
const fileInput = ref(null)

// 判断是否是管理员
const isAdmin = computed(() => authStore.userInfo?.role === 'admin')

// 路由与菜单索引的映射
const routeMap = {
  '1': '/home',
  '2': '/workspace',
  '3': '/history',
  '4': '/statistics'
}

// 根据当前路由设置激活菜单
const updateActiveIndex = () => {
  const path = router.currentRoute.value.path
  
  // 特殊处理：诊断页面时高亮工作台
  if (path.startsWith('/diagnosis')) {
    activeIndex.value = '2'
    return
  }
  
  for (const [key, value] of Object.entries(routeMap)) {
    if (path === value) {
      activeIndex.value = key
      break
    }
  }
}

const handleSelect = (key) => {
  activeIndex.value = key
  const targetRoute = routeMap[key]
  if (targetRoute && router.currentRoute.value.path !== targetRoute) {
    router.push(targetRoute)
  }
}

const triggerUpload = () => {
  fileInput.value.click()
}

const handleFileChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    emit('upload-file', file)
    e.target.value = ''
  }
}

const handleCommand = (command) => {
  if (command === 'logout') {
    handleLogout()
  }
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch (e) {
    console.error('登出失败', e)
    router.push('/login')
  }
}

onMounted(() => {
  authStore.checkAuth()
  updateActiveIndex()
  
  // 监听路由变化
  router.afterEach(() => {
    updateActiveIndex()
  })
})
</script>

<style scoped>
.app-header {
  height: 70px;
  background-color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
}

.header-content {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-box {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 8px rgba(64, 158, 255, 0.3);
}

.title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: #2c3e50;
  letter-spacing: 0.5px;
}

.nav-section {
  flex: 1;
  margin: 0 50px;
}

.custom-menu {
  border-bottom: none !important;
  height: 70px;
  background-color: transparent !important;
}

.custom-menu :deep(.el-menu-item) {
  height: 70px;
  line-height: 70px;
  font-size: 16px;
  font-weight: 500;
}

.actions {
  display: flex;
  align-items: center;
  gap: 24px;
}

.header-btns {
  display: flex;
  gap: 12px;
}

.header-btns :deep(.el-button) {
  display: flex;
  align-items: center;
  gap: 6px;
  border-radius: 8px;
}

.user-profile {
  padding-left: 24px;
  border-left: 1px solid #ebeef5;
}

.user-info-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: background 0.2s;
}

.user-info-wrapper:hover {
  background-color: #f5f7fa;
}

.user-details {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.username {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.role {
  font-size: 12px;
  color: #909399;
}

.user-avatar {
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>


