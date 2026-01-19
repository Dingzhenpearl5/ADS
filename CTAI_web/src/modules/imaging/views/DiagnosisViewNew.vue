<template>
  <div class="diagnosis-container">
    <!-- 顶部面包屑导航 + 流程指示 -->
    <div class="top-section">
      <el-breadcrumb separator="/" class="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/home' }">工作台</el-breadcrumb-item>
        <el-breadcrumb-item>{{ partName }}诊断</el-breadcrumb-item>
      </el-breadcrumb>
      
      <div class="workflow-steps">
        <el-steps :active="currentStep" finish-status="success" align-center>
          <el-step title="上传影像" :icon="Upload" />
          <el-step title="AI分析" :icon="Cpu" />
          <el-step title="查看结果" :icon="DataAnalysis" />
        </el-steps>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <el-row :gutter="20">
        <!-- 左侧：患者信息 + 操作面板 -->
        <el-col :xl="5" :lg="6" :md="8" :sm="24">
          <div class="left-panel">
            <!-- 患者信息卡片 -->
            <el-card class="panel-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <el-icon><User /></el-icon>
                  <span>患者信息</span>
                </div>
              </template>
              
              <div class="search-box">
                <el-input 
                  v-model="searchId" 
                  placeholder="输入患者ID"
                  @keyup.enter="fetchPatientData(searchId)"
                  clearable
                >
                  <template #append>
                    <el-button :icon="Search" @click="fetchPatientData(searchId)" />
                  </template>
                </el-input>
              </div>

              <div v-if="!hasPatientData" class="empty-patient-info">
                <el-empty 
                  description="请输入患者ID查询信息" 
                  :image-size="80"
                />
              </div>

              <el-descriptions v-else :column="1" border size="small" class="patient-desc">
                <el-descriptions-item label="姓名">{{ patient.name }}</el-descriptions-item>
                <el-descriptions-item label="性别">{{ patient.gender }}</el-descriptions-item>
                <el-descriptions-item label="年龄">{{ patient.age }}</el-descriptions-item>
                <el-descriptions-item label="电话">{{ patient.phone }}</el-descriptions-item>
                <el-descriptions-item label="检查部位">{{ patient.part }}</el-descriptions-item>
              </el-descriptions>
            </el-card>

            <!-- 操作面板 -->
            <el-card class="panel-card action-panel" shadow="hover">
              <template #header>
                <div class="card-header">
                  <el-icon><Operation /></el-icon>
                  <span>诊断操作</span>
                </div>
              </template>

              <div class="action-content">
                <!-- 上传按钮 -->
                <el-upload
                  ref="uploadRef"
                  :auto-upload="false"
                  :show-file-list="false"
                  accept=".dcm"
                  :on-change="handleFileSelect"
                  class="upload-area"
                  drag
                >
                  <div class="upload-content">
                    <el-icon class="upload-icon" :size="40"><UploadFilled /></el-icon>
                    <div class="upload-text">
                      <p>拖拽文件到此处或 <em>点击上传</em></p>
                      <p class="upload-hint">支持 .dcm 格式</p>
                    </div>
                  </div>
                </el-upload>

                <!-- 当前文件 -->
                <div v-if="currentFile" class="current-file">
                  <el-icon><Document /></el-icon>
                  <span class="filename">{{ currentFile.name }}</span>
                  <el-button link type="danger" @click="clearFile">
                    <el-icon><Close /></el-icon>
                  </el-button>
                </div>

                <!-- 开始诊断按钮 -->
                <el-button 
                  type="primary" 
                  size="large"
                  class="start-btn"
                  :loading="loading"
                  :disabled="!url1"
                  @click="handleStartDiagnosis"
                >
                  <el-icon><VideoPlay /></el-icon>
                  开始 AI 辅助诊断
                </el-button>

                <p class="status-hint" v-if="!url1">
                  <el-icon><InfoFilled /></el-icon>
                  请先上传 CT 影像文件
                </p>
              </div>
            </el-card>
          </div>
        </el-col>

        <!-- 中间：影像工作区 -->
        <el-col :xl="13" :lg="12" :md="16" :sm="24">
          <el-card class="workspace-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><Picture /></el-icon>
                <span>影像工作区</span>
                <div class="header-extra" v-if="url1">
                  <el-tag type="success" size="small">已上传</el-tag>
                  <el-tag v-if="url2" type="primary" size="small">已诊断</el-tag>
                </div>
              </div>
            </template>

            <div class="image-grid">
              <!-- 原始图像 -->
              <div class="image-panel">
                <div class="panel-label">原始 CT 影像</div>
                <div class="image-frame" v-loading="uploading" element-loading-text="上传中...">
                  <el-image
                    v-if="url1"
                    :src="url1"
                    :preview-src-list="[url1]"
                    fit="contain"
                    class="ct-image"
                  />
                  <div v-else class="placeholder">
                    <el-icon :size="64"><PictureFilled /></el-icon>
                    <p>等待上传影像</p>
                  </div>
                </div>
              </div>

              <!-- 诊断结果 -->
              <div class="image-panel">
                <div class="panel-label result-label">AI 诊断结果</div>
                <div class="image-frame" v-loading="diagnosing" element-loading-text="AI 分析中...">
                  <el-image
                    v-if="url2"
                    :src="url2"
                    :preview-src-list="[url2]"
                    fit="contain"
                    class="ct-image"
                  />
                  <div v-else class="placeholder">
                    <el-icon :size="64"><MagicStick /></el-icon>
                    <p>{{ diagnosing ? '正在分析...' : '等待诊断结果' }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- 图像操作工具栏 -->
            <div class="image-toolbar" v-if="url1 || url2">
              <el-button-group>
                <el-tooltip content="重新上传" placement="top">
                  <el-button :icon="Refresh" @click="triggerReupload" />
                </el-tooltip>
                <el-tooltip content="对比查看" placement="top">
                  <el-button :icon="Switch" :disabled="!url2" @click="toggleCompare" />
                </el-tooltip>
                <el-tooltip content="全屏预览" placement="top">
                  <el-button :icon="FullScreen" :disabled="!url1" @click="fullscreenPreview" />
                </el-tooltip>
              </el-button-group>
            </div>
          </el-card>

          <!-- AI病情分析卡片 -->
          <el-card class="ai-analysis-card" shadow="hover" v-if="url2">
            <template #header>
              <div class="card-header">
                <el-icon><Reading /></el-icon>
                <span>AI 病情分析</span>
                <el-tag size="small" type="info" v-if="!aiAnalysisResult.conclusion">待分析</el-tag>
                <el-tag size="small" type="success" v-else>已完成</el-tag>
              </div>
            </template>

            <div class="ai-analysis-content">
              <!-- 分析中状态 -->
              <div v-if="isAnalyzing" class="analyzing-state">
                <el-icon class="is-loading" :size="40"><Loading /></el-icon>
                <p>AI正在分析病情...</p>
              </div>

              <!-- 未分析状态 -->
              <div v-else-if="!aiAnalysisResult.conclusion" class="empty-analysis">
                <el-empty description="暂无AI病情分析" :image-size="100">
                  <el-button type="primary" @click="startAiAnalysis" :loading="isAnalyzing">
                    开始分析
                  </el-button>
                </el-empty>
              </div>

              <!-- 分析结果 -->
              <div v-else class="analysis-result">
                <div class="analysis-section">
                  <h4 class="section-title">
                    <el-icon><Document /></el-icon>
                    诊断结论
                  </h4>
                  <div class="section-content">
                    <el-alert 
                      :type="aiAnalysisResult.riskLevel === '高' ? 'error' : aiAnalysisResult.riskLevel === '中' ? 'warning' : 'success'"
                      :closable="false"
                      show-icon
                    >
                      <template #title>
                        <span style="font-weight: 600;">{{ aiAnalysisResult.conclusion }}</span>
                      </template>
                    </el-alert>
                  </div>
                </div>

                <div class="analysis-section">
                  <h4 class="section-title">
                    <el-icon><Warning /></el-icon>
                    风险等级
                  </h4>
                  <div class="section-content">
                    <el-tag 
                      :type="aiAnalysisResult.riskLevel === '高' ? 'danger' : aiAnalysisResult.riskLevel === '中' ? 'warning' : 'success'"
                      size="large"
                      effect="dark"
                    >
                      {{ aiAnalysisResult.riskLevel }}风险
                    </el-tag>
                    <span class="risk-score">置信度: {{ aiAnalysisResult.confidence }}%</span>
                  </div>
                </div>

                <div class="analysis-section">
                  <h4 class="section-title">
                    <el-icon><Memo /></el-icon>
                    详细描述
                  </h4>
                  <div class="section-content description-text">
                    {{ aiAnalysisResult.description }}
                  </div>
                </div>

                <div class="analysis-section">
                  <h4 class="section-title">
                    <el-icon><Guide /></el-icon>
                    建议措施
                  </h4>
                  <div class="section-content">
                    <ul class="suggestion-list">
                      <li v-for="(item, index) in aiAnalysisResult.suggestions" :key="index">
                        {{ item }}
                      </li>
                    </ul>
                  </div>
                </div>

                <div class="analysis-footer">
                  <el-button size="small" @click="regenerateAnalysis">
                    <el-icon><Refresh /></el-icon>
                    重新分析
                  </el-button>
                  <span class="analysis-time">分析时间: {{ aiAnalysisResult.analysisTime }}</span>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 医生诊断记录卡片 -->
          <el-card class="doctor-record-card" shadow="hover" v-if="url2">
            <template #header>
              <div class="card-header">
                <el-icon><EditPen /></el-icon>
                <span>医生诊断记录</span>
                <el-tag size="small" :type="doctorRecord.isSaved ? 'success' : 'info'">
                  {{ doctorRecord.isSaved ? '已保存' : '待填写' }}
                </el-tag>
              </div>
            </template>

            <el-form 
              :model="doctorRecord" 
              label-position="top" 
              class="doctor-record-form"
            >
              <el-form-item label="诊断结论">
                <el-select 
                  v-model="doctorRecord.conclusion" 
                  placeholder="请选择诊断结论"
                  style="width: 100%"
                >
                  <el-option label="良性病变" value="良性病变" />
                  <el-option label="恶性肿瘤" value="恶性肿瘤" />
                  <el-option label="疑似恶性" value="疑似恶性" />
                  <el-option label="待进一步检查" value="待进一步检查" />
                  <el-option label="正常" value="正常" />
                </el-select>
              </el-form-item>

              <el-form-item label="诊断描述">
                <el-input
                  v-model="doctorRecord.diagnosis"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入详细的诊断描述，包括病变位置、大小、形态特征等..."
                  maxlength="1000"
                  show-word-limit
                />
              </el-form-item>

              <el-form-item label="治疗建议">
                <el-input
                  v-model="doctorRecord.suggestion"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入治疗建议和后续处理方案..."
                  maxlength="500"
                  show-word-limit
                />
              </el-form-item>

              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="saveDoctorRecordHandler"
                  :loading="savingRecord"
                  :disabled="!currentRecordId"
                >
                  <el-icon><Check /></el-icon>
                  保存诊断记录
                </el-button>
                <el-button @click="clearDoctorRecord">
                  <el-icon><RefreshLeft /></el-icon>
                  清空
                </el-button>
              </el-form-item>
            </el-form>

            <div class="record-tips">
              <el-alert type="info" :closable="false" show-icon>
                <template #title>
                  <span style="font-size: 12px;">诊断记录将与当前患者信息绑定保存</span>
                </template>
              </el-alert>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧：特征分析 -->
        <el-col :xl="6" :lg="6" :md="24" :sm="24">
          <el-card class="analysis-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><DataAnalysis /></el-icon>
                <span>特征分析</span>
              </div>
            </template>

            <el-tabs v-model="activeTab" class="analysis-tabs">
              <!-- 特征列表 -->
              <el-tab-pane label="特征数据" name="features">
                <div class="feature-list" v-if="featureList.length">
                  <div 
                    v-for="(item, index) in featureList" 
                    :key="index"
                    class="feature-item"
                  >
                    <span class="feature-name">{{ item.name }}</span>
                    <span class="feature-value">{{ item.value }}</span>
                  </div>
                </div>
                <el-empty v-else description="暂无特征数据" :image-size="80" />
              </el-tab-pane>

              <!-- 面积图表 -->
              <el-tab-pane label="面积对比" name="area">
                <div ref="areaChartRef" class="chart-container"></div>
              </el-tab-pane>

              <!-- 周长图表 -->
              <el-tab-pane label="周长对比" name="perimeter">
                <div ref="perimeterChartRef" class="chart-container"></div>
              </el-tab-pane>
            </el-tabs>

            <!-- 快速统计 -->
            <div class="quick-stats" v-if="areaData || perimeterData">
              <div class="stat-item">
                <div class="stat-label">面积</div>
                <div class="stat-value">{{ areaData.toFixed(2) }} px²</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">周长</div>
                <div class="stat-value">{{ perimeterData.toFixed(2) }} px</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 诊断进度对话框 -->
    <el-dialog 
      v-model="isProcessing" 
      title="AI 诊断分析中" 
      :close-on-click-modal="false"
      :show-close="false"
      width="420px"
      center
      class="progress-dialog"
    >
      <div class="progress-content">
        <el-progress 
          type="dashboard" 
          :percentage="percentage" 
          :color="progressColors"
          :stroke-width="12"
          :width="160"
        >
          <template #default="{ percentage }">
            <div class="progress-inner">
              <span class="progress-value">{{ percentage }}%</span>
              <span class="progress-label">完成度</span>
            </div>
          </template>
        </el-progress>
        
        <div class="progress-status">
          <el-icon class="is-loading" v-if="percentage < 100"><Loading /></el-icon>
          <el-icon color="#67c23a" v-else><CircleCheck /></el-icon>
          <span>{{ progressStatus }}</span>
        </div>

        <div class="progress-steps">
          <div 
            v-for="(step, index) in progressSteps" 
            :key="index"
            class="step-item"
            :class="{ active: currentProgressStep >= index, done: currentProgressStep > index }"
          >
            <el-icon v-if="currentProgressStep > index"><Check /></el-icon>
            <span v-else>{{ index + 1 }}</span>
            <p>{{ step }}</p>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 隐藏的重新上传input -->
    <input
      ref="reuploadInput"
      type="file"
      accept=".dcm"
      style="display: none"
      @change="handleReupload"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  User, Search, Operation, Upload, UploadFilled, VideoPlay,
  Picture, PictureFilled, MagicStick, DataAnalysis, Document,
  Close, InfoFilled, Refresh, Switch, FullScreen, Loading,
  CircleCheck, Check, Cpu, Reading, Warning, Memo, Guide,
  EditPen, RefreshLeft
} from '@element-plus/icons-vue'

import { getPatientInfo } from '@/services/patient'
import { startTask, uploadDcm } from '@/services/task'
import { saveDoctorRecord } from '@/services/diagnosis'
import { useAiPrediction } from '@/composables/useAiPrediction'

const route = useRoute()
const { 
  percentage, 
  progressStatus, 
  isProcessing, 
  resultData, 
  initSocket 
} = useAiPrediction()

// 部位映射
const partMap = {
  rectum: '直肠',
  lung: '肺部',
  liver: '肝脏',
  brain: '脑部',
  breast: '乳腺',
  stomach: '胃部'
}

// 当前诊断部位
const currentPart = computed(() => route.params.part || 'rectum')
const partName = computed(() => partMap[currentPart.value] || '未知部位')

// Refs
const uploadRef = ref(null)
const reuploadInput = ref(null)
const areaChartRef = ref(null)
const perimeterChartRef = ref(null)

// State
const loading = ref(false)
const uploading = ref(false)
const diagnosing = ref(false)
const searchId = ref('')
const currentFile = ref(null)
const url1 = ref('')
const url2 = ref('')
const featureList = ref([])
const areaData = ref(0)
const perimeterData = ref(0)
const activeTab = ref('features')

// AI病情分析状态
const isAnalyzing = ref(false)
const aiAnalysisResult = ref({
  conclusion: '',
  riskLevel: '',
  confidence: 0,
  description: '',
  suggestions: [],
  analysisTime: ''
})

// 医生诊断记录状态
const currentRecordId = ref(null)
const savingRecord = ref(false)
const doctorRecord = ref({
  conclusion: '',
  diagnosis: '',
  suggestion: '',
  isSaved: false
})

// Charts
let areaChart = null
let perimeterChart = null

// 患者信息
const patient = ref({
  id: '',
  name: '',
  gender: '',
  age: '',
  phone: '',
  part: ''
})

// 判断是否有患者数据
const hasPatientData = computed(() => {
  return patient.value.name || patient.value.id
})

// 流程步骤
const currentStep = computed(() => {
  if (url2.value) return 3
  if (url1.value) return 1
  return 0
})

// 进度步骤
const progressSteps = ['图像预处理', '模型推理', '特征提取', '结果生成']
const currentProgressStep = computed(() => {
  if (percentage.value >= 90) return 4
  if (percentage.value >= 70) return 3
  if (percentage.value >= 50) return 2
  if (percentage.value >= 30) return 1
  return 0
})

const progressColors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#67c23a', percentage: 100 },
]

// 监听 AI 预测结果
watch(resultData, (newData) => {
  if (newData.url2) {
    url2.value = newData.url2
    featureList.value = newData.featureList || []
    areaData.value = newData.area || 0
    perimeterData.value = newData.perimeter || 0
    diagnosing.value = false
    updateCharts()
  }
}, { deep: true })

// 监听 Tab 切换更新图表
watch(activeTab, (newTab) => {
  if (newTab === 'area' || newTab === 'perimeter') {
    nextTick(() => updateCharts())
  }
})

// Methods
const fetchPatientData = async (id) => {
  // 空检索提示
  if (!id || id.trim() === '') {
    ElMessage.warning('请输入患者ID')
    return
  }
  
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
        part: d['部位'] || partName.value
      }
      ElMessage.success('患者信息获取成功')
    } else {
      // 未找到提示
      patient.value = {
        id: '',
        name: '',
        gender: '',
        age: '',
        phone: '',
        part: ''
      }
      ElMessage.warning(`未找到ID为 "${id}" 的患者信息，请检查后重试`)
    }
  } catch (e) {
    console.error(e)
    // 清空患者信息
    patient.value = {
      id: '',
      name: '',
      gender: '',
      age: '',
      phone: '',
      part: ''
    }
    ElMessage.error('获取患者信息失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}

const handleFileSelect = async (file) => {
  currentFile.value = file.raw
  await uploadFile(file.raw)
}

const uploadFile = async (file) => {
  uploading.value = true
  try {
    const res = await uploadDcm(file)
    if (res.status === 1) {
      url1.value = res.image_url
      // 清空之前的结果
      url2.value = ''
      featureList.value = []
      areaData.value = 0
      perimeterData.value = 0
      ElMessage.success('影像上传成功')
    } else {
      ElMessage.error(res.error || '上传失败')
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('上传失败: ' + (e.message || '未知错误'))
  } finally {
    uploading.value = false
  }
}

const clearFile = () => {
  currentFile.value = null
  url1.value = ''
  url2.value = ''
  featureList.value = []
  areaData.value = 0
  perimeterData.value = 0
}

const triggerReupload = () => {
  reuploadInput.value?.click()
}

const handleReupload = (e) => {
  const file = e.target.files[0]
  if (file) {
    currentFile.value = file
    uploadFile(file)
  }
  e.target.value = ''
}

const handleStartDiagnosis = async () => {
  if (!url1.value) {
    return ElMessage.warning('请先上传 CT 影像')
  }
  
  diagnosing.value = true
  isProcessing.value = true
  percentage.value = 0
  progressStatus.value = '正在进行AI分析...'
  
  try {
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
      
      // 保存诊断记录ID，用于后续保存医生记录
      if (res.record_id) {
        currentRecordId.value = res.record_id
        // 重置医生记录表单
        doctorRecord.value = {
          conclusion: '',
          diagnosis: '',
          suggestion: '',
          isSaved: false
        }
      }
      
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
      updateCharts()
    } else {
      ElMessage.error(res.error || '分析失败')
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('诊断失败: ' + (e.message || '未知错误'))
  } finally {
    diagnosing.value = false
    setTimeout(() => {
      isProcessing.value = false
    }, 1000)
  }
}

const toggleCompare = () => {
  // 可以实现图像对比功能
  ElMessage.info('对比功能开发中')
}

const fullscreenPreview = () => {
  // 触发图片预览
  const imgEl = document.querySelector('.ct-image .el-image__inner')
  imgEl?.click()
}

// AI病情分析相关方法
const startAiAnalysis = async () => {
  if (!url2.value) {
    ElMessage.warning('请先完成AI诊断')
    return
  }
  
  isAnalyzing.value = true
  
  try {
    // 模拟AI分析过程，实际应调用后端API
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // TODO: 替换为实际的API调用
    // const res = await analyzeCondition({ imageUrl: url2.value, features: featureList.value })
    
    // 模拟返回结果
    const mockResult = {
      conclusion: '检测到直肠肿瘤病变，建议进一步检查',
      riskLevel: '中',
      confidence: 87.5,
      description: '根据影像分析，在直肠区域检测到异常组织增生。肿瘤边界相对清晰，大小约为' + areaData.value.toFixed(2) + 'px²。组织密度异常，与周围正常组织存在明显差异。建议结合病理检查进行综合评估。',
      suggestions: [
        '建议尽快进行肠镜检查以确认病变性质',
        '建议进行病理活检以明确肿瘤类型',
        '建议完善CT增强扫描评估淋巴结情况',
        '建议咨询肛肠外科专家制定治疗方案',
        '定期复查监测病情变化'
      ],
      analysisTime: new Date().toLocaleString('zh-CN', { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit',
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
      })
    }
    
    aiAnalysisResult.value = mockResult
    ElMessage.success('AI病情分析完成')
  } catch (e) {
    console.error(e)
    ElMessage.error('AI分析失败: ' + (e.message || '未知错误'))
  } finally {
    isAnalyzing.value = false
  }
}

const regenerateAnalysis = () => {
  aiAnalysisResult.value = {
    conclusion: '',
    riskLevel: '',
    confidence: 0,
    description: '',
    suggestions: [],
    analysisTime: ''
  }
  startAiAnalysis()
}

// 医生诊断记录相关方法
const saveDoctorRecordHandler = async () => {
  if (!currentRecordId.value) {
    ElMessage.warning('诊断记录不存在，请先完成AI诊断')
    return
  }
  
  if (!doctorRecord.value.conclusion && !doctorRecord.value.diagnosis && !doctorRecord.value.suggestion) {
    ElMessage.warning('请至少填写一项诊断信息')
    return
  }
  
  savingRecord.value = true
  
  try {
    const res = await saveDoctorRecord(currentRecordId.value, {
      diagnosis_conclusion: doctorRecord.value.conclusion,
      doctor_diagnosis: doctorRecord.value.diagnosis,
      doctor_suggestion: doctorRecord.value.suggestion
    })
    
    if (res.status === 1) {
      doctorRecord.value.isSaved = true
      ElMessage.success('诊断记录保存成功')
    } else {
      ElMessage.error(res.error || '保存失败')
    }
  } catch (e) {
    console.error('保存诊断记录失败:', e)
    ElMessage.error('保存失败: ' + (e.message || '网络错误'))
  } finally {
    savingRecord.value = false
  }
}

const clearDoctorRecord = () => {
  doctorRecord.value = {
    conclusion: '',
    diagnosis: '',
    suggestion: '',
    isSaved: false
  }
}

const updateCharts = () => {
  nextTick(() => {
    // 面积图表
    if (areaChartRef.value && activeTab.value === 'area') {
      if (!areaChart) {
        areaChart = echarts.init(areaChartRef.value)
      }
      areaChart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
        xAxis: { 
          type: 'category', 
          data: ['样本1', '样本2', '样本3', '样本4', '样本5', '样本6', '样本7', '当前'],
          axisLabel: { fontSize: 10 }
        },
        yAxis: { type: 'value', name: '面积(px²)', nameTextStyle: { fontSize: 10 } },
        series: [{
          name: '面积',
          type: 'line',
          smooth: true,
          data: [1300, 1290, 1272, 1123.5, 1123, 1092, 1086, areaData.value],
          itemStyle: { color: '#409eff' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0)' }
            ])
          }
        }]
      })
    }

    // 周长图表
    if (perimeterChartRef.value && activeTab.value === 'perimeter') {
      if (!perimeterChart) {
        perimeterChart = echarts.init(perimeterChartRef.value)
      }
      perimeterChart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
        xAxis: { 
          type: 'category', 
          data: ['样本1', '样本2', '样本3', '样本4', '样本5', '样本6', '样本7', '当前'],
          axisLabel: { fontSize: 10 }
        },
        yAxis: { type: 'value', name: '周长(px)', nameTextStyle: { fontSize: 10 } },
        series: [{
          name: '周长',
          type: 'bar',
          data: [150, 145, 142, 138, 135, 130, 128, perimeterData.value],
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#67c23a' },
              { offset: 1, color: '#95d475' }
            ]),
            borderRadius: [4, 4, 0, 0]
          }
        }]
      })
    }
  })
}

const handleResize = () => {
  areaChart?.resize()
  perimeterChart?.resize()
}

// 监听全局上传事件
const handleGlobalUpload = (event) => {
  if (event.detail) {
    currentFile.value = event.detail
    uploadFile(event.detail)
  }
}

onMounted(() => {
  // 检查部位是否支持
  if (!partMap[currentPart.value]) {
    ElMessage.warning(`不支持的诊断部位: ${currentPart.value}`)
  }
  
  initSocket()
  
  // 如果 URL 中有患者 ID，则自动查询
  const id = route.query.id
  if (id) {
    searchId.value = id
    fetchPatientData(id)
  }
  
  window.addEventListener('resize', handleResize)
  window.addEventListener('upload-ct-file', handleGlobalUpload)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('upload-ct-file', handleGlobalUpload)
  areaChart?.dispose()
  perimeterChart?.dispose()
})
</script>

<style scoped>
.diagnosis-container {
  padding: 20px;
  min-height: calc(100vh - 70px);
}

/* 顶部区域 */
.top-section {
  margin-bottom: 20px;
}

.breadcrumb {
  background: #fff;
  padding: 12px 20px;
  border-radius: 8px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.breadcrumb :deep(.el-breadcrumb__inner) {
  color: #606266;
  font-weight: 500;
}

.breadcrumb :deep(.el-breadcrumb__inner:hover) {
  color: #409eff;
}

/* 流程步骤 */
.workflow-steps {
  background: #fff;
  padding: 20px 40px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

/* 左侧面板 */
.left-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.panel-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

.header-extra {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.search-box {
  margin-bottom: 16px;
}

.empty-patient-info {
  padding: 20px 0;
}

.empty-patient-info :deep(.el-empty__description) {
  color: #909399;
  font-size: 13px;
}

.patient-desc :deep(.el-descriptions__label) {
  width: 80px;
  font-weight: 500;
}

/* 操作面板 */
.action-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  padding: 20px;
  border-radius: 8px;
  background: #fafafa;
  transition: all 0.3s;
}

.upload-area :deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background: #f0f7ff;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.upload-icon {
  color: #909399;
}

.upload-text p {
  margin: 0;
  color: #606266;
  font-size: 13px;
}

.upload-text em {
  color: #409eff;
  font-style: normal;
}

.upload-hint {
  color: #909399 !important;
  font-size: 12px !important;
}

.current-file {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f0f9eb;
  border-radius: 6px;
  color: #67c23a;
}

.filename {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
}

.start-btn {
  width: 100%;
  height: 48px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 8px;
}

.status-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #909399;
  font-size: 12px;
  margin: 0;
}

/* 影像工作区 */
.workspace-card {
  border-radius: 12px;
  min-height: 500px;
}

.image-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.image-panel {
  position: relative;
}

.panel-label {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  padding: 4px 16px;
  border-radius: 20px;
  font-size: 12px;
  backdrop-filter: blur(4px);
}

.panel-label.result-label {
  background: rgba(64, 158, 255, 0.8);
}

.image-frame {
  aspect-ratio: 1;
  background: #1a1a1a;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ct-image {
  width: 100%;
  height: 100%;
}

.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #606266;
}

.placeholder p {
  margin: 0;
  font-size: 13px;
}

.image-toolbar {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

/* AI病情分析卡片 */
.ai-analysis-card {
  border-radius: 12px;
  margin-top: 16px;
}

.ai-analysis-card .card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.ai-analysis-content {
  min-height: 200px;
}

.analyzing-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 16px;
}

.analyzing-state .el-icon {
  color: #409eff;
}

.analyzing-state p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.empty-analysis {
  padding: 20px;
}

.analysis-result {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.analysis-section {
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.section-content {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

.risk-score {
  margin-left: 12px;
  font-size: 13px;
  color: #909399;
}

.description-text {
  text-align: justify;
}

.suggestion-list {
  margin: 0;
  padding-left: 20px;
}

.suggestion-list li {
  margin-bottom: 8px;
  line-height: 1.6;
}

.suggestion-list li:last-child {
  margin-bottom: 0;
}

.analysis-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
  margin-top: 4px;
}

.analysis-time {
  font-size: 12px;
  color: #909399;
}

/* 医生诊断记录卡片 */
.doctor-record-card {
  border-radius: 12px;
  margin-top: 16px;
}

.doctor-record-form {
  padding: 8px 0;
}

.doctor-record-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #303133;
}

.doctor-record-form :deep(.el-textarea__inner) {
  font-size: 13px;
  line-height: 1.6;
}

.doctor-record-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.doctor-record-form :deep(.el-form-item:last-child) {
  margin-bottom: 8px;
}

.record-tips {
  margin-top: 8px;
}

.record-tips :deep(.el-alert) {
  padding: 8px 12px;
}

/* 特征分析 */
.analysis-card {
  border-radius: 12px;
  min-height: 500px;
}

.analysis-tabs :deep(.el-tabs__header) {
  margin-bottom: 16px;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 320px;
  overflow-y: auto;
}

.feature-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 6px;
  transition: all 0.2s;
}

.feature-item:hover {
  background: #f0f7ff;
  transform: translateX(2px);
}

.feature-name {
  color: #606266;
  font-size: 13px;
}

.feature-value {
  font-family: 'Monaco', monospace;
  font-weight: 600;
  color: #409eff;
  font-size: 13px;
}

.chart-container {
  height: 280px;
}

.quick-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.stat-item {
  text-align: center;
  padding: 12px;
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
  border-radius: 8px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #67c23a;
}

/* 进度对话框 */
.progress-dialog :deep(.el-dialog) {
  border-radius: 16px;
}

.progress-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.progress-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.progress-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.progress-label {
  font-size: 12px;
  color: #909399;
}

.progress-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 20px;
  font-size: 15px;
  color: #606266;
}

.progress-steps {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.step-item span,
.step-item .el-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #f0f0f0;
  color: #909399;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition: all 0.3s;
}

.step-item.active span,
.step-item.active .el-icon {
  background: #409eff;
  color: #fff;
}

.step-item.done .el-icon {
  background: #67c23a;
  color: #fff;
}

.step-item p {
  margin: 0;
  font-size: 11px;
  color: #909399;
}

.step-item.active p {
  color: #409eff;
  font-weight: 500;
}

/* 响应式 */
@media (max-width: 1200px) {
  .image-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .diagnosis-container {
    padding: 12px;
  }
  
  .workflow-steps {
    padding: 12px 20px;
  }
  
  .quick-stats {
    grid-template-columns: 1fr;
  }
}
</style>
