<template>
  <div class="history-container">
    <!-- 搜索栏 -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="患者ID" :required="!isAdmin">
          <el-input 
            v-model="searchForm.patient_id" 
            placeholder="请输入患者ID" 
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset" v-if="isAdmin">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- 隐私提示 - 仅医生可见 -->
      <el-alert 
        v-if="!isAdmin"
        type="warning" 
        :closable="false" 
        show-icon
        style="margin-top: 12px;"
      >
        <template #title>
          为保护患者隐私，请输入患者ID后查询诊断历史记录
        </template>
      </el-alert>
    </el-card>

    <!-- 历史记录表格 -->
    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>诊断历史记录</span>
          <el-tag type="info">共 {{ pagination.total }} 条记录</el-tag>
        </div>
      </template>

      <!-- 未查询时的提示 -->
      <div v-if="!isAdmin && !hasSearched" class="empty-tip">
        <el-empty description="请输入患者ID进行查询" :image-size="150">
          <template #image>
            <el-icon :size="80" color="#909399"><Lock /></el-icon>
          </template>
        </el-empty>
      </div>

      <!-- 表格内容 -->
      <template v-else>
        <el-table 
          :data="historyList" 
          v-loading="loading"
          stripe
          border
          style="width: 100%"
        >
          <el-table-column prop="id" label="ID" width="80" align="center" />
          <el-table-column prop="patient_id" label="患者ID" width="120" align="center" />
          <el-table-column prop="doctor" label="诊断医生" width="120" align="center" />
          <el-table-column prop="filename" label="文件名" min-width="150" show-overflow-tooltip />
          <el-table-column label="诊断结果" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getResultType(row.features)">
                {{ getResultText(row.features) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="诊断时间" width="180" align="center">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="viewDetail(row)">
                <el-icon><View /></el-icon>
                查看详情
              </el-button>
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
      </template>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog 
      v-model="detailVisible" 
      title="诊断详情" 
      width="700px"
      destroy-on-close
    >
      <div v-if="currentDetail" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="诊断ID">{{ currentDetail.id }}</el-descriptions-item>
          <el-descriptions-item label="患者ID">{{ currentDetail.patient_id }}</el-descriptions-item>
          <el-descriptions-item label="诊断医生">{{ currentDetail.doctor }}</el-descriptions-item>
          <el-descriptions-item label="文件名">{{ currentDetail.filename }}</el-descriptions-item>
          <el-descriptions-item label="诊断时间" :span="2">
            {{ formatDate(currentDetail.created_at) }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 图像预览 -->
        <div class="image-preview" v-if="currentDetail.original_url || currentDetail.mask_url">
          <h4>图像预览</h4>
          <div class="image-grid">
            <div class="image-item" v-if="currentDetail.original_url">
              <p>原始图像</p>
              <el-image 
                :src="getImageUrl(currentDetail.original_url)" 
                fit="contain"
                :preview-src-list="[getImageUrl(currentDetail.original_url)]"
              />
            </div>
            <div class="image-item" v-if="currentDetail.mask_url">
              <p>分割结果</p>
              <el-image 
                :src="getImageUrl(currentDetail.mask_url)" 
                fit="contain"
                :preview-src-list="[getImageUrl(currentDetail.mask_url)]"
              />
            </div>
          </div>
        </div>

        <!-- 特征数据 -->
        <div class="features-section" v-if="currentDetail.features">
          <h4>特征分析</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="面积">
              {{ currentDetail.features.area || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="周长">
              {{ currentDetail.features.perimeter || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="圆度">
              {{ currentDetail.features.circularity?.toFixed(4) || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="离心率">
              {{ currentDetail.features.eccentricity?.toFixed(4) || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="平均灰度">
              {{ currentDetail.features.mean_intensity?.toFixed(2) || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="灰度标准差">
              {{ currentDetail.features.std_intensity?.toFixed(2) || '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, View, Lock } from '@element-plus/icons-vue'
import { getDiagnosisHistory, getDiagnosisDetail } from '@/services/diagnosis'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()

const loading = ref(false)
const historyList = ref([])
const detailVisible = ref(false)
const currentDetail = ref(null)
const hasSearched = ref(false) // 是否已执行过搜索

// 判断是否是管理员
const isAdmin = computed(() => authStore.userInfo?.role === 'admin')

const searchForm = reactive({
  patient_id: ''
})

const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0
})

// 获取历史列表
const fetchHistory = async () => {
  loading.value = true
  try {
    const res = await getDiagnosisHistory({
      page: pagination.page,
      per_page: pagination.per_page,
      patient_id: searchForm.patient_id || undefined
    })
    if (res.data.success) {
      historyList.value = res.data.data.items || []
      pagination.total = res.data.data.total || 0
    }
  } catch (error) {
    console.error('获取历史记录失败:', error)
    ElMessage.error('获取历史记录失败')
  } finally {
    loading.value = false
  }
}

// 查看详情
const viewDetail = async (row) => {
  try {
    const res = await getDiagnosisDetail(row.id)
    if (res.data.success) {
      currentDetail.value = res.data.data
      detailVisible.value = true
    }
  } catch (error) {
    console.error('获取详情失败:', error)
    ElMessage.error('获取详情失败')
  }
}

// 搜索
const handleSearch = () => {
  // 非管理员必须输入患者ID
  if (!isAdmin.value && !searchForm.patient_id.trim()) {
    ElMessage.warning('请输入患者ID进行查询')
    return
  }
  hasSearched.value = true
  pagination.page = 1
  fetchHistory()
}

// 重置
const handleReset = () => {
  searchForm.patient_id = ''
  pagination.page = 1
  fetchHistory()
}

// 分页
const handleSizeChange = (size) => {
  pagination.per_page = size
  pagination.page = 1
  fetchHistory()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchHistory()
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

// 获取结果类型
const getResultType = (features) => {
  if (!features || !features.area) return 'info'
  return features.area > 1000 ? 'danger' : 'success'
}

// 获取结果文本
const getResultText = (features) => {
  if (!features || !features.area) return '未分析'
  return features.area > 1000 ? '需关注' : '正常'
}

onMounted(() => {
  // 管理员自动加载数据，医生需要输入患者ID后才能查询
  if (isAdmin.value) {
    hasSearched.value = true
    fetchHistory()
  }
})
</script>

<style scoped>
.history-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 70px);
}

.search-card {
  margin-bottom: 20px;
}

.search-form {
  display: flex;
  align-items: center;
}

.table-card {
  background: #fff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.detail-content {
  padding: 10px 0;
}

.image-preview {
  margin-top: 20px;
}

.image-preview h4,
.features-section h4 {
  margin-bottom: 15px;
  color: #303133;
  font-size: 16px;
  border-left: 4px solid #409eff;
  padding-left: 10px;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.image-item {
  text-align: center;
}

.image-item p {
  margin-bottom: 10px;
  color: #606266;
}

.image-item .el-image {
  width: 100%;
  max-height: 250px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.features-section {
  margin-top: 20px;
}

.empty-tip {
  padding: 60px 0;
  text-align: center;
}
</style>
