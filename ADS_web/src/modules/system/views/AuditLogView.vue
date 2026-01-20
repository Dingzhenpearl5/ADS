<template>
  <div class="audit-log-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
              <el-icon :size="28"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total }}</div>
              <div class="stat-label">总日志数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
              <el-icon :size="28"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.today_count }}</div>
              <div class="stat-label">今日日志</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
              <el-icon :size="28"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.active_users?.length || 0 }}</div>
              <div class="stat-label">活跃用户</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)">
              <el-icon :size="28"><Grid /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.module_stats?.length || 0 }}</div>
              <div class="stat-label">涉及模块</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选和操作栏 -->
    <el-card class="filter-card" shadow="never">
      <div class="filter-bar">
        <div class="filter-left">
          <el-input
            v-model="filters.username"
            placeholder="用户名"
            clearable
            style="width: 120px"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.module" placeholder="模块" clearable style="width: 120px" @change="handleSearch">
            <el-option label="认证" value="auth" />
            <el-option label="设置" value="settings" />
            <el-option label="公告" value="announcement" />
            <el-option label="诊断" value="diagnosis" />
            <el-option label="患者" value="patient" />
            <el-option label="审计" value="audit" />
            <el-option label="系统" value="system" />
          </el-select>
          <el-select v-model="filters.action" placeholder="操作类型" clearable style="width: 120px" @change="handleSearch">
            <el-option label="登录" value="login" />
            <el-option label="登出" value="logout" />
            <el-option label="创建" value="create" />
            <el-option label="更新" value="update" />
            <el-option label="删除" value="delete" />
            <el-option label="发布" value="publish" />
            <el-option label="下架" value="archive" />
            <el-option label="重置" value="reset" />
            <el-option label="导出" value="export" />
            <el-option label="上传" value="upload" />
          </el-select>
          <el-select v-model="filters.status" placeholder="状态" clearable style="width: 100px" @change="handleSearch">
            <el-option label="成功" value="success" />
            <el-option label="失败" value="fail" />
          </el-select>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 240px"
            @change="handleDateChange"
          />
          <el-input
            v-model="filters.keyword"
            placeholder="关键词搜索"
            clearable
            style="width: 150px"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshRight /></el-icon>
            重置
          </el-button>
        </div>
        <div class="filter-right">
          <el-button type="success" @click="handleExport" :loading="exporting">
            <el-icon><Download /></el-icon>
            导出CSV
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 日志列表 -->
    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon :size="20" color="#409eff"><Notebook /></el-icon>
            <span>审计日志</span>
          </div>
          <el-tag type="info">共 {{ pagination.total }} 条记录</el-tag>
        </div>
      </template>

      <el-table :data="logs" v-loading="loading" stripe border>
        <el-table-column prop="id" label="ID" width="70" align="center" />
        <el-table-column prop="created_at" label="时间" width="170" align="center" />
        <el-table-column prop="username" label="用户" width="100" align="center">
          <template #default="{ row }">
            <span>{{ row.username || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="getActionType(row.action)" size="small">
              {{ getActionLabel(row.action) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="模块" width="90" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small" effect="plain">
              {{ getModuleLabel(row.module) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target" label="目标" width="120" show-overflow-tooltip>
          <template #default="{ row }">
            <span>{{ row.target || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="detail" label="详情" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="detail-text">{{ formatDetail(row.detail) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="130" align="center">
          <template #default="{ row }">
            <span class="ip-text">{{ row.ip_address || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 统计图表 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>最近7天趋势</span>
            </div>
          </template>
          <div class="chart-content">
            <div v-if="stats.daily_stats?.length" class="simple-chart">
              <div 
                v-for="(item, index) in stats.daily_stats" 
                :key="index" 
                class="chart-bar-item"
              >
                <div class="bar-label">{{ formatDate(item.date) }}</div>
                <div class="bar-container">
                  <div 
                    class="bar-fill" 
                    :style="{ width: getBarWidth(item.count) + '%' }"
                  ></div>
                  <span class="bar-value">{{ item.count }}</span>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无数据" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>活跃用户排行</span>
            </div>
          </template>
          <div class="chart-content">
            <div v-if="stats.active_users?.length" class="user-rank-list">
              <div 
                v-for="(item, index) in stats.active_users" 
                :key="index" 
                class="rank-item"
              >
                <span class="rank-num" :class="{ 'top-three': index < 3 }">{{ index + 1 }}</span>
                <span class="rank-name">{{ item.username }}</span>
                <span class="rank-count">{{ item.count }} 次操作</span>
              </div>
            </div>
            <el-empty v-else description="暂无数据" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Document,
  Clock,
  User,
  Grid,
  Search,
  RefreshRight,
  Download,
  Notebook
} from '@element-plus/icons-vue'
import request from '../../../services/request'

// 筛选条件
const filters = reactive({
  username: '',
  action: '',
  module: '',
  status: '',
  keyword: '',
  start_date: '',
  end_date: ''
})

const dateRange = ref([])

// 分页
const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

// 数据
const logs = ref([])
const stats = ref({})
const loading = ref(false)
const exporting = ref(false)

// 操作类型映射
const actionMap = {
  login: { label: '登录', type: 'success' },
  logout: { label: '登出', type: 'info' },
  create: { label: '创建', type: 'primary' },
  update: { label: '更新', type: 'warning' },
  delete: { label: '删除', type: 'danger' },
  publish: { label: '发布', type: 'success' },
  archive: { label: '下架', type: 'warning' },
  reset: { label: '重置', type: 'info' },
  export: { label: '导出', type: 'primary' },
  upload: { label: '上传', type: 'primary' },
  view: { label: '查看', type: 'info' }
}

// 模块映射
const moduleMap = {
  auth: '认证',
  settings: '设置',
  announcement: '公告',
  diagnosis: '诊断',
  patient: '患者',
  audit: '审计',
  system: '系统'
}

const getActionLabel = (action) => actionMap[action]?.label || action
const getActionType = (action) => actionMap[action]?.type || 'info'
const getModuleLabel = (module) => moduleMap[module] || module

const formatDetail = (detail) => {
  if (!detail) return '-'
  try {
    const obj = JSON.parse(detail)
    return Object.entries(obj)
      .map(([k, v]) => `${k}: ${v}`)
      .join(', ')
  } catch {
    return detail
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

const getBarWidth = (count) => {
  if (!stats.value.daily_stats?.length) return 0
  const max = Math.max(...stats.value.daily_stats.map(d => d.count))
  return max > 0 ? (count / max) * 100 : 0
}

// 获取日志列表
const fetchLogs = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      ...filters
    }
    // 移除空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })
    
    const res = await request.get('/api/audit-logs', { params })
    if (res.data.status === 1) {
      logs.value = res.data.data.list
      pagination.total = res.data.data.total
    } else {
      ElMessage.error(res.data.error || '获取日志失败')
    }
  } catch (error) {
    ElMessage.error('获取日志失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const res = await request.get('/api/audit-logs/stats')
    if (res.data.status === 1) {
      stats.value = res.data.data
    }
  } catch (error) {
    console.error('获取统计失败', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchLogs()
}

// 重置筛选
const handleReset = () => {
  filters.username = ''
  filters.action = ''
  filters.module = ''
  filters.status = ''
  filters.keyword = ''
  filters.start_date = ''
  filters.end_date = ''
  dateRange.value = []
  pagination.page = 1
  fetchLogs()
}

// 日期变化
const handleDateChange = (val) => {
  if (val && val.length === 2) {
    filters.start_date = val[0]
    filters.end_date = val[1]
  } else {
    filters.start_date = ''
    filters.end_date = ''
  }
  handleSearch()
}

// 分页
const handleSizeChange = (size) => {
  pagination.per_page = size
  pagination.page = 1
  fetchLogs()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchLogs()
}

// 导出
const handleExport = async () => {
  exporting.value = true
  try {
    const params = new URLSearchParams()
    if (filters.start_date) params.append('start_date', filters.start_date)
    if (filters.end_date) params.append('end_date', filters.end_date)
    
    const url = `/api/audit-logs/export${params.toString() ? '?' + params.toString() : ''}`
    
    // 使用 fetch 下载文件
    const token = localStorage.getItem('token')
    const response = await fetch(`http://127.0.0.1:5003${url}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.ok) {
      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = `audit_logs_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(downloadUrl)
      ElMessage.success('导出成功')
    } else {
      ElMessage.error('导出失败')
    }
  } catch (error) {
    ElMessage.error('导出失败')
    console.error(error)
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  fetchLogs()
  fetchStats()
})
</script>

<style scoped>
.audit-log-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 12px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.filter-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.table-card {
  border-radius: 12px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.detail-text {
  color: #606266;
  font-size: 13px;
}

.ip-text {
  font-family: monospace;
  font-size: 13px;
  color: #909399;
}

.charts-row {
  margin-top: 20px;
}

.chart-card {
  border-radius: 12px;
}

.chart-content {
  min-height: 200px;
}

.simple-chart {
  padding: 10px 0;
}

.chart-bar-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.bar-label {
  width: 50px;
  font-size: 13px;
  color: #606266;
}

.bar-container {
  flex: 1;
  height: 24px;
  background: #f0f2f5;
  border-radius: 4px;
  position: relative;
  display: flex;
  align-items: center;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #409eff 0%, #67c23a 100%);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.bar-value {
  position: absolute;
  right: 8px;
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.user-rank-list {
  padding: 10px 0;
}

.rank-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  margin-bottom: 8px;
  background: #f9fafc;
  border-radius: 8px;
  transition: all 0.2s;
}

.rank-item:hover {
  background: #ecf5ff;
}

.rank-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #909399;
  margin-right: 12px;
}

.rank-num.top-three {
  background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
  color: white;
}

.rank-name {
  flex: 1;
  font-weight: 500;
  color: #303133;
}

.rank-count {
  font-size: 13px;
  color: #909399;
}
</style>
