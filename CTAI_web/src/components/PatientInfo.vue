<template>
  <div class="patient-info">
    <div class="custom-card">
      <div class="section-title">
        <el-icon><User /></el-icon>
        <span>患者信息</span>
      </div>
      
      <div class="search-box">
        <el-input 
          v-model="searchId" 
          placeholder="输入患者ID搜索" 
          @keyup.enter="handleSearch"
          class="custom-input"
        >
          <template #append>
            <el-button :icon="Search" @click="handleSearch" />
          </template>
        </el-input>
      </div>

      <div class="info-list">
        <div v-for="(value, name) in patient" :key="name" class="info-item">
          <span class="label">{{ name }}:</span>
          <span class="value">{{ value }}</span>
        </div>
        <el-empty v-if="!Object.keys(patient).length" description="暂无患者数据" :image-size="60" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Search, User } from '@element-plus/icons-vue'

defineProps({
  patient: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['search'])
const searchId = ref('')

const handleSearch = () => {
  if (!searchId.value.trim()) return
  emit('search', searchId.value)
}
</script>

<style scoped>
.patient-info {
  height: 100%;
}

.search-box {
  margin-bottom: 20px;
}

.custom-input :deep(.el-input__wrapper) {
  border-radius: 8px 0 0 8px;
}

.custom-input :deep(.el-input-group__append) {
  border-radius: 0 8px 8px 0;
  background-color: var(--primary-color);
  color: white;
  border: none;
}

.custom-input :deep(.el-input-group__append .el-button) {
  color: white;
  margin: -5px -20px;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 12px;
  background-color: #f8fafc;
  border-radius: 6px;
  transition: all 0.2s;
}

.info-item:hover {
  background-color: #f1f5f9;
  transform: translateX(4px);
}

.label {
  color: #64748b;
  font-size: 13px;
}

.value {
  color: #1e293b;
  font-weight: 600;
  font-size: 14px;
}
</style>
