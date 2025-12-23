<template>
  <div class="feature-analysis">
    <el-card style="border-radius: 8px;">
      <template #header>
        <div class="clearfix">
          <span>肿瘤区域特征值</span>
          <el-button
            style="margin-left: 35px"
            v-show="!showUploadButton"
            type="primary"
            :icon="Upload"
            class="download_bt"
            @click="triggerReupload"
          >
            重新选择图像
            <input
              ref="reuploadInput"
              style="display: none"
              type="file"
              @change="handleFileChange"
            >
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <el-tab-pane label="肿瘤区域特征值" name="first">
          <el-table
            :data="featureList"
            height="390"
            border
            style="width:750px;text-align:center;"
            v-loading="loading"
          >
            <el-table-column label="Feature" prop="2" width="250px" />
            <el-table-column label="特征名" prop="0" width="250px" />
            <el-table-column label="特征值" prop="1" width="250px" />
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="面积对比" name="second">
          <div id="area" style="width: 750px; height: 400px;"></div>
        </el-tab-pane>
        
        <el-tab-pane label="周长对比" name="third">
          <div id="perimeter" style="width: 750px; height: 400px;"></div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits, onMounted, watch, nextTick } from 'vue'
import { Upload } from '@element-plus/icons-vue'
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
          xAxis: { type: 'category', data: ['1', '2', '3', '4', '5', '6', '7', '8'] },
          yAxis: { type: 'value', name: '面积' },
          series: [{
            name: '面积',
            type: 'line',
            data: [1300, 1290, 1272, 1123.5, 1123, 1092, 1086, props.areaData],
            areaStyle: {}
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
          xAxis: { type: 'category', data: ['1', '2', '3', '4', '5', '6', '7', '8'] },
          yAxis: { type: 'value', name: '周长' },
          series: [{
            name: '周长',
            type: 'line',
            data: [250, 243, 227, 201, 197, 170, 159, props.perimeterData],
            areaStyle: {}
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
  if (activeTab.value === 'second') initCharts()
})

watch(() => props.perimeterData, () => {
  if (activeTab.value === 'third') initCharts()
})

onMounted(() => {
  window.addEventListener('resize', () => {
    areaChart?.resize()
    perimeterChart?.resize()
  })
})
</script>
