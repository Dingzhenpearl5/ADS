<template>
  <div id="Content">
    <!-- 使用须知对话框 -->
    <el-dialog
      title="肿瘤辅助诊断系统使用须知"
      v-model="centerDialogVisible"
      width="65%"
      :before-close="handleClose"
    >
      <el-steps :active="activeStep" finish-status="success">
        <el-step title="步骤1" description="下载测试CT文件" />
        <el-step title="步骤2" description="上传CT图像并预测" />
        <el-step title="步骤3" description="查看辅助诊断结果" />
      </el-steps>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="downTemplate">下载测试CT图像</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- AI预测进度对话框 -->
    <el-dialog
      title="AI预测中"
      v-model="dialogTableVisible"
      :show-close="false"
      :close-on-press-escape="false"
      :append-to-body="true"
      :close-on-click-modal="false"
      :center="true"
    >
      <el-progress :percentage="percentage"></el-progress>
      <template #footer>
        <span class="dialog-footer">非GPU学生服务器性能有限，请耐心等待约一分钟</span>
      </template>
    </el-dialog>

    <!-- 侧边栏：病人信息 -->
    <div id="aside">
      <PatientInfo :patient="patient" @search="searchPatient" />
    </div>

    <!-- 主体内容：图像与特征分析 -->
    <div id="CT">
      <ImageWorkspace 
        :url1="url1" 
        :url2="url2" 
        :srcList="srcList" 
        :srcList1="srcList1"
        :loading="loading"
        :showUploadButton="showUploadButton"
        :waitReturn="waitReturn"
        @upload="handleFile"
      />

      <div id="info_patient">
        <FeatureAnalysis 
          :featureList="featureList"
          :loading="loading"
          :showUploadButton="showUploadButton"
          :areaData="areaData"
          :perimeterData="perimeterData"
          @upload="handleFile"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, defineExpose } from 'vue'
import { ElMessageBox, ElMessage, ElNotification } from 'element-plus'
import { io } from 'socket.io-client'
import PatientInfo from './PatientInfo.vue'
import ImageWorkspace from './ImageWorkspace.vue'
import FeatureAnalysis from './FeatureAnalysis.vue'
import { getPatientInfo } from '../api/patient'
import { uploadDcm, downloadTemplate as apiDownloadTemplate } from '../api/task'

// 状态变量
const centerDialogVisible = ref(true)
const dialogTableVisible = ref(false)
const percentage = ref(0)
const loading = ref(false)
const showUploadButton = ref(true)
const activeStep = ref(0)

const url1 = ref('')
const url2 = ref('')
const srcList = ref([])
const srcList1 = ref([])
const waitReturn = ref('等待上传')
const featureList = ref([])
const areaData = ref(0)
const perimeterData = ref(0)

const patient = ref({
  ID: '',
  姓名: '',
  性别: '',
  年龄: '',
  电话: '',
  部位: ''
})

let socket = null
let progressTimer = null

// 初始化 Socket
const initSocket = () => {
  const socketUrl = process.env.VUE_APP_SOCKET_URL || 'http://127.0.0.1:5003'
  socket = io(socketUrl)
  
  socket.on('connect', () => console.log('[Socket] Connected'))
  
  socket.on('task_completed', (data) => {
    updateResult(data)
  })
  
  socket.on('task_failed', (data) => {
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
  Object.keys(info).forEach(key => {
    if (Array.isArray(info[key])) {
      list.push([info[key][0], info[key][1], key])
    }
  })
  featureList.value = list
  
  areaData.value = parseInt(info.area?.[1] || 0)
  perimeterData.value = parseInt(info.perimeter?.[1] || 0)
  
  ElNotification({
    title: '预测成功',
    message: '点击图片查看大图，下方显示肿瘤特征值供参考',
    type: 'success'
  })
}

const handleTaskFailed = (error) => {
  stopProgress()
  dialogTableVisible.value = false
  loading.value = false
  ElMessage.error('AI预测失败: ' + error)
}

// 进度条模拟
const startProgress = () => {
  percentage.value = 0
  progressTimer = setInterval(() => {
    if (percentage.value < 95) {
      percentage.value += Math.floor(Math.random() * 5) + 1
    }
  }, 500)
}

const stopProgress = () => {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
}

// 业务方法
const searchPatient = async (id) => {
  try {
    const res = await getPatientInfo(id)
    if (res.status === 1) {
      patient.value = res.data
      ElMessage.success('获取病人信息成功')
    } else {
      ElMessage.warning(res.error || '未找到该病人')
    }
  } catch (e) {
    console.error(e)
  }
}

const handleFile = async (file) => {
  if (!file) return
  
  loading.value = true
  showUploadButton.value = false
  dialogTableVisible.value = true
  startProgress()
  
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const res = await uploadDcm(formData)
    if (res && res.image_url) {
      updateResult(res)
    }
  } catch (e) {
    handleTaskFailed(e.message)
  }
}

const downTemplate = async () => {
  try {
    const data = await apiDownloadTemplate()
    const url = window.URL.createObjectURL(new Blob([data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', '测试CT图像.zip')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('下载成功')
    centerDialogVisible.value = false
    activeStep.value = 1
  } catch (e) {
    ElMessage.error('下载失败')
  }
}

const handleClose = (done) => {
  ElMessageBox.confirm('确认关闭？').then(() => done()).catch(() => {})
}

// 生命周期
onMounted(() => {
  initSocket()
  searchPatient() // 默认加载
})

onUnmounted(() => {
  if (socket) socket.disconnect()
  stopProgress()
})

// 暴露给父组件
defineExpose({
  downTemplate,
  handleFile
})
</script>

<style scoped>
#Content {
  width: 85%;
  margin: 15px auto;
  display: flex;
  min-width: 1200px;
  align-items: flex-start;
}

#aside {
  width: 25%;
  padding: 30px;
  margin-right: 40px;
  position: sticky;
  top: 20px;
}

#CT {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

#info_patient {
  width: 100%;
}
</style>
