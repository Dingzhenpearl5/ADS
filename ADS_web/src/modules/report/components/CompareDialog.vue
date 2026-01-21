<template>
  <el-dialog 
    v-model="visible" 
    title="历史记录对比分析" 
    width="95%"
    top="3vh"
    destroy-on-close
    class="compare-dialog"
    @close="handleClose"
  >
    <div class="compare-content" v-loading="loading">
      <!-- 时间轴提示 -->
      <el-alert type="info" :closable="false" style="margin-bottom: 20px;">
        <template #title>
          已选择 {{ compareDetails.length }} 条记录进行对比，按诊断时间从早到晚排列
        </template>
      </el-alert>

      <!-- 对比卡片区域 -->
      <div class="compare-cards">
        <el-card 
          v-for="(item, index) in compareDetails" 
          :key="item.id" 
          class="compare-card"
          :class="{ 'first-record': index === 0, 'last-record': index === compareDetails.length - 1 }"
        >
          <template #header>
            <div class="compare-card-header">
              <el-tag :type="index === 0 ? 'info' : index === compareDetails.length - 1 ? 'success' : ''">
                {{ index === 0 ? '最早' : index === compareDetails.length - 1 ? '最新' : `第${index + 1}次` }}
              </el-tag>
              <span class="compare-time">{{ formatDate(item.created_at) }}</span>
            </div>
          </template>
          
          <!-- 图像对比 -->
          <div class="compare-images">
            <div class="compare-image-item" v-if="item.mask_url">
              <p>分割结果</p>
              <el-image 
                :src="getImageUrl(item.mask_url)" 
                fit="contain"
                :preview-src-list="compareDetails.map(d => getImageUrl(d.mask_url)).filter(Boolean)"
                :initial-index="index"
              />
            </div>
            <div class="compare-image-item" v-else>
              <p>分割结果</p>
              <el-empty description="无图像" :image-size="60" />
            </div>
          </div>
          
          <!-- 特征数据 -->
          <div class="compare-features" v-if="item.features">
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="面积">
                <span :class="getChangeClass(item, 'area', index)">
                  {{ item.features.area || '-' }}
                  <span v-if="index > 0 && item.features.area" class="change-indicator">
                    {{ getChangeIndicator(item, 'area', index) }}
                  </span>
                </span>
              </el-descriptions-item>
              <el-descriptions-item label="周长">
                <span :class="getChangeClass(item, 'perimeter', index)">
                  {{ item.features.perimeter || '-' }}
                  <span v-if="index > 0 && item.features.perimeter" class="change-indicator">
                    {{ getChangeIndicator(item, 'perimeter', index) }}
                  </span>
                </span>
              </el-descriptions-item>
              <el-descriptions-item label="圆度">
                {{ item.features.circularity?.toFixed(4) || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="离心率">
                {{ item.features.eccentricity?.toFixed(4) || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="平均灰度">
                {{ item.features.mean_intensity?.toFixed(2) || '-' }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </div>

      <!-- 变化趋势图表 -->
      <el-card class="trend-card" v-if="compareDetails.length >= 2">
        <template #header>
          <div class="trend-header">
            <el-icon><TrendCharts /></el-icon>
            <span>变化趋势</span>
          </div>
        </template>
        <div class="trend-content">
          <div class="trend-summary">
            <div class="trend-item">
              <span class="trend-label">面积变化：</span>
              <span :class="getTrendClass('area')">
                {{ getTrendText('area') }}
              </span>
            </div>
            <div class="trend-item">
              <span class="trend-label">周长变化：</span>
              <span :class="getTrendClass('perimeter')">
                {{ getTrendText('perimeter') }}
              </span>
            </div>
          </div>
          <el-alert 
            :type="overallTrendType" 
            :closable="false"
            style="margin-top: 15px;"
          >
            <template #title>
              <strong>综合评估：</strong>{{ overallTrendText }}
            </template>
          </el-alert>
        </div>
      </el-card>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { TrendCharts } from '@element-plus/icons-vue'
import { getDiagnosisDetail } from '@/services/diagnosis'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  selectedRows: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const loading = ref(false)
const compareDetails = ref([])

// 监听弹窗打开
watch(() => props.modelValue, async (newVal) => {
  if (newVal && props.selectedRows.length >= 2) {
    await fetchCompareDetails()
  }
})

// 获取对比详情
const fetchCompareDetails = async () => {
  loading.value = true
  compareDetails.value = []
  
  try {
    const detailPromises = props.selectedRows.map(row => getDiagnosisDetail(row.id))
    const results = await Promise.all(detailPromises)
    
    // 按时间排序（从早到晚）
    const details = results
      .filter(res => res.status === 1 && res.data)
      .map(res => res.data)
      .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
    
    compareDetails.value = details
  } catch (error) {
    console.error('获取对比数据失败:', error)
    ElMessage.error('获取对比数据失败')
  } finally {
    loading.value = false
  }
}

// 关闭弹窗
const handleClose = () => {
  compareDetails.value = []
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 获取图片完整URL
const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5003'
  return `${baseUrl}${path}`
}

// 获取变化样式类
const getChangeClass = (item, field, index) => {
  if (index === 0) return ''
  const prev = compareDetails.value[index - 1]
  if (!prev?.features?.[field] || !item?.features?.[field]) return ''
  
  const change = item.features[field] - prev.features[field]
  if (change > 0) return 'value-increase'
  if (change < 0) return 'value-decrease'
  return ''
}

// 获取变化指示器
const getChangeIndicator = (item, field, index) => {
  if (index === 0) return ''
  const prev = compareDetails.value[index - 1]
  if (!prev?.features?.[field] || !item?.features?.[field]) return ''
  
  const change = item.features[field] - prev.features[field]
  const percent = ((change / prev.features[field]) * 100).toFixed(1)
  
  if (change > 0) return `↑${percent}%`
  if (change < 0) return `↓${Math.abs(percent)}%`
  return '→'
}

// 获取趋势样式类
const getTrendClass = (field) => {
  if (compareDetails.value.length < 2) return ''
  const first = compareDetails.value[0]?.features?.[field]
  const last = compareDetails.value[compareDetails.value.length - 1]?.features?.[field]
  if (!first || !last) return ''
  
  if (last > first) return 'trend-up'
  if (last < first) return 'trend-down'
  return 'trend-stable'
}

// 获取趋势文本
const getTrendText = (field) => {
  if (compareDetails.value.length < 2) return '数据不足'
  const first = compareDetails.value[0]?.features?.[field]
  const last = compareDetails.value[compareDetails.value.length - 1]?.features?.[field]
  if (!first || !last) return '无数据'
  
  const change = last - first
  const percent = ((change / first) * 100).toFixed(1)
  
  if (change > 0) return `增加 ${percent}% (${first} → ${last})`
  if (change < 0) return `减少 ${Math.abs(percent)}% (${first} → ${last})`
  return `保持稳定 (${first})`
}

// 整体趋势类型
const overallTrendType = computed(() => {
  if (compareDetails.value.length < 2) return 'info'
  const first = compareDetails.value[0]?.features?.area
  const last = compareDetails.value[compareDetails.value.length - 1]?.features?.area
  if (!first || !last) return 'info'
  
  const changePercent = ((last - first) / first) * 100
  if (changePercent > 10) return 'warning'
  if (changePercent < -10) return 'success'
  return 'info'
})

// 整体趋势文本
const overallTrendText = computed(() => {
  if (compareDetails.value.length < 2) return '数据不足，无法评估变化趋势'
  const first = compareDetails.value[0]?.features?.area
  const last = compareDetails.value[compareDetails.value.length - 1]?.features?.area
  if (!first || !last) return '特征数据不完整，无法评估'
  
  const changePercent = ((last - first) / first) * 100
  const timeSpan = compareDetails.value.length
  
  if (changePercent > 20) {
    return `在 ${timeSpan} 次诊断期间，肿瘤面积显著增加 ${changePercent.toFixed(1)}%，建议密切关注并尽快复诊`
  }
  if (changePercent > 10) {
    return `在 ${timeSpan} 次诊断期间，肿瘤面积有所增加 ${changePercent.toFixed(1)}%，建议继续观察`
  }
  if (changePercent < -20) {
    return `在 ${timeSpan} 次诊断期间，肿瘤面积显著减少 ${Math.abs(changePercent).toFixed(1)}%，治疗效果良好`
  }
  if (changePercent < -10) {
    return `在 ${timeSpan} 次诊断期间，肿瘤面积有所减少 ${Math.abs(changePercent).toFixed(1)}%，病情趋于稳定`
  }
  return `在 ${timeSpan} 次诊断期间，肿瘤面积基本稳定，变化 ${changePercent.toFixed(1)}%`
})
</script>

<style scoped>
/* 对比弹窗样式 */
.compare-dialog :deep(.el-dialog__body) {
  max-height: calc(90vh - 120px);
  overflow-y: auto;
}

.compare-content {
  padding: 10px 0;
}

.compare-cards {
  display: flex;
  gap: 20px;
  overflow-x: auto;
  padding-bottom: 10px;
}

.compare-card {
  flex: 0 0 280px;
  min-width: 280px;
}

.compare-card.first-record {
  border-top: 3px solid #909399;
}

.compare-card.last-record {
  border-top: 3px solid #67c23a;
}

.compare-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.compare-time {
  font-size: 13px;
  color: #909399;
}

.compare-images {
  margin-bottom: 15px;
}

.compare-image-item {
  text-align: center;
}

.compare-image-item p {
  margin-bottom: 8px;
  color: #606266;
  font-size: 13px;
}

.compare-image-item .el-image {
  width: 100%;
  height: 180px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.compare-features {
  margin-top: 10px;
}

/* 变化指示 */
.value-increase {
  color: #f56c6c;
  font-weight: 600;
}

.value-decrease {
  color: #67c23a;
  font-weight: 600;
}

.change-indicator {
  font-size: 12px;
  margin-left: 5px;
}

/* 趋势卡片 */
.trend-card {
  margin-top: 20px;
}

.trend-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trend-content {
  padding: 10px 0;
}

.trend-summary {
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
}

.trend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trend-label {
  color: #606266;
}

.trend-up {
  color: #f56c6c;
  font-weight: 600;
}

.trend-down {
  color: #67c23a;
  font-weight: 600;
}

.trend-stable {
  color: #909399;
}
</style>
