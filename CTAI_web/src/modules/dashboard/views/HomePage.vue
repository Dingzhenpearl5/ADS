<template>
  <div class="home-page">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="banner-content">
        <div class="welcome-text">
          <h1 class="greeting">你好，{{ userName }}！</h1>
          <p class="date-info">{{ currentDate }} {{ currentTime }}</p>
          <p class="tip">今天也要元气满满地工作哦 💪</p>
        </div>
        <div class="quick-actions">
          <el-button type="primary" size="large" :icon="VideoPlay" @click="goToWorkspace">
            开始诊断
          </el-button>
          <el-button size="large" :icon="Document" @click="goToHistory">
            历史记录
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
            <el-icon :size="32"><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ totalDiagnosis }}</div>
            <div class="stat-label">累计诊断</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
            <el-icon :size="32"><Calendar /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ todayDiagnosis }}</div>
            <div class="stat-label">今日诊断</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%)">
            <el-icon :size="32"><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ accuracy }}%</div>
            <div class="stat-label">平均准确率</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, #30cfd0 0%, #330867 100%)">
            <el-icon :size="32"><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ avgTime }}分钟</div>
            <div class="stat-label">平均用时</div>
          </div>
        </div>
      </el-card>
    </div>

    <el-row :gutter="20">
      <!-- 左侧：系统介绍 + AI能力 -->
      <el-col :xl="16" :lg="16" :md="24" :sm="24">
        <!-- 系统介绍 -->
        <el-card class="intro-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Notebook /></el-icon>
              <span>系统介绍</span>
            </div>
          </template>
          
          <div class="intro-content">
            <h3>肿瘤辅助诊断系统 (CTAI System)</h3>
            <p class="intro-text">
              本系统是一款基于深度学习的智能医学影像辅助诊断平台，专注于肿瘤的早期筛查、精准定位和智能分析。
              通过整合先进的人工智能算法和医学影像处理技术，为医生提供快速、准确的诊断参考。
            </p>

            <div class="features-grid">
              <div class="feature-item">
                <div class="feature-icon">🎯</div>
                <h4>精准定位</h4>
                <p>AI自动识别病灶区域，精确标注肿瘤边界</p>
              </div>
              <div class="feature-item">
                <div class="feature-icon">⚡</div>
                <h4>快速分析</h4>
                <p>2-5分钟完成影像分析，大幅提升诊断效率</p>
              </div>
              <div class="feature-item">
                <div class="feature-icon">📊</div>
                <h4>量化评估</h4>
                <p>提供面积、周长等量化指标，辅助判断</p>
              </div>
              <div class="feature-item">
                <div class="feature-icon">🔬</div>
                <h4>多部位支持</h4>
                <p>支持直肠、肺部、肝脏等多个部位诊断</p>
              </div>
            </div>
          </div>
        </el-card>

        <!-- AI能力展示 -->
        <el-card class="ai-capability-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Cpu /></el-icon>
              <span>AI 智能辅助诊断</span>
            </div>
          </template>

          <div class="ai-content">
            <div class="ai-flow">
              <div class="flow-step">
                <div class="step-number">1</div>
                <div class="step-content">
                  <h4>图像预处理</h4>
                  <p>自动去噪、增强对比度、标准化尺寸</p>
                </div>
              </div>
              <el-icon class="flow-arrow"><ArrowRight /></el-icon>

              <div class="flow-step">
                <div class="step-number">2</div>
                <div class="step-content">
                  <h4>病灶检测</h4>
                  <p>U-Net深度学习模型识别异常区域</p>
                </div>
              </div>
              <el-icon class="flow-arrow"><ArrowRight /></el-icon>

              <div class="flow-step">
                <div class="step-number">3</div>
                <div class="step-content">
                  <h4>特征提取</h4>
                  <p>计算形态学、纹理等多维度特征</p>
                </div>
              </div>
              <el-icon class="flow-arrow"><ArrowRight /></el-icon>

              <div class="flow-step">
                <div class="step-number">4</div>
                <div class="step-content">
                  <h4>结果生成</h4>
                  <p>可视化标注、量化报告、诊断建议</p>
                </div>
              </div>
            </div>

            <div class="ai-highlights">
              <el-alert
                type="success"
                :closable="false"
                show-icon
              >
                <template #title>
                  <span style="font-weight: 600;">AI 核心优势</span>
                </template>
                <div class="highlights-list">
                  <div class="highlight-item">
                    <el-icon color="#67c23a"><Select /></el-icon>
                    <span><strong>高准确率：</strong>平均诊断准确率达 92%+，部分部位可达 95%</span>
                  </div>
                  <div class="highlight-item">
                    <el-icon color="#67c23a"><Select /></el-icon>
                    <span><strong>快速响应：</strong>单次诊断仅需 2-5 分钟，大幅缩短等待时间</span>
                  </div>
                  <div class="highlight-item">
                    <el-icon color="#67c23a"><Select /></el-icon>
                    <span><strong>客观量化：</strong>提供精确的量化指标，减少主观判断误差</span>
                  </div>
                  <div class="highlight-item">
                    <el-icon color="#67c23a"><Select /></el-icon>
                    <span><strong>持续学习：</strong>模型定期更新，诊断能力不断提升</span>
                  </div>
                </div>
              </el-alert>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：快捷入口 + 最近记录 -->
      <el-col :xl="8" :lg="8" :md="24" :sm="24">
        <!-- 快捷入口 -->
        <el-card class="shortcuts-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Grid /></el-icon>
              <span>快捷入口</span>
            </div>
          </template>

          <div class="shortcuts-grid">
            <div class="shortcut-item" @click="goToWorkspace">
              <div class="shortcut-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
                <el-icon :size="28"><VideoPlay /></el-icon>
              </div>
              <span>开始诊断</span>
            </div>

            <div class="shortcut-item" @click="goToHistory">
              <div class="shortcut-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
                <el-icon :size="28"><Document /></el-icon>
              </div>
              <span>历史记录</span>
            </div>

            <div class="shortcut-item" @click="goToStatistics">
              <div class="shortcut-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%)">
                <el-icon :size="28"><DataAnalysis /></el-icon>
              </div>
              <span>统计分析</span>
            </div>

            <div class="shortcut-item" @click="openHelp">
              <div class="shortcut-icon" style="background: linear-gradient(135deg, #30cfd0 0%, #330867 100%)">
                <el-icon :size="28"><QuestionFilled /></el-icon>
              </div>
              <span>使用帮助</span>
            </div>
          </div>
        </el-card>

        <!-- 最近诊断 -->
        <el-card class="recent-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Timer /></el-icon>
              <span>最近诊断</span>
            </div>
          </template>

          <div class="recent-list">
            <div 
              v-for="item in recentDiagnosis" 
              :key="item.id"
              class="recent-item"
              @click="viewRecord(item)"
            >
              <div class="recent-info">
                <div class="recent-title">{{ item.patientName }} - {{ item.part }}</div>
                <div class="recent-time">{{ item.time }}</div>
              </div>
              <el-tag :type="item.status === '已完成' ? 'success' : 'warning'" size="small">
                {{ item.status }}
              </el-tag>
            </div>

            <el-empty v-if="recentDiagnosis.length === 0" description="暂无诊断记录" :image-size="100" />
          </div>
        </el-card>

        <!-- 系统公告 -->
        <el-card class="notice-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Bell /></el-icon>
              <span>系统公告</span>
            </div>
          </template>

          <div class="notice-list">
            <div class="notice-item">
              <el-icon color="#409eff"><InfoFilled /></el-icon>
              <div class="notice-content">
                <div class="notice-title">系统维护通知</div>
                <div class="notice-desc">本周六凌晨 2:00-4:00 进行系统维护</div>
              </div>
            </div>
            <div class="notice-item">
              <el-icon color="#67c23a"><SuccessFilled /></el-icon>
              <div class="notice-content">
                <div class="notice-title">模型更新</div>
                <div class="notice-desc">直肠诊断模型已更新，准确率提升至 94.5%</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  VideoPlay, Document, TrendCharts, Calendar, CircleCheck, Clock,
  Notebook, Cpu, ArrowRight, Select, Grid, DataAnalysis, 
  QuestionFilled, Timer, Bell, InfoFilled, SuccessFilled
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

// 用户信息
const userName = computed(() => authStore.userInfo?.name || authStore.userInfo?.username || '用户')

// 当前日期时间
const currentDate = ref('')
const currentTime = ref('')

const updateDateTime = () => {
  const now = new Date()
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  currentDate.value = `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日 ${weekdays[now.getDay()]}`
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 统计数据
const totalDiagnosis = ref(4782)
const todayDiagnosis = ref(23)
const accuracy = ref(93.2)
const avgTime = ref(3.5)

// 最近诊断记录
const recentDiagnosis = ref([
  { id: 1, patientName: '张三', part: '直肠', time: '10分钟前', status: '已完成' },
  { id: 2, patientName: '李四', part: '肺部', time: '1小时前', status: '已完成' },
  { id: 3, patientName: '王五', part: '肝脏', time: '2小时前', status: '已完成' },
  { id: 4, patientName: '赵六', part: '直肠', time: '今天 09:30', status: '已完成' },
])

// 导航方法
const goToWorkspace = () => {
  router.push('/workspace')
}

const goToHistory = () => {
  router.push('/history')
}

const goToStatistics = () => {
  router.push('/statistics')
}

const openHelp = () => {
  ElMessage.info('使用帮助功能开发中')
}

const viewRecord = (item) => {
  ElMessage.info(`查看 ${item.patientName} 的诊断记录`)
}

onMounted(() => {
  updateDateTime()
  setInterval(updateDateTime, 60000) // 每分钟更新一次
})
</script>

<style scoped>
.home-page {
  padding: 20px;
  min-height: calc(100vh - 70px);
}

/* 欢迎横幅 */
.welcome-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 40px;
  margin-bottom: 24px;
  color: #fff;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}

.banner-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-text .greeting {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
}

.welcome-text .date-info {
  font-size: 16px;
  opacity: 0.9;
  margin: 0 0 4px 0;
}

.welcome-text .tip {
  font-size: 14px;
  opacity: 0.8;
  margin: 0;
}

.quick-actions {
  display: flex;
  gap: 12px;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

/* 卡片通用样式 */
.intro-card,
.ai-capability-card,
.shortcuts-card,
.recent-card,
.notice-card {
  border-radius: 12px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

/* 系统介绍 */
.intro-content h3 {
  font-size: 20px;
  color: #303133;
  margin: 0 0 12px 0;
}

.intro-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
  margin-bottom: 24px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.feature-item {
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  text-align: center;
  transition: all 0.3s;
}

.feature-item:hover {
  background: #f0f7ff;
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.feature-item h4 {
  font-size: 15px;
  color: #303133;
  margin: 0 0 6px 0;
}

.feature-item p {
  font-size: 13px;
  color: #606266;
  margin: 0;
  line-height: 1.5;
}

/* AI能力展示 */
.ai-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.ai-flow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.flow-step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
}

.step-content h4 {
  font-size: 15px;
  color: #303133;
  margin: 0 0 4px 0;
  text-align: center;
}

.step-content p {
  font-size: 12px;
  color: #606266;
  margin: 0;
  text-align: center;
  line-height: 1.4;
}

.flow-arrow {
  color: #dcdfe6;
  font-size: 20px;
  flex-shrink: 0;
}

.highlights-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
}

.highlight-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

/* 快捷入口 */
.shortcuts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.shortcut-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.shortcut-item:hover {
  background: #f0f7ff;
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.shortcut-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.shortcut-item span {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

/* 最近诊断 */
.recent-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.recent-item:hover {
  background: #f0f7ff;
}

.recent-info {
  flex: 1;
}

.recent-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.recent-time {
  font-size: 12px;
  color: #909399;
}

/* 系统公告 */
.notice-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.notice-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.notice-content {
  flex: 1;
}

.notice-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.notice-desc {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

/* 响应式 */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .ai-flow {
    flex-direction: column;
  }

  .flow-arrow {
    transform: rotate(90deg);
  }
}

@media (max-width: 768px) {
  .home-page {
    padding: 12px;
  }

  .welcome-banner {
    padding: 24px;
  }

  .banner-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }

  .welcome-text .greeting {
    font-size: 24px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>
