<template>
  <div class="help-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><QuestionFilled /></el-icon>
        使用帮助
      </h1>
      <p class="page-subtitle">了解如何使用直肠肿瘤辅助诊断系统进行 CT 影像分析</p>
    </div>

    <!-- 流程概览 -->
    <el-card class="overview-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Guide /></el-icon>
          <span>诊断流程概览</span>
        </div>
      </template>
      
      <div class="flow-overview">
        <div class="flow-step-overview">
          <div class="step-circle">1</div>
          <div class="step-label">上传CT图像</div>
        </div>
        <el-icon class="flow-connector"><ArrowRight /></el-icon>
        <div class="flow-step-overview">
          <div class="step-circle">2</div>
          <div class="step-label">AI智能诊断</div>
        </div>
        <el-icon class="flow-connector"><ArrowRight /></el-icon>
        <div class="flow-step-overview">
          <div class="step-circle">3</div>
          <div class="step-label">数据分析</div>
        </div>
        <el-icon class="flow-connector"><ArrowRight /></el-icon>
        <div class="flow-step-overview">
          <div class="step-circle">4</div>
          <div class="step-label">生成报告</div>
        </div>
      </div>
    </el-card>

    <!-- 详细步骤 -->
    <el-timeline class="help-timeline">
      <!-- 步骤1：上传CT图像 -->
      <el-timeline-item
        :timestamp="'第一步'"
        placement="top"
        type="primary"
        :hollow="true"
        size="large"
      >
        <el-card class="step-card" shadow="hover">
          <template #header>
            <div class="step-header">
              <el-icon :size="24" color="#409eff"><Upload /></el-icon>
              <h3>上传CT图像</h3>
            </div>
          </template>
          
          <div class="step-content">
            <div class="step-description">
              <p>首先，您需要将患者的CT影像文件上传到系统中。系统支持标准的DICOM格式（.dcm）文件。</p>
            </div>
            
            <el-divider content-position="left">操作步骤</el-divider>
            
            <div class="instruction-list">
              <div class="instruction-item">
                <el-icon color="#67c23a"><CircleCheck /></el-icon>
                <span>点击导航栏中的 <el-tag size="small">工作台</el-tag> 进入诊断界面</span>
              </div>
              <div class="instruction-item">
                <el-icon color="#67c23a"><CircleCheck /></el-icon>
                <span>选择 <el-tag size="small" type="info">直肠诊断</el-tag> 诊断类型</span>
              </div>
              <div class="instruction-item">
                <el-icon color="#67c23a"><CircleCheck /></el-icon>
                <span>点击上传区域或将 .dcm 文件拖拽到上传框中</span>
              </div>
              <div class="instruction-item">
                <el-icon color="#67c23a"><CircleCheck /></el-icon>
                <span>系统会自动解析并显示CT图像预览</span>
              </div>
            </div>

            <el-alert
              type="info"
              :closable="false"
              show-icon
              class="tip-alert"
            >
              <template #title>
                <strong>文件要求</strong>
              </template>
              <ul class="tip-list">
                <li>仅支持 DICOM 格式（.dcm）的CT影像文件</li>
                <li>文件大小限制：最大 50MB</li>
                <li>建议上传高质量的腹部CT扫描图像</li>
              </ul>
            </el-alert>
          </div>
        </el-card>
      </el-timeline-item>

      <!-- 步骤2：AI智能诊断 -->
      <el-timeline-item
        :timestamp="'第二步'"
        placement="top"
        type="success"
        :hollow="true"
        size="large"
      >
        <el-card class="step-card" shadow="hover">
          <template #header>
            <div class="step-header">
              <el-icon :size="24" color="#67c23a"><Cpu /></el-icon>
              <h3>AI智能诊断</h3>
            </div>
          </template>
          
          <div class="step-content">
            <div class="step-description">
              <p>上传图像后，点击"开始诊断"按钮，系统将使用先进的 <strong>Transformer + UNet 融合模型</strong> 对CT图像进行智能分析。</p>
            </div>
            
            <el-divider content-position="left">AI处理流程</el-divider>
            
            <div class="ai-process">
              <div class="process-item">
                <div class="process-icon">
                  <el-icon :size="20"><Picture /></el-icon>
                </div>
                <div class="process-info">
                  <h4>图像预处理</h4>
                  <p>自动对CT图像进行去噪、增强对比度、标准化等预处理操作</p>
                </div>
              </div>
              
              <div class="process-item">
                <div class="process-icon">
                  <el-icon :size="20"><Aim /></el-icon>
                </div>
                <div class="process-info">
                  <h4>肿瘤定位</h4>
                  <p>Transformer注意力机制捕获全局上下文，精准定位肿瘤区域</p>
                </div>
              </div>
              
              <div class="process-item">
                <div class="process-icon">
                  <el-icon :size="20"><Select /></el-icon>
                </div>
                <div class="process-info">
                  <h4>边界分割</h4>
                  <p>UNet编码-解码架构精细化分割肿瘤边界，生成精确的分割掩码</p>
                </div>
              </div>
              
              <div class="process-item">
                <div class="process-icon">
                  <el-icon :size="20"><DataAnalysis /></el-icon>
                </div>
                <div class="process-info">
                  <h4>特征提取</h4>
                  <p>自动计算肿瘤的形态学特征（面积、周长、圆度等）</p>
                </div>
              </div>
            </div>

            <el-alert
              type="success"
              :closable="false"
              show-icon
              class="tip-alert"
            >
              <template #title>
                <strong>模型优势</strong>
              </template>
              <ul class="tip-list">
                <li>融合 Transformer 全局建模能力与 UNet 精细分割能力</li>
                <li>对直肠肿瘤边界识别准确率达 94.5%</li>
                <li>单次诊断仅需 2-3 分钟，实时反馈结果</li>
              </ul>
            </el-alert>
          </div>
        </el-card>
      </el-timeline-item>

      <!-- 步骤3：数据分析 -->
      <el-timeline-item
        :timestamp="'第三步'"
        placement="top"
        type="warning"
        :hollow="true"
        size="large"
      >
        <el-card class="step-card" shadow="hover">
          <template #header>
            <div class="step-header">
              <el-icon :size="24" color="#e6a23c"><TrendCharts /></el-icon>
              <h3>数据分析与总结</h3>
            </div>
          </template>
          
          <div class="step-content">
            <div class="step-description">
              <p>AI诊断完成后，系统会自动提取并展示详细的肿瘤特征数据，帮助医生进行深入分析。</p>
            </div>
            
            <el-divider content-position="left">分析指标说明</el-divider>
            
            <el-table :data="featureData" style="width: 100%" stripe>
              <el-table-column prop="name" label="指标名称" width="140" />
              <el-table-column prop="description" label="说明" />
              <el-table-column prop="unit" label="单位" width="100" />
            </el-table>

            <el-divider content-position="left">可视化展示</el-divider>
            
            <div class="visualization-intro">
              <div class="vis-item">
                <el-icon :size="32" color="#409eff"><PictureFilled /></el-icon>
                <div class="vis-info">
                  <h4>原始CT图像</h4>
                  <p>显示上传的原始CT扫描图像</p>
                </div>
              </div>
              <div class="vis-item">
                <el-icon :size="32" color="#67c23a"><Brush /></el-icon>
                <div class="vis-info">
                  <h4>分割结果图</h4>
                  <p>在原图上标注肿瘤区域轮廓（绿色边界线）</p>
                </div>
              </div>
              <div class="vis-item">
                <el-icon :size="32" color="#e6a23c"><Histogram /></el-icon>
                <div class="vis-info">
                  <h4>特征数据表</h4>
                  <p>以表格形式展示所有提取的量化特征</p>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-timeline-item>

      <!-- 步骤4：生成报告 -->
      <el-timeline-item
        :timestamp="'第四步'"
        placement="top"
        type="danger"
        :hollow="true"
        size="large"
      >
        <el-card class="step-card" shadow="hover">
          <template #header>
            <div class="step-header">
              <el-icon :size="24" color="#f56c6c"><Document /></el-icon>
              <h3>得出结果与报告</h3>
            </div>
          </template>
          
          <div class="step-content">
            <div class="step-description">
              <p>根据AI分析结果和特征数据，系统会生成诊断报告，供医生参考和存档。</p>
            </div>
            
            <el-divider content-position="left">结果解读</el-divider>
            
            <div class="result-guide">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="肿瘤定位">
                  分割结果图中绿色轮廓标注的区域即为AI识别的肿瘤位置
                </el-descriptions-item>
                <el-descriptions-item label="肿瘤大小">
                  通过面积和等效直径指标评估肿瘤的实际大小
                </el-descriptions-item>
                <el-descriptions-item label="形态特征">
                  圆度、紧凑度、偏心率等指标反映肿瘤的形态规则程度
                </el-descriptions-item>
                <el-descriptions-item label="诊断建议">
                  结合特征数据，医生可做出专业判断并给出诊疗建议
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <el-divider content-position="left">后续操作</el-divider>
            
            <div class="action-list">
              <div class="action-item">
                <el-button type="primary" :icon="Printer" plain>打印报告</el-button>
                <span>将诊断结果打印为纸质报告</span>
              </div>
              <div class="action-item">
                <el-button type="success" :icon="Download" plain>导出数据</el-button>
                <span>导出特征数据为Excel或PDF格式</span>
              </div>
              <div class="action-item">
                <el-button type="info" :icon="FolderOpened" plain>保存记录</el-button>
                <span>诊断结果会自动保存到历史记录中</span>
              </div>
            </div>

            <el-alert
              type="warning"
              :closable="false"
              show-icon
              class="tip-alert"
            >
              <template #title>
                <strong>重要提示</strong>
              </template>
              <p>本系统提供的诊断结果仅供参考，最终诊断需由专业医生根据临床情况综合判断。AI辅助诊断不能替代医生的专业判断。</p>
            </el-alert>
          </div>
        </el-card>
      </el-timeline-item>
    </el-timeline>

    <!-- 快速开始按钮 -->
    <div class="quick-start">
      <el-button type="primary" size="large" :icon="VideoPlay" @click="goToWorkspace">
        立即开始诊断
      </el-button>
      <el-button size="large" :icon="Timer" @click="goToHistory">
        查看历史记录
      </el-button>
    </div>

    <!-- 常见问题 -->
    <el-card class="faq-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><ChatLineSquare /></el-icon>
          <span>常见问题</span>
        </div>
      </template>
      
      <el-collapse accordion>
        <el-collapse-item title="Q: 系统支持哪些格式的CT图像？" name="1">
          <p>目前系统仅支持 DICOM 格式（.dcm）的CT影像文件。这是医学影像领域的标准格式，大多数CT设备导出的图像都是此格式。</p>
        </el-collapse-item>
        <el-collapse-item title="Q: 诊断结果的准确率如何？" name="2">
          <p>我们的 Transformer+UNet 融合模型在直肠肿瘤分割任务上达到了 94.5% 的准确率。但请注意，AI诊断结果仅供参考，最终诊断需由专业医生做出。</p>
        </el-collapse-item>
        <el-collapse-item title="Q: 一次诊断需要多长时间？" name="3">
          <p>从上传图像到生成完整的诊断结果，通常需要 2-3 分钟。具体时间可能因图像大小和服务器负载而略有不同。</p>
        </el-collapse-item>
        <el-collapse-item title="Q: 诊断记录会保存多久？" name="4">
          <p>所有诊断记录会永久保存在系统数据库中，您可以随时在"历史记录"页面查看和管理历史诊断数据。</p>
        </el-collapse-item>
        <el-collapse-item title="Q: 如何保护患者隐私？" name="5">
          <p>系统采用严格的数据安全措施，所有患者数据都经过加密存储。同时，系统仅供授权医护人员使用，需要登录验证才能访问。</p>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  QuestionFilled, Guide, ArrowRight, Upload, Cpu, TrendCharts, Document,
  CircleCheck, Picture, Aim, Select, DataAnalysis, PictureFilled, Brush,
  Histogram, Printer, Download, FolderOpened, VideoPlay, Timer, ChatLineSquare
} from '@element-plus/icons-vue'

const router = useRouter()

// 特征指标数据
const featureData = ref([
  { name: '面积', description: '肿瘤区域的像素面积，反映肿瘤大小', unit: '像素²' },
  { name: '周长', description: '肿瘤轮廓的总长度', unit: '像素' },
  { name: '圆度', description: '形状接近圆形的程度，值越接近1越圆', unit: '无' },
  { name: '紧凑度', description: '形状的紧凑程度，反映边界复杂度', unit: '无' },
  { name: '偏心率', description: '形状的偏心程度，椭圆形态的长短轴比', unit: '无' },
  { name: '等效直径', description: '与肿瘤面积相同的圆的直径', unit: '像素' },
  { name: '主轴长度', description: '拟合椭圆的长轴长度', unit: '像素' },
  { name: '次轴长度', description: '拟合椭圆的短轴长度', unit: '像素' },
])

const goToWorkspace = () => {
  router.push('/workspace')
}

const goToHistory = () => {
  router.push('/history')
}
</script>

<style scoped>
.help-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  background: linear-gradient(135deg, #f5f8fc 0%, #e3f2fd 100%);
  min-height: calc(100vh - 70px);
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 16px;
  color: #909399;
  margin: 0;
}

/* 流程概览卡片 */
.overview-card {
  margin-bottom: 32px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.flow-overview {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 20px 0;
}

.flow-step-overview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.step-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff 0%, #1890ff 100%);
  color: #fff;
  font-size: 24px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.step-label {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.flow-connector {
  font-size: 24px;
  color: #c0c4cc;
}

/* 时间线样式 */
.help-timeline {
  padding: 0 20px;
}

.step-card {
  border-radius: 12px;
  margin-bottom: 8px;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.step-content {
  padding: 8px 0;
}

.step-description {
  font-size: 15px;
  line-height: 1.8;
  color: #606266;
}

/* 指令列表 */
.instruction-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.instruction-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 8px;
  font-size: 14px;
}

/* 提示框 */
.tip-alert {
  margin-top: 16px;
}

.tip-list {
  margin: 8px 0 0 0;
  padding-left: 20px;
}

.tip-list li {
  margin: 4px 0;
  font-size: 13px;
}

/* AI处理流程 */
.ai-process {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.process-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 10px;
  transition: all 0.3s;
}

.process-item:hover {
  background: #e8f4ff;
  transform: translateX(4px);
}

.process-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #409eff 0%, #1890ff 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.process-info h4 {
  margin: 0 0 4px 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.process-info p {
  margin: 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}

/* 可视化介绍 */
.visualization-intro {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.vis-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 12px;
  text-align: center;
}

.vis-info h4 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.vis-info p {
  margin: 4px 0 0 0;
  font-size: 13px;
  color: #909399;
}

/* 结果指南 */
.result-guide {
  margin-bottom: 16px;
}

/* 操作列表 */
.action-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.action-item span {
  font-size: 14px;
  color: #606266;
}

/* 快速开始 */
.quick-start {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin: 40px 0;
}

/* FAQ卡片 */
.faq-card {
  border-radius: 12px;
}

.faq-card :deep(.el-collapse-item__header) {
  font-weight: 500;
  font-size: 15px;
}

.faq-card :deep(.el-collapse-item__content) {
  font-size: 14px;
  line-height: 1.8;
  color: #606266;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .flow-overview {
    flex-wrap: wrap;
  }
  
  .ai-process {
    grid-template-columns: 1fr;
  }
  
  .visualization-intro {
    grid-template-columns: 1fr;
  }
  
  .quick-start {
    flex-direction: column;
    align-items: center;
  }
}
</style>
