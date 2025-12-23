<template>
  <div class="patient-info">
    <el-card class="box-card" style="width:250px;height:auto">
      <template #header>
        <div class="clearfix">
          <span>病人信息</span>
        </div>
      </template>
      
      <div style="margin-bottom: 15px; display: flex;">
        <el-input 
          v-model="searchId" 
          placeholder="输入ID搜索" 
          size="small" 
          style="margin-right: 5px;"
          @keyup.enter="handleSearch"
        ></el-input>
        <el-button type="primary" :icon="Search" circle size="small" @click="handleSearch"></el-button>
      </div>

      <div v-for="(value, name) in patient" :key="name" class="text item">
        <h3 style="font-weight:normal;">{{ name }}: {{ value }}</h3>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'

defineProps({
  patient: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['search'])
const searchId = ref('')

const handleSearch = () => {
  emit('search', searchId.value)
}
</script>

<style scoped>
.text {
  font-size: 14px;
}
.item {
  margin-bottom: 10px;
}
</style>
