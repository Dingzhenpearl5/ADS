<template>
  <div class="content-container">
    <el-row :gutter="20">
      <!-- 左侧：患者信息与操作 -->
      <el-col :span="6">
        <PatientInfo 
          :patient="displayPatient" 
          :loading="loading"
          @search="fetchPatientData"
        />
        <div style="margin-top: 20px; text-align: center;">
          <el-button type="success" size="large" @click="handleStartDiagnosis" :loading="loading" round>
            开始辅助诊断
          </el-button>
        </div>
      </el-col>

      <!-- 中间：图像工作区 -->
      <el-col :span="12">
        <ImageWorkspace 
          :url1="url1"
          :url2="url2"
          :src-list="srcList"
          :src-list1="srcList1"
          :loading="loading"
        />
      </el-col>

      <!-- 右侧：特征分析 -->
      <el-col :span="6">
        <FeatureAnalysis :feature-list="featureList" />
      </el-col>
    </el-row>

    <!-- 诊断进度弹窗 -->
    <el-dialog 
      v-model="dialogTableVisible" 
      title="诊断进度" 
      :close-on-click-modal="false"
      :show-close="false"
      width="30%"
      center
    >
      <div class="progress-container">
        <el-progress type="dashboard" :percentage="percentage" :color="colors" />
        <p class="progress-text">{{ progressStatus }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, defineExpose } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { io } from 'socket.io-client'
import PatientInfo from './PatientInfo.vue'
import ImageWorkspace from './ImageWorkspace.vue'
import FeatureAnalysis from './FeatureAnalysis.vue'
import { getPatientInfo } from '../api/patient'
import { startTask, downloadTemplate, uploadDcm } from '../api/task'

const route = useRoute()

// 状态变量
const loading = ref(false)
const dialogTableVisible = ref(false)
const percentage = ref(0)
const progressStatus = ref('正在准备诊断任务...')
const url1 = ref('')
const url2 = ref('')
const srcList = ref([])
const srcList1 = ref([])
const featureList = ref([])

const patient = ref({
  id: '',
  name: '',
  gender: '',
  age: '',
  phone: '',
  part: ''
})

// 映射显示用的患者信息
const displayPatient = computed(() => ({
  '姓名': patient.value.name,
  '性别': patient.value.gender,
  '年龄': patient.value.age,
  '电话': patient.value.phone,
  '部位': patient.value.part
}))

let socket = null
let progressTimer = null

// 初始化 Socket
const initSocket = () => {
  const socketUrl = process.env.VUE_APP_SOCKET_URL || 'http://127.0.0.1:5003'
  console.log('[Socket] Connecting to:', socketUrl)
  socket = io(socketUrl)
  
  socket.on('connect', () => console.log('[Socket] Connected'))
  
  socket.on('task_completed', (data) => {
    console.log('[Socket] Task completed:', data)
    updateResult(data)
  })
  
  socket.on('task_failed', (data) => {
    console.error('[Socket] Task failed:', data)
    handleTaskFailed(data.error)
  })
}

// 更新预测结果
const updateResult = (data) => {
  stopProgress()
  percentage.value = 100
  url1.value = data.image_url
  srcList.value = [data.image_url]
  url2.value = data.draw_url
  srcList1.value = [data.draw_url]
  
  loading.value = false
  dialogTableVisible.value = false
  
  // 处理特征数据
  const info = data.image_info
  const list = []
  if (info) {
    Object.keys(info).forEach(key => {
      list.push({
        name: key,
        area: info[key].area,
        perimeter: info[key].perimeter
      })
    })
  }
  featureList.value = list
  
  ElMessage.success('诊断完成')
}

const handleTaskFailed = (error) => {
  stopProgress()
  loading.value = false
  dialogTableVisible.value = false
  ElMessage.error('诊断失败: ' + error)
}

// 进度条控制
const startProgress = () => {
  percentage.value = 0
  dialogTableVisible.value = true
  progressStatus.value = '正在分析图像...'
  progressTimer = setInterval(() => {
    if (percentage.value < 95) {
      percentage.value += Math.floor(Math.random() * 5)
      if (percentage.value > 95) percentage.value = 95
    }
  }, 500)
}

const stopProgress = () => {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
}

// 开始诊断
const handleStartDiagnosis = async () => {
  if (!patient.value.id) {
    ElMessage.warning('未找到患者信息')
    return
  }
  
  loading.value = true
  startProgress()
  
  try {
    console.log('Starting task for patient:', patient.value.id)
    await startTask(patient.value.id)
  } catch (error) {
    handleTaskFailed(error.message)
  }
}

// 获取患者数据
const fetchPatientData = async (id) => {
  if (!id) return
  try {
    console.log('Fetching patient data for:', id)
    const res = await getPatientInfo(id)
    if (res.status === 1) {
      const d = res.data
      if (d) {
        patient.value = {
          id: d.ID || d.id || id,
          name: d['姓名'] || d.name || '',
          gender: d['性别'] || d.gender || '',
          age: d['年龄'] || d.age || '',
          phone: d['电话'] || d.phone || '',
          part: d['部位'] || d.part || ''
        }
      }
    } else {
      ElMessage.error(res.error || '获取患者信息失败')
    }
  } catch (error) {
    console.error('Fetch patient error:', error)
    ElMessage.error('获取患者信息失败')
  }
}

// 下载模板
const downTemplate = async () => {
  try {
    const res = await downloadTemplate()
    const url = window.URL.createObjectURL(new Blob([res]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'template.dcm')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 处理文件上传
const handleFile = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  loading.value = true
  try {
    const res = await uploadDcm(formData)
    if (res.status === 1) {
      ElMessage.success('上传成功')
      if (res.patient_id) {
        fetchPatientData(res.patient_id)
      }
    } else {
      ElMessage.error(res.error || '上传失败')
    }
  } catch (error) {
    ElMessage.error('上传请求失败')
  } finally {
    loading.value = false
  }
}

// 暴露方法给父组件
defineExpose({
  downTemplate,
  handleFile
})

const colors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 },
]

onMounted(() => {
  const id = route.query.id
  if (id) {
    fetchPatientData(id)
  }
  initSocket()
})

onUnmounted(() => {
  if (socket) socket.disconnect()
  stopProgress()
})
</script>

<style scoped>
.content-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 120px);
}

.progress-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.progress-text {
  margin-top: 20px;
  font-size: 16px;
  color: #606266;
}
</style>