<template>
  <div class="statistics-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="8">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon total">
              <el-icon :size="32"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">诊断总数</p>
              <p class="stat-value">{{ statistics.total_diagnoses || 0 }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon patients">
              <el-icon :size="32"><User /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">患者总数</p>
              <p class="stat-value">{{ statistics.total_patients || 0 }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon today">
              <el-icon :size="32"><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">今日诊断</p>
              <p class="stat-value">{{ statistics.today_diagnoses || 0 }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>近7天诊断趋势</span>
              <el-button type="primary" link @click="fetchStatistics">
                <el-icon><Refresh /></el-icon>
                刷新数据
              </el-button>
            </div>
          </template>
          <div class="chart-container" ref="trendChartRef"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <span>系统状态</span>
          </template>
          <div class="system-status">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="后端服务">
                <el-tag :type="systemStatus.backend ? 'success' : 'danger'">
                  {{ systemStatus.backend ? '正常' : '异常' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="模型状态">
                <el-tag :type="systemStatus.model ? 'success' : 'warning'">
                  {{ systemStatus.model ? '已加载' : '未加载' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="数据库">
                <el-tag :type="systemStatus.database ? 'success' : 'danger'">
                  {{ systemStatus.database ? '已连接' : '未连接' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="检查时间">
                {{ systemStatus.checkTime || '-' }}
              </el-descriptions-item>
            </el-descriptions>
            <el-button 
              type="primary" 
              class="check-btn"
              @click="checkSystemHealth"
              :loading="checking"
            >
              <el-icon><Monitor /></el-icon>
              检查系统状态
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 数据详情表格 -->
    <el-card class="detail-card" shadow="never">
      <template #header>
        <span>近7天数据明细</span>
      </template>
      <el-table :data="trendData" stripe border>
        <el-table-column prop="date" label="日期" align="center" />
        <el-table-column prop="count" label="诊断数量" align="center">
          <template #default="{ row }">
            <el-tag>{{ row.count }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="占比" align="center">
          <template #default="{ row }">
            <el-progress 
              :percentage="getPercentage(row.count)" 
              :stroke-width="10"
              :format="() => `${getPercentage(row.count)}%`"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, User, Calendar, Refresh, Monitor } from '@element-plus/icons-vue'
import { getStatistics, healthCheck } from '@/services/diagnosis'
import * as echarts from 'echarts'

const trendChartRef = ref(null)
let trendChart = null

const loading = ref(false)
const checking = ref(false)

const statistics = reactive({
  total_diagnoses: 0,
  total_patients: 0,
  today_diagnoses: 0
})

const trendData = ref([])

const systemStatus = reactive({
  backend: false,
  model: false,
  database: false,
  checkTime: ''
})

// 获取统计数据
const fetchStatistics = async () => {
  loading.value = true
  try {
    const res = await getStatistics()
    if (res.status === 1 && res.data) {
      const data = res.data
      statistics.total_diagnoses = data.total_diagnoses || 0
      statistics.total_patients = data.total_patients || 0
      statistics.today_diagnoses = data.today_diagnoses || 0
      trendData.value = data.trend || []
      
      // 更新图表
      updateChart()
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

// 检查系统健康状态
const checkSystemHealth = async () => {
  checking.value = true
  try {
    const res = await healthCheck()
    // 后端返回格式: { status: 1, data: { database: "正常", model: "...", server: "..." } }
    if (res.status === 1) {
      systemStatus.backend = true
      systemStatus.model = res.data.model && !res.data.model.includes('未加载')
      systemStatus.database = res.data.database === '正常'
      systemStatus.checkTime = new Date().toLocaleString('zh-CN')
      ElMessage.success('系统状态检查完成')
    } else {
      throw new Error(res.error || '检查失败')
    }
  } catch (error) {
    console.error('健康检查失败:', error)
    systemStatus.backend = false
    systemStatus.model = false
    systemStatus.database = false
    systemStatus.checkTime = new Date().toLocaleString('zh-CN')
    ElMessage.error('后端服务无响应')
  } finally {
    checking.value = false
  }
}

// 初始化图表
const initChart = () => {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    updateChart()
  }
}

// 更新图表
const updateChart = () => {
  if (!trendChart) return

  const dates = trendData.value.map(item => item.date)
  const counts = trendData.value.map(item => item.count)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      minInterval: 1
    },
    series: [
      {
        name: '诊断数量',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#409eff' },
            { offset: 1, color: '#79bbff' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#337ecc' },
              { offset: 1, color: '#409eff' }
            ])
          }
        }
      },
      {
        name: '趋势线',
        type: 'line',
        data: counts,
        smooth: true,
        lineStyle: {
          color: '#67c23a',
          width: 2
        },
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: {
          color: '#67c23a'
        }
      }
    ]
  }

  trendChart.setOption(option)
}

// 计算占比
const getPercentage = (count) => {
  const total = trendData.value.reduce((sum, item) => sum + item.count, 0)
  if (total === 0) return 0
  return Math.round((count / total) * 100)
}

// 窗口大小变化时重新调整图表
const handleResize = () => {
  trendChart?.resize()
}

onMounted(() => {
  fetchStatistics()
  checkSystemHealth()
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
})
</script>

<style scoped>
.statistics-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 70px);
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
}

.stat-icon.total {
  background: linear-gradient(135deg, #409eff 0%, #79bbff 100%);
  color: #fff;
}

.stat-icon.patients {
  background: linear-gradient(135deg, #67c23a 0%, #95d475 100%);
  color: #fff;
}

.stat-icon.today {
  background: linear-gradient(135deg, #e6a23c 0%, #f3d19e 100%);
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
}

.system-status {
  padding: 10px 0;
}

.check-btn {
  width: 100%;
  margin-top: 20px;
}

.detail-card {
  margin-top: 20px;
}
</style>
