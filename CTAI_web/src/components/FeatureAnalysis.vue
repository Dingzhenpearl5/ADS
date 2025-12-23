<template>
  <div class="feature-analysis">
    <div class="custom-card">
      <div class="section-title">
        <el-icon><DataAnalysis /></el-icon>
        <span>特征分析与对比</span>
        <div class="header-actions" v-if="!showUploadButton">
          <el-button link type="primary" @click="triggerReupload">
            <el-icon><Refresh /></el-icon> 重新选择
          </el-button>
          <input
            ref="reuploadInput"
            style="display: none"
            type="file"
            @change="handleFileChange"
          >
        </div>
      </div>

      <el-tabs v-model="activeTab" class="custom-tabs" @tab-click="handleTabClick">
        <el-tab-pane name="first">
          <template #label>
            <span class="tab-label"><el-icon><List /></el-icon> 特征列表</span>
          </template>
          <el-table
            :data="featureList"
            height="400"
            v-loading="loading"
            class="modern-table"
          >
            <el-table-column label="特征类别" prop="2" width="180" />
            <el-table-column label="特征名称" prop="0" />
            <el-table-column label="数值" prop="1" width="120">
              <template #default="scope">
                <span class="feature-value">{{ scope.row[1] }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane name="second">
          <template #label>
            <span class="tab-label"><el-icon><PieChart /></el-icon> 面积对比</span>
          </template>
          <div class="chart-container">
            <div id="area" class="chart-box"></div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane name="third">
          <template #label>
            <span class="tab-label"><el-icon><TrendCharts /></el-icon> 周长对比</span>
          </template>
          <div class="chart-container">
            <div id="perimeter" class="chart-box"></div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { DataAnalysis, Refresh, List, PieChart, TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const props = defineProps({
  featureList: Array,
  loading: Boolean,
  showUploadButton: Boolean,
  areaData: Number,
  perimeterData: Number
})

const emit = defineEmits(['upload'])
const activeTab = ref('first')
const reuploadInput = ref(null)

let areaChart = null
let perimeterChart = null

const triggerReupload = () => {
  reuploadInput.value.click()
}

const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    emit('upload', file)
  }
}

const initCharts = () => {
  if (activeTab.value === 'second') {
    nextTick(() => {
      const chartDom = document.getElementById('area')
      if (chartDom) {
        if (!areaChart) areaChart = echarts.init(chartDom)
        areaChart.setOption({
          tooltip: { trigger: 'axis' },
          grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
          xAxis: { type: 'category', data: ['样本1', '样本2', '样本3', '样本4', '样本5', '样本6', '样本7', '当前'] },
          yAxis: { type: 'value', name: '面积 (px²)' },
          series: [{
            name: '面积',
            type: 'line',
            smooth: true,
            data: [1300, 1290, 1272, 1123.5, 1123, 1092, 1086, props.areaData],
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
    })
  } else if (activeTab.value === 'third') {
    nextTick(() => {
      const chartDom = document.getElementById('perimeter')
      if (chartDom) {
        if (!perimeterChart) perimeterChart = echarts.init(chartDom)
        perimeterChart.setOption({
          tooltip: { trigger: 'axis' },
          grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
          xAxis: { type: 'category', data: ['样本1', '样本2', '样本3', '样本4', '样本5', '样本6', '样本7', '当前'] },
          yAxis: { type: 'value', name: '周长 (px)' },
          series: [{
            name: '周长',
            type: 'bar',
            data: [150, 145, 142, 138, 135, 130, 128, props.perimeterData],
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
}

const handleTabClick = () => {
  initCharts()
}

watch(() => props.areaData, () => {
  if (areaChart) initCharts()
})

watch(() => props.perimeterData, () => {
  if (perimeterChart) initCharts()
})

onMounted(() => {
  window.addEventListener('resize', () => {
    areaChart?.resize()
    perimeterChart?.resize()
  })
})
</script>

<style scoped>
.feature-analysis {
  height: 100%;
}

.header-actions {
  margin-left: auto;
}

.custom-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background-color: #f1f5f9;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.modern-table {
  border-radius: 8px;
  overflow: hidden;
}

.feature-value {
  font-family: 'Monaco', 'Menlo', monospace;
  font-weight: 600;
  color: var(--primary-color);
}

.chart-container {
  padding: 20px 0;
}

.chart-box {
  width: 100%;
  height: 400px;
}
</style>
