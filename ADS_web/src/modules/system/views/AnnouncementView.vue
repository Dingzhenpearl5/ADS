<template>
  <div class="announcement-container">
    <!-- 操作栏 -->
    <el-card class="action-card" shadow="never">
      <div class="action-bar">
        <div class="action-left">
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建公告
          </el-button>
        </div>
        <div class="action-right">
          <el-select v-model="filterStatus" placeholder="全部状态" clearable @change="fetchAnnouncements">
            <el-option label="全部" value="" />
            <el-option label="草稿" value="draft" />
            <el-option label="已发布" value="published" />
            <el-option label="已下架" value="archived" />
          </el-select>
        </div>
      </div>
    </el-card>

    <!-- 公告列表 -->
    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>公告管理</span>
          <el-tag type="info">共 {{ pagination.total }} 条</el-tag>
        </div>
      </template>

      <el-table :data="announcements" v-loading="loading" stripe border>
        <el-table-column prop="id" label="ID" width="70" align="center" />
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.type" size="small">{{ getTypeName(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.priority >= 10" type="danger" size="small">置顶</el-tag>
            <span v-else>{{ row.priority }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by" label="创建人" width="100" align="center" />
        <el-table-column prop="created_at" label="创建时间" width="170" align="center" />
        <el-table-column prop="published_at" label="发布时间" width="170" align="center">
          <template #default="{ row }">
            {{ row.published_at || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button 
              v-if="row.status === 'draft'" 
              type="success" 
              link 
              size="small" 
              @click="handlePublish(row)"
            >
              <el-icon><Promotion /></el-icon>发布
            </el-button>
            <el-button 
              v-if="row.status === 'published'" 
              type="warning" 
              link 
              size="small" 
              @click="handleArchive(row)"
            >
              <el-icon><Download /></el-icon>下架
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 编辑弹窗 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑公告' : '新建公告'" 
      width="650px"
      destroy-on-close
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入公告标题" maxlength="100" show-word-limit />
        </el-form-item>
        
        <el-form-item label="类型" prop="type">
          <el-select v-model="form.type" style="width: 100%">
            <el-option label="普通信息" value="info">
              <el-tag type="info" size="small">普通信息</el-tag>
            </el-option>
            <el-option label="成功提示" value="success">
              <el-tag type="success" size="small">成功提示</el-tag>
            </el-option>
            <el-option label="警告信息" value="warning">
              <el-tag type="warning" size="small">警告信息</el-tag>
            </el-option>
            <el-option label="重要通知" value="error">
              <el-tag type="danger" size="small">重要通知</el-tag>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="优先级" prop="priority">
          <el-input-number v-model="form.priority" :min="0" :max="100" />
          <span class="form-tip">数值越大越靠前，≥10 为置顶</span>
        </el-form-item>
        
        <el-form-item label="内容" prop="content">
          <el-input 
            v-model="form.content" 
            type="textarea" 
            :rows="6" 
            placeholder="请输入公告内容"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit(false)" :loading="submitting">
          保存为草稿
        </el-button>
        <el-button type="success" @click="handleSubmit(true)" :loading="submitting">
          保存并发布
        </el-button>
      </template>
    </el-dialog>

    <!-- 预览弹窗 -->
    <el-dialog v-model="previewVisible" title="公告预览" width="500px">
      <el-alert 
        v-if="previewData"
        :title="previewData.title" 
        :type="previewData.type" 
        :closable="false"
        show-icon
      >
        <template #default>
          <div class="preview-content">{{ previewData.content }}</div>
        </template>
      </el-alert>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Promotion, Download } from '@element-plus/icons-vue'
import { 
  getAnnouncements, 
  createAnnouncement, 
  updateAnnouncement, 
  publishAnnouncement, 
  archiveAnnouncement,
  deleteAnnouncement 
} from '@/services/announcement'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const previewVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const filterStatus = ref('')
const formRef = ref(null)
const previewData = ref(null)

const announcements = ref([])
const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0
})

const form = reactive({
  title: '',
  content: '',
  type: 'info',
  priority: 0
})

const rules = {
  title: [{ required: true, message: '请输入公告标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入公告内容', trigger: 'blur' }]
}

// 获取公告列表
const fetchAnnouncements = async () => {
  loading.value = true
  try {
    const res = await getAnnouncements({
      page: pagination.page,
      per_page: pagination.per_page,
      status: filterStatus.value || undefined
    })
    if (res.status === 1) {
      announcements.value = res.data.items
      pagination.total = res.data.total
    }
  } catch (error) {
    console.error('获取公告失败:', error)
    ElMessage.error('获取公告列表失败')
  } finally {
    loading.value = false
  }
}

// 新建公告
const handleCreate = () => {
  isEdit.value = false
  editingId.value = null
  form.title = ''
  form.content = ''
  form.type = 'info'
  form.priority = 0
  dialogVisible.value = true
}

// 编辑公告
const handleEdit = (row) => {
  isEdit.value = true
  editingId.value = row.id
  form.title = row.title
  form.content = row.content
  form.type = row.type
  form.priority = row.priority
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async (publish = false) => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      const data = {
        title: form.title,
        content: form.content,
        type: form.type,
        priority: form.priority,
        status: publish ? 'published' : 'draft'
      }
      
      let res
      if (isEdit.value) {
        res = await updateAnnouncement(editingId.value, data)
        if (res.status === 1 && publish) {
          await publishAnnouncement(editingId.value)
        }
      } else {
        res = await createAnnouncement(data)
      }
      
      if (res.status === 1) {
        ElMessage.success(publish ? '公告已发布' : '公告已保存')
        dialogVisible.value = false
        fetchAnnouncements()
      } else {
        ElMessage.error(res.error || '操作失败')
      }
    } catch (error) {
      console.error('保存公告失败:', error)
      ElMessage.error('保存失败')
    } finally {
      submitting.value = false
    }
  })
}

// 发布公告
const handlePublish = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要发布公告"${row.title}"吗？`, '确认发布', { type: 'info' })
    
    const res = await publishAnnouncement(row.id)
    if (res.status === 1) {
      ElMessage.success('公告已发布')
      fetchAnnouncements()
    } else {
      ElMessage.error(res.error || '发布失败')
    }
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

// 下架公告
const handleArchive = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要下架公告"${row.title}"吗？`, '确认下架', { type: 'warning' })
    
    const res = await archiveAnnouncement(row.id)
    if (res.status === 1) {
      ElMessage.success('公告已下架')
      fetchAnnouncements()
    } else {
      ElMessage.error(res.error || '下架失败')
    }
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

// 删除公告
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除公告"${row.title}"吗？此操作不可撤销。`, '确认删除', { type: 'error' })
    
    const res = await deleteAnnouncement(row.id)
    if (res.status === 1) {
      ElMessage.success('公告已删除')
      fetchAnnouncements()
    } else {
      ElMessage.error(res.error || '删除失败')
    }
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

// 分页
const handleSizeChange = (size) => {
  pagination.per_page = size
  pagination.page = 1
  fetchAnnouncements()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchAnnouncements()
}

// 获取类型名称
const getTypeName = (type) => {
  const names = { info: '普通', success: '成功', warning: '警告', error: '重要' }
  return names[type] || type
}

// 获取状态名称
const getStatusName = (status) => {
  const names = { draft: '草稿', published: '已发布', archived: '已下架' }
  return names[status] || status
}

// 获取状态标签类型
const getStatusType = (status) => {
  const types = { draft: 'info', published: 'success', archived: 'warning' }
  return types[status] || 'info'
}

onMounted(() => {
  fetchAnnouncements()
})
</script>

<style scoped>
.announcement-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 70px);
}

.action-card {
  margin-bottom: 20px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.form-tip {
  margin-left: 15px;
  color: #909399;
  font-size: 12px;
}

.preview-content {
  margin-top: 10px;
  white-space: pre-wrap;
  line-height: 1.6;
}
</style>
