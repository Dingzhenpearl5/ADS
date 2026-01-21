<template>
  <div class="user-manage-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>用户管理</h2>
      <p>管理系统医生账号</p>
    </div>

    <!-- 搜索和操作栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="关键词">
          <el-input
            v-model="filters.keyword"
            placeholder="用户名/姓名"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="filters.role" placeholder="全部" clearable style="width: 120px">
            <el-option label="医生" value="doctor" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width: 120px">
            <el-option label="正常" value="active" />
            <el-option label="已禁用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="RefreshRight" @click="handleReset">重置</el-button>
        </el-form-item>
        <el-form-item style="float: right">
          <el-button type="primary" :icon="Plus" @click="handleCreate">新建用户</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 用户列表 -->
    <el-card class="table-card" shadow="never">
      <el-table :data="users" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="name" label="姓名" width="150" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'">
              {{ row.role === 'admin' ? '管理员' : '医生' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '正常' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="诊断权限" min-width="200">
          <template #default="{ row }">
            <template v-if="row.role === 'admin'">
              <el-tag type="danger" size="small">全部权限</el-tag>
            </template>
            <template v-else>
              <el-tag 
                v-for="perm in (row.permissions || [])" 
                :key="perm"
                type="primary"
                size="small"
                style="margin-right: 4px; margin-bottom: 4px;"
              >
                {{ permissionLabels[perm] || perm }}
              </el-tag>
              <el-tag v-if="!row.permissions || row.permissions.length === 0" type="info" size="small">
                无权限
              </el-tag>
            </template>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              link 
              size="small" 
              @click="handleEdit(row)"
              :disabled="row.role === 'admin'"
            >
              编辑
            </el-button>
            <el-button 
              :type="row.status === 'active' ? 'warning' : 'success'"
              link 
              size="small" 
              @click="handleToggleStatus(row)"
              :disabled="row.role === 'admin'"
            >
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
            <el-button 
              type="info" 
              link 
              size="small" 
              @click="handleResetPassword(row)"
              :disabled="row.role === 'admin'"
            >
              重置密码
            </el-button>
            <el-popconfirm
              title="确定要删除该用户吗？"
              @confirm="handleDelete(row)"
              :disabled="row.role === 'admin'"
            >
              <template #reference>
                <el-button 
                  type="danger" 
                  link 
                  size="small"
                  :disabled="row.role === 'admin'"
                >
                  删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
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

    <!-- 创建/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'create' ? '新建用户' : '编辑用户'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="form.username" 
            placeholder="请输入用户名"
            :disabled="dialogType === 'edit'"
          />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="医生" value="doctor" />
          </el-select>
        </el-form-item>
        <el-form-item label="诊断权限" prop="permissions">
          <el-checkbox-group v-model="form.permissions">
            <el-checkbox label="rectum">直肠诊断</el-checkbox>
            <el-checkbox label="lung">肺部诊断</el-checkbox>
            <el-checkbox label="liver">肝脏诊断</el-checkbox>
            <el-checkbox label="brain">脑部诊断</el-checkbox>
            <el-checkbox label="breast">乳腺诊断</el-checkbox>
            <el-checkbox label="stomach">胃部诊断</el-checkbox>
          </el-checkbox-group>
          <div class="permission-tip">
            <el-text type="info" size="small">勾选医生可访问的诊断工作区</el-text>
          </div>
        </el-form-item>
        <el-form-item v-if="dialogType === 'create'" label="密码" prop="password">
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item v-if="dialogType === 'edit'" label="新密码">
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="留空则不修改密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog
      v-model="resetPasswordVisible"
      title="重置密码"
      width="400px"
    >
      <el-form :model="resetForm" label-width="80px">
        <el-form-item label="新密码">
          <el-input 
            v-model="resetForm.password" 
            type="password" 
            placeholder="请输入新密码，默认为 123456"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetPasswordVisible = false">取消</el-button>
        <el-button type="primary" :loading="resetting" @click="confirmResetPassword">
          确定重置
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, RefreshRight, Plus } from '@element-plus/icons-vue'
import request from '../../../services/request'

// 权限标签映射
const permissionLabels = {
  rectum: '直肠',
  lung: '肺部',
  liver: '肝脏',
  brain: '脑部',
  breast: '乳腺',
  stomach: '胃部'
}

// 筛选条件
const filters = reactive({
  keyword: '',
  role: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

// 数据
const users = ref([])
const loading = ref(false)

// 对话框
const dialogVisible = ref(false)
const dialogType = ref('create')
const submitting = ref(false)
const formRef = ref(null)

// 表单
const form = reactive({
  id: null,
  username: '',
  name: '',
  role: 'doctor',
  password: '',
  permissions: ['rectum'] // 默认有直肠诊断权限
})

// 表单验证
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
  ]
}

// 重置密码
const resetPasswordVisible = ref(false)
const resetForm = reactive({
  userId: null,
  password: ''
})
const resetting = ref(false)

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      ...filters
    }
    Object.keys(params).forEach(key => {
      if (params[key] === '') delete params[key]
    })
    
    const res = await request.get('/api/users', { params })
    if (res.status === 1) {
      users.value = res.data.list
      pagination.total = res.data.total
    } else {
      ElMessage.error(res.error || '获取用户列表失败')
    }
  } catch (error) {
    ElMessage.error('获取用户列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchUsers()
}

// 重置
const handleReset = () => {
  filters.keyword = ''
  filters.role = ''
  filters.status = ''
  pagination.page = 1
  fetchUsers()
}

// 分页
const handleSizeChange = (size) => {
  pagination.per_page = size
  pagination.page = 1
  fetchUsers()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchUsers()
}

// 新建用户
const handleCreate = () => {
  dialogType.value = 'create'
  form.id = null
  form.username = ''
  form.name = ''
  form.role = 'doctor'
  form.password = ''
  form.permissions = ['rectum'] // 默认权限
  dialogVisible.value = true
}

// 编辑用户
const handleEdit = (row) => {
  dialogType.value = 'edit'
  form.id = row.id
  form.username = row.username
  form.name = row.name
  form.role = row.role
  form.password = ''
  form.permissions = row.permissions || ['rectum']
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  // 编辑时密码不是必填
  if (dialogType.value === 'edit') {
    const editRules = { ...rules }
    delete editRules.password
    formRef.value.rules = editRules
  }
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (dialogType.value === 'create') {
        const res = await request.post('/api/users', {
          username: form.username,
          name: form.name,
          role: form.role,
          password: form.password,
          permissions: form.permissions
        })
        if (res.status === 1) {
          ElMessage.success('用户创建成功')
          dialogVisible.value = false
          fetchUsers()
        } else {
          ElMessage.error(res.error || '创建失败')
        }
      } else {
        const data = {
          name: form.name,
          role: form.role,
          permissions: form.permissions
        }
        if (form.password) {
          data.password = form.password
        }
        const res = await request.put(`/api/users/${form.id}`, data)
        if (res.status === 1) {
          ElMessage.success('用户更新成功')
          dialogVisible.value = false
          fetchUsers()
        } else {
          ElMessage.error(res.error || '更新失败')
        }
      }
    } catch (error) {
      ElMessage.error('操作失败')
      console.error(error)
    } finally {
      submitting.value = false
    }
  })
}

// 切换状态
const handleToggleStatus = async (row) => {
  const newStatus = row.status === 'active' ? 'disabled' : 'active'
  const actionText = newStatus === 'disabled' ? '禁用' : '启用'
  
  try {
    const res = await request.put(`/api/users/${row.id}/status`, { status: newStatus })
    if (res.status === 1) {
      ElMessage.success(`用户已${actionText}`)
      fetchUsers()
    } else {
      ElMessage.error(res.error || `${actionText}失败`)
    }
  } catch (error) {
    ElMessage.error(`${actionText}失败`)
    console.error(error)
  }
}

// 重置密码
const handleResetPassword = (row) => {
  resetForm.userId = row.id
  resetForm.password = ''
  resetPasswordVisible.value = true
}

const confirmResetPassword = async () => {
  resetting.value = true
  try {
    const res = await request.post(`/api/users/${resetForm.userId}/reset-password`, {
      password: resetForm.password || '123456'
    })
    if (res.status === 1) {
      ElMessage.success('密码重置成功')
      resetPasswordVisible.value = false
    } else {
      ElMessage.error(res.error || '重置失败')
    }
  } catch (error) {
    ElMessage.error('重置失败')
    console.error(error)
  } finally {
    resetting.value = false
  }
}

// 删除用户
const handleDelete = async (row) => {
  try {
    const res = await request.delete(`/api/users/${row.id}`)
    if (res.status === 1) {
      ElMessage.success('用户删除成功')
      fetchUsers()
    } else {
      ElMessage.error(res.error || '删除失败')
    }
  } catch (error) {
    ElMessage.error('删除失败')
    console.error(error)
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-manage-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.filter-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.table-card {
  border-radius: 8px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.permission-tip {
  margin-top: 4px;
}
</style>
