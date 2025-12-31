<template>
  <div class="app-layout">
    <Header 
      @download-template="handleDownloadTemplate"
      @upload-file="handleUploadFile"
    />
    
    <main class="main-content">
      <router-view />
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import Header from './Header.vue'
import Footer from './Footer.vue'
import { downloadTemplate, uploadDcm } from '@/services/task'
import { ElMessage } from 'element-plus'

const router = useRouter()

const handleDownloadTemplate = async () => {
  try {
    const res = await downloadTemplate()
    const blob = new Blob([res.data], { type: 'application/zip' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'test_data.zip'
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  }
}

const handleUploadFile = (file) => {
  // 如果不在工作台页面，先跳转
  if (router.currentRoute.value.path !== '/home') {
    router.push('/home')
  }
  // 触发全局事件，让DiagnosisView处理
  window.dispatchEvent(new CustomEvent('upload-ct-file', { detail: file }))
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f0f2f5;
  background-image: 
    radial-gradient(at 0% 0%, rgba(64, 158, 255, 0.05) 0px, transparent 50%),
    radial-gradient(at 100% 0%, rgba(103, 194, 58, 0.05) 0px, transparent 50%);
}

.main-content {
  flex: 1;
  overflow-y: auto;
}
</style>
