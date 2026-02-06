<template>
  <div class="settings-container">
    <el-card class="settings-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon :size="24" color="#409eff"><Setting /></el-icon>
            <span class="title">系统设置</span>
          </div>
          <div class="header-right">
            <el-button @click="handleResetAll" :loading="resetting" v-if="activeTab !== 'model'">
              <el-icon><RefreshRight /></el-icon>
              重置所有
            </el-button>
            <el-button type="primary" @click="handleSaveAll" :loading="saving" v-if="activeTab !== 'model'">
              <el-icon><Check /></el-icon>
              保存设置
            </el-button>
          </div>
        </div>
      </template>

      <el-tabs v-model="activeTab" type="border-card" v-loading="loading">
        <!-- 数据分析参数 -->
        <el-tab-pane label="数据分析参数" name="analysis">
          <div class="tab-header">
            <el-icon><DataAnalysis /></el-icon>
            <span>调整肿瘤分析的阈值和参数</span>
          </div>
          
          <el-form :model="analysisForm" label-width="180px" class="settings-form">
            <el-form-item label="面积阈值 (像素)">
              <el-input-number 
                v-model="analysisForm.analysis_threshold" 
                :min="100" 
                :max="10000" 
                :step="100"
              />
              <span class="form-tip">超过此值判定为"需关注"</span>
            </el-form-item>
            
            <el-form-item label="圆度阈值">
              <el-slider 
                v-model="analysisForm.analysis_circularity_threshold" 
                :min="0" 
                :max="1" 
                :step="0.05"
                show-input
              />
              <span class="form-tip">低于此值可能为异常形态 (0-1)</span>
            </el-form-item>
            
            <el-form-item label="最小有效面积 (像素)">
              <el-input-number 
                v-model="analysisForm.analysis_min_area" 
                :min="10" 
                :max="1000" 
                :step="10"
              />
              <span class="form-tip">小于此值的区域将被忽略</span>
            </el-form-item>
            
            <el-form-item label="模型置信度阈值">
              <el-slider 
                v-model="analysisForm.analysis_confidence_threshold" 
                :min="0" 
                :max="1" 
                :step="0.05"
                show-input
              />
              <span class="form-tip">低于此值的预测结果将被过滤</span>
            </el-form-item>
          </el-form>
          
          <div class="section-actions">
            <el-button @click="handleReset('analysis')">重置此分类</el-button>
          </div>
        </el-tab-pane>

        <!-- 报告内容设置 -->
        <el-tab-pane label="报告内容设置" name="report">
          <div class="tab-header">
            <el-icon><Document /></el-icon>
            <span>配置诊断报告显示的内容</span>
          </div>
          
          <el-form :model="reportForm" label-width="180px" class="settings-form">
            <el-divider content-position="left">显示项目</el-divider>
            
            <el-form-item label="显示面积">
              <el-switch v-model="reportForm.report_show_area" />
            </el-form-item>
            
            <el-form-item label="显示周长">
              <el-switch v-model="reportForm.report_show_perimeter" />
            </el-form-item>
            
            <el-form-item label="显示圆度">
              <el-switch v-model="reportForm.report_show_circularity" />
            </el-form-item>
            
            <el-form-item label="显示离心率">
              <el-switch v-model="reportForm.report_show_eccentricity" />
            </el-form-item>
            
            <el-form-item label="显示灰度信息">
              <el-switch v-model="reportForm.report_show_intensity" />
            </el-form-item>
            
            <el-form-item label="显示灰度直方图">
              <el-switch v-model="reportForm.report_show_histogram" />
            </el-form-item>
            
            <el-divider content-position="left">报告信息</el-divider>
            
            <el-form-item label="医院/机构名称">
              <el-input 
                v-model="reportForm.report_hospital_name" 
                placeholder="请输入医院名称"
                style="width: 300px;"
              />
            </el-form-item>
            
            <el-form-item label="报告页脚文字">
              <el-input 
                v-model="reportForm.report_footer_text" 
                type="textarea"
                :rows="2"
                placeholder="请输入报告底部的提示文字"
                style="width: 400px;"
              />
            </el-form-item>
          </el-form>
          
          <div class="section-actions">
            <el-button @click="handleReset('report')">重置此分类</el-button>
          </div>
        </el-tab-pane>

        <!-- 模型管理 -->
        <el-tab-pane label="模型管理" name="model">
          <div class="tab-header">
            <el-icon><Cpu /></el-icon>
            <span>管理诊断分析使用的AI模型</span>
          </div>
          
          <!-- 当前模型状态 -->
          <el-card class="model-status-card" shadow="never">
            <template #header>
              <div class="model-card-header">
                <span>当前模型状态</span>
                <el-button type="primary" size="small" @click="fetchCurrentModel" :loading="modelLoading">
                  <el-icon><Refresh /></el-icon>
                  刷新状态
                </el-button>
              </div>
            </template>
            
            <el-descriptions :column="2" border>
              <el-descriptions-item label="当前模型">
                <el-tag :type="currentModel.model_loaded ? 'success' : 'warning'">
                  {{ currentModel.current_model || '未设置' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="运行状态">
                <el-tag :type="currentModel.model_loaded ? 'success' : 'danger'">
                  {{ currentModel.model_loaded ? '已加载' : '未加载' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="运行设备">
                <el-tag type="info">{{ currentModel.device || '-' }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="文件大小">
                {{ currentModel.model_info?.size_mb || '-' }} MB
              </el-descriptions-item>
              <el-descriptions-item label="修改时间" :span="2">
                {{ currentModel.model_info?.modified_at || '-' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
          
          <!-- 模型列表 -->
          <el-card class="model-list-card" shadow="never" style="margin-top: 20px;">
            <template #header>
              <div class="model-card-header">
                <span>可用模型列表</span>
                <el-upload
                  ref="uploadRef"
                  :show-file-list="false"
                  :before-upload="beforeModelUpload"
                  :http-request="handleModelUpload"
                  accept=".pth"
                >
                  <el-button type="success" size="small">
                    <el-icon><Upload /></el-icon>
                    上传模型
                  </el-button>
                </el-upload>
              </div>
            </template>
            
            <el-table :data="modelList" v-loading="modelLoading" empty-text="暂无可用模型">
              <el-table-column prop="name" label="模型名称" min-width="150">
                <template #default="{ row }">
                  <div class="model-name-cell">
                    <el-icon v-if="row.name === currentModel.current_model" color="#67c23a"><Check /></el-icon>
                    <span>{{ row.name }}</span>
                    <el-tag v-if="row.is_legacy" size="small" type="info">旧版</el-tag>
                    <el-tag v-if="row.name === currentModel.current_model" size="small" type="success">使用中</el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="size_mb" label="文件大小" width="120">
                <template #default="{ row }">
                  {{ row.size_mb }} MB
                </template>
              </el-table-column>
              <el-table-column prop="modified_at" label="修改时间" width="180" />
              <el-table-column label="操作" width="200" fixed="right">
                <template #default="{ row }">
                  <el-button 
                    type="primary" 
                    size="small" 
                    :disabled="row.name === currentModel.current_model"
                    :loading="switchingModel === row.name"
                    @click="handleSwitchModel(row)"
                  >
                    {{ row.name === currentModel.current_model ? '当前使用' : '切换使用' }}
                  </el-button>
                  <el-button 
                    type="danger" 
                    size="small" 
                    :disabled="row.name === 'default' || row.name === currentModel.current_model"
                    @click="handleDeleteModel(row)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <div class="model-tips">
              <el-alert type="info" :closable="false" show-icon>
                <template #title>
                  <span>提示：上传的模型文件必须与系统的 UNet 网络结构兼容（输入通道：1，输出通道：1）。切换模型后将立即生效。</span>
                </template>
              </el-alert>
            </div>
          </el-card>
        </el-tab-pane>

        <!-- 系统设置 -->
        <el-tab-pane label="系统设置" name="system">
          <div class="tab-header">
            <el-icon><Tools /></el-icon>
            <span>配置系统运行参数</span>
          </div>
          
          <el-form :model="systemForm" label-width="180px" class="settings-form">
            <el-form-item label="最大上传文件大小">
              <el-input-number 
                v-model="systemForm.system_max_upload_size" 
                :min="1" 
                :max="200" 
                :step="10"
              />
              <span class="form-tip">单位：MB</span>
            </el-form-item>
            
            <el-form-item label="登录有效期">
              <el-input-number 
                v-model="systemForm.system_session_timeout" 
                :min="1" 
                :max="168" 
                :step="1"
              />
              <span class="form-tip">单位：小时</span>
            </el-form-item>
            
            <el-form-item label="自动备份">
              <el-switch v-model="systemForm.system_auto_backup" />
              <span class="form-tip">启用后将定期备份诊断数据</span>
            </el-form-item>
          </el-form>
          
          <div class="section-actions">
            <el-button @click="handleReset('system')">重置此分类</el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 设置预览 -->
    <el-card class="preview-card" shadow="never" v-if="activeTab !== 'model'">
      <template #header>
        <div class="card-header">
          <el-icon><View /></el-icon>
          <span>当前配置预览</span>
        </div>
      </template>
      
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="面积阈值">{{ analysisForm.analysis_threshold }} 像素</el-descriptions-item>
        <el-descriptions-item label="圆度阈值">{{ analysisForm.analysis_circularity_threshold }}</el-descriptions-item>
        <el-descriptions-item label="最小面积">{{ analysisForm.analysis_min_area }} 像素</el-descriptions-item>
        <el-descriptions-item label="置信度阈值">{{ analysisForm.analysis_confidence_threshold }}</el-descriptions-item>
        <el-descriptions-item label="医院名称">{{ reportForm.report_hospital_name }}</el-descriptions-item>
        <el-descriptions-item label="上传限制">{{ systemForm.system_max_upload_size }} MB</el-descriptions-item>
      </el-descriptions>
      
      <div class="last-update" v-if="lastUpdate">
        <el-icon><Clock /></el-icon>
        最后更新: {{ lastUpdate }}
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Setting, 
  RefreshRight, 
  Check, 
  DataAnalysis, 
  Document, 
  Tools,
  View,
  Clock,
  Cpu,
  Refresh,
  Upload
} from '@element-plus/icons-vue'
import { 
  getSettings, 
  updateSettings, 
  resetSettings,
  getModels,
  getCurrentModel,
  switchModel,
  uploadModel,
  deleteModel
} from '@/services/settings'

const loading = ref(false)
const saving = ref(false)
const resetting = ref(false)
const activeTab = ref('analysis')
const lastUpdate = ref('')

// 模型管理相关状态
const modelLoading = ref(false)
const modelList = ref([])
const currentModel = reactive({
  current_model: '',
  model_loaded: false,
  model_info: null,
  device: ''
})
const switchingModel = ref('')
const uploadRef = ref(null)

// 数据分析参数表单
const analysisForm = reactive({
  analysis_threshold: '',
  analysis_circularity_threshold: '',
  analysis_min_area: '',
  analysis_confidence_threshold: ''
})

// 报告内容设置表单
const reportForm = reactive({
  report_show_area: true,
  report_show_perimeter: true,
  report_show_circularity: true,
  report_show_eccentricity: true,
  report_show_intensity: true,
  report_show_histogram: true,
  report_hospital_name: '',
  report_footer_text: ''
})

// 系统设置表单
const systemForm = reactive({
  system_max_upload_size: '',
  system_session_timeout: '',
  system_auto_backup: false
})

// 加载设置
const fetchSettings = async () => {
  loading.value = true
  try {
    const res = await getSettings()
    if (res.data.status === 1) {
      const data = res.data.data
      
      // 填充分析参数
      data.analysis?.forEach(item => {
        if (item.key in analysisForm) {
          const value = parseFloat(item.value)
          analysisForm[item.key] = isNaN(value) ? item.value : value
        }
        if (item.updated_at) {
          lastUpdate.value = item.updated_at
        }
      })
      
      // 填充报告设置
      data.report?.forEach(item => {
        if (item.key in reportForm) {
          // 布尔值处理
          if (item.value === 'true' || item.value === 'false') {
            reportForm[item.key] = item.value === 'true'
          } else {
            reportForm[item.key] = item.value
          }
        }
        if (item.updated_at && item.updated_at > lastUpdate.value) {
          lastUpdate.value = item.updated_at
        }
      })
      
      // 填充系统设置
      data.system?.forEach(item => {
        if (item.key in systemForm) {
          if (item.value === 'true' || item.value === 'false') {
            systemForm[item.key] = item.value === 'true'
          } else {
            const value = parseFloat(item.value)
            systemForm[item.key] = isNaN(value) ? item.value : value
          }
        }
        if (item.updated_at && item.updated_at > lastUpdate.value) {
          lastUpdate.value = item.updated_at
        }
      })
    }
  } catch (error) {
    console.error('获取设置失败:', error)
    ElMessage.error('获取设置失败')
  } finally {
    loading.value = false
  }
}

// 保存所有设置
const handleSaveAll = async () => {
  saving.value = true
  try {
    // 合并所有设置
    const allSettings = {
      ...analysisForm,
      ...Object.fromEntries(
        Object.entries(reportForm).map(([k, v]) => [k, String(v)])
      ),
      ...Object.fromEntries(
        Object.entries(systemForm).map(([k, v]) => [k, String(v)])
      )
    }
    
    const res = await updateSettings(allSettings)
    if (res.data.status === 1) {
      ElMessage.success(res.data.message || '保存成功')
      lastUpdate.value = new Date().toLocaleString('zh-CN')
    } else {
      ElMessage.error(res.data.error || '保存失败')
    }
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('保存设置失败')
  } finally {
    saving.value = false
  }
}

// 重置单个分类
const handleReset = async (category) => {
  try {
    await ElMessageBox.confirm(
      `确定要重置"${getCategoryName(category)}"的所有设置为默认值吗？`,
      '确认重置',
      { type: 'warning' }
    )
    
    resetting.value = true
    const res = await resetSettings(category)
    if (res.data.status === 1) {
      ElMessage.success(res.data.message || '重置成功')
      await fetchSettings()
    } else {
      ElMessage.error(res.data.error || '重置失败')
    }
  } catch (e) {
    if (e !== 'cancel') {
      console.error('重置失败:', e)
    }
  } finally {
    resetting.value = false
  }
}

// 重置所有设置
const handleResetAll = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重置所有设置为默认值吗？此操作不可撤销。',
      '确认重置',
      { type: 'warning' }
    )
    
    resetting.value = true
    const res = await resetSettings()
    if (res.data.status === 1) {
      ElMessage.success(res.data.message || '重置成功')
      await fetchSettings()
    } else {
      ElMessage.error(res.data.error || '重置失败')
    }
  } catch (e) {
    if (e !== 'cancel') {
      console.error('重置失败:', e)
    }
  } finally {
    resetting.value = false
  }
}

// 获取分类名称
const getCategoryName = (category) => {
  const names = {
    analysis: '数据分析参数',
    report: '报告内容设置',
    system: '系统设置',
    model: '模型管理'
  }
  return names[category] || category
}

// ==================== 模型管理功能 ====================

// 获取模型列表
const fetchModelList = async () => {
  modelLoading.value = true
  try {
    const res = await getModels()
    if (res.data.status === 1) {
      modelList.value = res.data.data.models || []
    }
  } catch (error) {
    console.error('获取模型列表失败:', error)
    ElMessage.error('获取模型列表失败')
  } finally {
    modelLoading.value = false
  }
}

// 获取当前模型信息
const fetchCurrentModel = async () => {
  modelLoading.value = true
  try {
    const res = await getCurrentModel()
    if (res.data.status === 1) {
      Object.assign(currentModel, res.data.data)
    }
  } catch (error) {
    console.error('获取当前模型失败:', error)
    ElMessage.error('获取当前模型信息失败')
  } finally {
    modelLoading.value = false
  }
}

// 切换模型
const handleSwitchModel = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要切换到模型 "${row.name}" 吗？切换后将立即生效。`,
      '确认切换',
      { type: 'warning' }
    )
    
    switchingModel.value = row.name
    const res = await switchModel(row.name)
    if (res.data.status === 1) {
      ElMessage.success(res.data.message || '切换成功')
      await fetchCurrentModel()
    } else {
      ElMessage.error(res.data.error || '切换失败')
    }
  } catch (e) {
    if (e !== 'cancel') {
      console.error('切换模型失败:', e)
      ElMessage.error('切换模型失败')
    }
  } finally {
    switchingModel.value = ''
  }
}

// 上传前验证
const beforeModelUpload = (file) => {
  if (!file.name.endsWith('.pth')) {
    ElMessage.error('仅支持 .pth 格式的模型文件')
    return false
  }
  
  // 限制文件大小为 500MB
  const maxSize = 500 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('模型文件不能超过 500MB')
    return false
  }
  
  return true
}

// 上传模型
const handleModelUpload = async (options) => {
  const { file } = options
  
  try {
    // 询问模型名称
    const { value: modelName } = await ElMessageBox.prompt(
      '请输入模型名称（可选，留空则使用文件名）',
      '上传模型',
      {
        confirmButtonText: '上传',
        cancelButtonText: '取消',
        inputPlaceholder: '模型名称'
      }
    )
    
    modelLoading.value = true
    
    const formData = new FormData()
    formData.append('file', file)
    if (modelName) {
      formData.append('model_name', modelName)
    }
    
    const res = await uploadModel(formData)
    if (res.data.status === 1) {
      ElMessage.success(res.data.message || '上传成功')
      await fetchModelList()
    } else {
      ElMessage.error(res.data.error || '上传失败')
    }
  } catch (e) {
    if (e !== 'cancel') {
      console.error('上传模型失败:', e)
      ElMessage.error('上传模型失败')
    }
  } finally {
    modelLoading.value = false
  }
}

// 删除模型
const handleDeleteModel = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模型 "${row.name}" 吗？此操作不可撤销。`,
      '确认删除',
      { type: 'warning' }
    )
    
    modelLoading.value = true
    const res = await deleteModel(row.name)
    if (res.data.status === 1) {
      ElMessage.success(res.data.message || '删除成功')
      await fetchModelList()
    } else {
      ElMessage.error(res.data.error || '删除失败')
    }
  } catch (e) {
    if (e !== 'cancel') {
      console.error('删除模型失败:', e)
      ElMessage.error('删除模型失败')
    }
  } finally {
    modelLoading.value = false
  }
}

// 监听tab切换，加载模型数据
watch(activeTab, (newTab) => {
  if (newTab === 'model') {
    fetchModelList()
    fetchCurrentModel()
  }
})

onMounted(() => {
  fetchSettings()
})
</script>

<style scoped>
.settings-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 70px);
}

.settings-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-left .title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  gap: 10px;
}

.tab-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 15px 0;
  margin-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
  color: #606266;
}

.tab-header .el-icon {
  color: #409eff;
}

.settings-form {
  max-width: 700px;
}

.settings-form .el-form-item {
  margin-bottom: 25px;
}

.form-tip {
  margin-left: 15px;
  color: #909399;
  font-size: 12px;
}

.section-actions {
  padding-top: 20px;
  border-top: 1px dashed #ebeef5;
  margin-top: 20px;
}

.preview-card .card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.last-update {
  margin-top: 15px;
  display: flex;
  align-items: center;
  gap: 5px;
  color: #909399;
  font-size: 12px;
}

/* 模型管理样式 */
.model-status-card,
.model-list-card {
  border: 1px solid #ebeef5;
}

.model-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.model-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.model-tips {
  margin-top: 20px;
}

:deep(.el-tabs__content) {
  padding: 20px;
}

:deep(.el-divider__text) {
  color: #409eff;
  font-weight: 500;
}
</style>
