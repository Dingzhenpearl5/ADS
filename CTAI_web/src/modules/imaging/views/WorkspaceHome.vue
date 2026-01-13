<template>
  <div class="workspace-home">
    <div class="welcome-section">
      <h1 class="main-title">肿瘤辅助诊断系统</h1>
      <p class="subtitle">AI-Powered Tumor Diagnosis System</p>
      <p class="description">选择诊断部位开始智能辅助诊断</p>
    </div>

    <div class="body-parts-grid">
      <el-card
        v-for="part in bodyParts"
        :key="part.id"
        class="part-card"
        :class="{ disabled: !part.available }"
        shadow="hover"
        @click="handlePartClick(part)"
      >
        <div class="card-content">
          <div class="icon-wrapper" :style="{ background: part.color }">
            <el-icon :size="48">
              <component :is="part.icon" />
            </el-icon>
          </div>
          
          <h3 class="part-name">{{ part.name }}</h3>
          <p class="part-desc">{{ part.description }}</p>
          
          <div class="part-meta">
            <el-tag v-if="part.available" type="success" size="small">可用</el-tag>
            <el-tag v-else type="info" size="small">开发中</el-tag>
            <span class="case-count">{{ part.caseCount }} 例</span>
          </div>

          <div class="part-stats" v-if="part.available">
            <div class="stat-item">
              <span class="label">准确率</span>
              <span class="value">{{ part.accuracy }}%</span>
            </div>
            <div class="stat-item">
              <span class="label">处理时间</span>
              <span class="value">{{ part.processTime }}</span>
            </div>
          </div>

          <el-button 
            v-if="part.available"
            type="primary" 
            class="enter-btn"
            :icon="Right"
          >
            进入诊断
          </el-button>
          <el-button 
            v-else
            disabled
            class="enter-btn"
          >
            敬请期待
          </el-button>
        </div>

        <div v-if="!part.available" class="overlay">
          <el-icon class="lock-icon" :size="32"><Lock /></el-icon>
        </div>
      </el-card>
    </div>

    <div class="quick-stats-section">
      <el-card shadow="never" class="stats-card">
        <el-statistic title="累计诊断" :value="totalCases" />
      </el-card>
      <el-card shadow="never" class="stats-card">
        <el-statistic title="今日诊断" :value="todayCases" />
      </el-card>
      <el-card shadow="never" class="stats-card">
        <el-statistic title="平均准确率" :value="averageAccuracy" suffix="%" />
      </el-card>
      <el-card shadow="never" class="stats-card">
        <el-statistic title="在线医生" :value="onlineDoctors" />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Right, Lock, Medal, FirstAidKit, 
  Orange, Apple, Coffee, IceCream
} from '@element-plus/icons-vue'

const router = useRouter()

// 身体部位配置
const bodyParts = ref([
  {
    id: 'rectum',
    name: '直肠',
    description: '直肠癌症智能检测与分析',
    icon: Medal,
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    available: true,
    caseCount: 1247,
    accuracy: 94.5,
    processTime: '2-3分钟',
    route: '/diagnosis/rectum'
  },
  {
    id: 'lung',
    name: '肺部',
    description: '肺部结节检测与良恶性判断',
    icon: FirstAidKit,
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    available: false,
    caseCount: 856,
    accuracy: 92.3,
    processTime: '3-4分钟',
    route: '/diagnosis/lung'
  },
  {
    id: 'liver',
    name: '肝脏',
    description: '肝脏肿瘤检测与分级诊断',
    icon: Orange,
    color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    available: false,
    caseCount: 624,
    accuracy: 91.8,
    processTime: '2-3分钟',
    route: '/diagnosis/liver'
  },
  {
    id: 'brain',
    name: '脑部',
    description: '脑部肿瘤检测与区域定位',
    icon: Apple,
    color: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
    available: false,
    caseCount: 432,
    accuracy: 93.2,
    processTime: '4-5分钟',
    route: '/diagnosis/brain'
  },
  {
    id: 'breast',
    name: '乳腺',
    description: '乳腺癌症筛查与风险评估',
    icon: Coffee,
    color: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
    available: false,
    caseCount: 1089,
    accuracy: 95.1,
    processTime: '2-3分钟',
    route: '/diagnosis/breast'
  },
  {
    id: 'stomach',
    name: '胃部',
    description: '胃部肿瘤检测与病变分析',
    icon: IceCream,
    color: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
    available: false,
    caseCount: 534,
    accuracy: 90.7,
    processTime: '3-4分钟',
    route: '/diagnosis/stomach'
  }
])

// 统计数据
const totalCases = ref(4782)
const todayCases = ref(23)
const averageAccuracy = computed(() => {
  const sum = bodyParts.value.reduce((acc, part) => acc + part.accuracy, 0)
  return (sum / bodyParts.value.length).toFixed(1)
})
const onlineDoctors = ref(8)

const handlePartClick = (part) => {
  if (!part.available) {
    ElMessage.info(`${part.name}诊断功能正在开发中，敬请期待！`)
    return
  }
  
  router.push(part.route)
}
</script>

<style scoped>
.workspace-home {
  padding: 20px;
  min-height: calc(100vh - 70px);
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* 欢迎区域 */
.welcome-section {
  text-align: center;
  margin-bottom: 40px;
  padding: 40px 20px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.main-title {
  font-size: 36px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 12px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 16px;
  color: #909399;
  margin: 0 0 8px 0;
  letter-spacing: 2px;
}

.description {
  font-size: 14px;
  color: #606266;
  margin: 0;
}

/* 部位卡片网格 */
.body-parts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.part-card {
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.part-card:not(.disabled):hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
}

.part-card.disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.card-content {
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  z-index: 1;
}

.icon-wrapper {
  width: 100px;
  height: 100px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  color: #fff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.part-name {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 8px 0;
}

.part-desc {
  font-size: 14px;
  color: #606266;
  text-align: center;
  margin: 0 0 16px 0;
  line-height: 1.6;
}

.part-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.case-count {
  font-size: 13px;
  color: #909399;
}

.part-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  width: 100%;
  margin-bottom: 20px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-item .label {
  font-size: 12px;
  color: #909399;
}

.stat-item .value {
  font-size: 18px;
  font-weight: 700;
  color: #409eff;
}

.enter-btn {
  width: 100%;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 22px;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.lock-icon {
  color: #909399;
}

/* 快速统计 */
.quick-stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stats-card {
  border-radius: 12px;
  text-align: center;
}

.stats-card :deep(.el-statistic__head) {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stats-card :deep(.el-statistic__content) {
  font-size: 32px;
  font-weight: 700;
  color: #409eff;
}

/* 响应式 */
@media (max-width: 768px) {
  .workspace-home {
    padding: 12px;
  }

  .welcome-section {
    padding: 24px 12px;
    margin-bottom: 24px;
  }

  .main-title {
    font-size: 28px;
  }

  .body-parts-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .quick-stats-section {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
