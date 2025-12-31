<template>
  <div class="content-container">
    <el-row :gutter="24">
      <!-- Left Column: Patient Info & Actions -->
      <el-col :lg="6" :md="8" :sm="24">
        <div class="side-panel">
          <PatientInfo 
            :patient="displayPatient" 
            :loading="loading"
            @search="fetchPatientData"
          />
          
          <div class="action-card custom-card">
            <div class="section-title">
              <el-icon><Operation /></el-icon>
              <span>诊断操作</span>
            </div>
            <div class="action-btns">
              <el-button 
                type="primary" 
                size="large" 
                class="start-btn"
                @click="handleStartDiagnosis" 
                :loading="loading"
                :disabled="!url1"
              >
                <el-icon><VideoPlay /></el-icon>
                <span>开始 AI 辅助诊断</span>
              </el-button>
              <p class="hint-text" v-if="!url1">请先上传 CT 影像文件</p>
            </div>
          </div>
        </div>
      </el-col>

      <!-- Middle Column: Image Workspace -->
      <el-col :lg="12" :md="16" :sm="24">
        <ImageWorkspace 
          :url1="url1"
          :url2="url2"
          :src-list="srcList"
          :src-list1="srcList1"
          :loading="loading"
          :show-upload-button="!url1"
          :wait-return="progressStatus"
          @upload="handleFile"
        />
      </el-col>

      <!-- Right Column: Feature Analysis -->
      <el-col :lg="6" :md="24" :sm="24">
        <FeatureAnalysis 
          :feature-list="featureList" 
          :loading="loading"
          :area-data="areaData"
          :perimeter-data="perimeterData"
          :show-upload-button="!url1"
          @upload="handleFile"
        />
      </el-col>
    </el-row>

    <!-- Diagnosis Progress Dialog -->
    <el-dialog 
      v-model="isProcessing" 
      title="AI 诊断分析中" 
      :close-on-click-modal="false"
      :show-close="false"
      width="400px"
      center
      class="custom-dialog"
    >
      <div class="progress-content">
        <el-progress 
          type="dashboard" 
          :percentage="percentage" 
          :color="progressColors"
          :stroke-width="10"
          :width="180"
        >
          <template #default="{ percentage }">
            <div class="percentage-value">{{ percentage }}%</div>
            <div class="percentage-label">完成度</div>
          </template>
        </el-progress>
        <div class="status-info">
          <el-icon class="is-loading" v-if="percentage < 100"><Loading /></el-icon>
          <el-icon color="#67c23a" v-else><Check /></el-icon>
          <span>{{ progressStatus }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Operation, VideoPlay, Loading, Check } from '@element-plus/icons-vue'

import PatientInfo from '../../patient/components/PatientInfo.vue'
import ImageWorkspace from '../components/ImageWorkspace.vue'
import FeatureAnalysis from '../components/FeatureAnalysis.vue'

import { getPatientInfo } from '../../../services/patient'
import { startTask, downloadTemplate, uploadDcm } from '../../../services/task'
import { useAiPrediction } from '../../../composables/useAiPrediction'

const route = useRoute()
const { 
  percentage, 
  progressStatus, 
  isProcessing, 
  resultData, 
  initSocket 
} = useAiPrediction()

// State
const loading = ref(false)
const url1 = ref('')
const url2 = ref('')
const srcList = ref([])
const srcList1 = ref([])
const featureList = ref([])
const areaData = ref(0)
const perimeterData = ref(0)

// 监听 AI 预测结果
watch(resultData, (newData) => {
  if (newData.url2) {
    url2.value = newData.url2
    srcList1.value = [newData.url2]
    featureList.value = newData.featureList
    areaData.value = newData.area
    perimeterData.value = newData.perimeter
    loading.value = false
  }
}, { deep: true })

const patient = ref({
  id: '',
  name: '',
  gender: '',
  age: '',
  phone: '',
  part: ''
})

const progressColors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 },
]

const displayPatient = computed(() => {
  if (!patient.value) return {}
  return {
    '姓名': patient.value.name || '未填写',
    '性别': patient.value.gender || '未填写',
    '年龄': patient.value.age || '未填写',
    '电话': patient.value.phone || '未填写',
    '部位': patient.value.part || '未填写'
  }
})

// Methods
const fetchPatientData = async (id) => {
  if (!id) return
  loading.value = true
  try {
    const res = await getPatientInfo(id)
    if (res.status === 1 && res.data) {
      const d = res.data
      patient.value = {
        id: d['ID'] || '',
        name: d['姓名'] || '',
        gender: d['性别'] || '',
        age: d['年龄'] || '',
        phone: d['电话'] || '',
        part: d['部位'] || ''
      }
      ElMessage.success('患者信息获取成功')
    } else {
      ElMessage.warning(res.error || '未找到该患者信息')
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('获取患者信息失败')
  } finally {
    loading.value = false
  }
}

const handleFile = async (file) => {
  loading.value = true
  try {
    const res = await uploadDcm(file)
    
    if (res.status === 1) {
      url1.value = res.image_url
      srcList.value = [res.image_url]
      // 上传成功后清空之前的预测结果
      url2.value = ''
      srcList1.value = []
      featureList.value = []
      areaData.value = 0
      perimeterData.value = 0
      
      ElMessage.success('影像上传成功，请点击"开始AI辅助诊断"')
    } else {
      ElMessage.error(res.error || '上传失败')
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('上传失败: ' + (e.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleStartDiagnosis = async () => {
  if (!url1.value) {
    return ElMessage.warning('请先上传 CT 影像')
  }
  
  loading.value = true
  isProcessing.value = true
  percentage.value = 0
  progressStatus.value = '正在进行AI分析...'
  
  try {
    // 模拟进度更新
    const progressInterval = setInterval(() => {
      if (percentage.value < 90) {
        percentage.value += 10
        if (percentage.value === 30) progressStatus.value = '预处理图像...'
        if (percentage.value === 50) progressStatus.value = '模型推理中...'
        if (percentage.value === 70) progressStatus.value = '提取特征...'
        if (percentage.value === 90) progressStatus.value = '生成结果...'
      }
    }, 400)
    
    const res = await startTask({ imageUrl: url1.value })
    
    clearInterval(progressInterval)
    percentage.value = 100
    progressStatus.value = '分析完成'
    
    if (res.status === 1) {
      url2.value = res.draw_url
      srcList1.value = [res.draw_url]
      
      // 处理特征数据
      if (res.image_info) {
        const info = res.image_info
        featureList.value = Object.entries(info).map(([key, value]) => ({
          name: key,
          value: typeof value === 'number' ? value.toFixed(4) : value
        }))
        areaData.value = info['面积'] || info['area'] || 0
        perimeterData.value = info['周长'] || info['perimeter'] || 0
      }
      
      ElMessage.success('AI诊断分析完成')
    } else {
      ElMessage.error(res.error || '分析失败')
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('诊断失败: ' + (e.message || '未知错误'))
  } finally {
    loading.value = false
    setTimeout(() => {
      isProcessing.value = false
    }, 1000)
  }
}

const downTemplate = async () => {
  try {
    const res = await downloadTemplate()
    // 处理 blob 下载
    const blob = new Blob([res], { type: 'application/zip' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'testfile.zip'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('测试数据下载成功')
  } catch (e) {
    console.error(e)
    ElMessage.error('下载失败')
  }
}

// Lifecycle
onMounted(() => {
  initSocket()
  const id = route.query.id || '20190001'
  fetchPatientData(id)
})

// Expose methods for Home.vue
defineExpose({
  downTemplate,
  handleFile
})
</script>

<style scoped>
.content-container {
  padding: 10px 0;
}

.side-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.action-card {
  padding: 20px;
}

.action-btns {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
}

.start-btn {
  width: 100%;
  height: 50px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.hint-text {
  font-size: 12px;
  color: #909399;
  margin: 0;
}

.progress-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.percentage-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.percentage-label {
  font-size: 12px;
  color: #909399;
}

.status-info {
  margin-top: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  color: #606266;
}

:deep(.custom-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

:deep(.custom-dialog .el-dialog__header) {
  margin-right: 0;
  padding-bottom: 20px;
  border-bottom: 1px solid #f1f5f9;
}
</style>
