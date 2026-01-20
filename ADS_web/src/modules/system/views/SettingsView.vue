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
            <el-button @click="handleResetAll" :loading="resetting">
              <el-icon><RefreshRight /></el-icon>
              重置所有
            </el-button>
            <el-button type="primary" @click="handleSaveAll" :loading="saving">
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
    <el-card class="preview-card" shadow="never">
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Setting, 
  RefreshRight, 
  Check, 
  DataAnalysis, 
  Document, 
  Tools,
  View,
  Clock
} from '@element-plus/icons-vue'
import { getSettings, updateSettings, resetSettings } from '@/services/settings'

const loading = ref(false)
const saving = ref(false)
const resetting = ref(false)
const activeTab = ref('analysis')
const lastUpdate = ref('')

// 数据分析参数表单
const analysisForm = reactive({
  analysis_threshold: 1000,
  analysis_circularity_threshold: 0.7,
  analysis_min_area: 100,
  analysis_confidence_threshold: 0.5
})

// 报告内容设置表单
const reportForm = reactive({
  report_show_area: true,
  report_show_perimeter: true,
  report_show_circularity: true,
  report_show_eccentricity: true,
  report_show_intensity: true,
  report_show_histogram: true,
  report_hospital_name: '直肠肿瘤辅助诊断中心',
  report_footer_text: '本报告仅供临床参考，最终诊断以医生意见为准'
})

// 系统设置表单
const systemForm = reactive({
  system_max_upload_size: 50,
  system_session_timeout: 24,
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
    system: '系统设置'
  }
  return names[category] || category
}

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

:deep(.el-tabs__content) {
  padding: 20px;
}

:deep(.el-divider__text) {
  color: #409eff;
  font-weight: 500;
}
</style>
