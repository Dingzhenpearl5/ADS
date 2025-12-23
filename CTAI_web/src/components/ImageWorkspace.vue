<template>
  <div class="image-workspace">
    <div class="custom-card">
      <div class="section-title">
        <el-icon><Picture /></el-icon>
        <span>影像工作区</span>
      </div>

      <div class="image-container">
        <!-- Original Image -->
        <div class="image-box">
          <div class="image-wrapper" v-loading="loading" element-loading-text="上传中...">
            <el-image
              :src="url1"
              :preview-src-list="srcList"
              fit="contain"
              class="main-image"
            >
              <template #error>
                <div class="image-placeholder">
                  <el-icon :size="48" color="#dcdfe6"><PictureFilled /></el-icon>
                  <p v-if="!loading">等待上传图像</p>
                </div>
              </template>
            </el-image>
            <div class="image-label">原始 CT 影像</div>
          </div>
        </div>

        <!-- Processed Image -->
        <div class="image-box">
          <div class="image-wrapper" v-loading="loading" element-loading-text="AI 诊断中...">
            <el-image
              :src="url2"
              :preview-src-list="srcList1"
              fit="contain"
              class="main-image"
            >
              <template #error>
                <div class="image-placeholder">
                  <el-icon :size="48" color="#dcdfe6"><MagicStick /></el-icon>
                  <p>{{ waitReturn || '等待诊断结果' }}</p>
                </div>
              </template>
            </el-image>
            <div class="image-label diagnostic">AI 辅助诊断结果</div>
          </div>
        </div>
      </div>

      <div v-if="showUploadButton" class="upload-overlay">
        <el-button type="primary" size="large" :icon="Upload" @click="triggerUpload">
          上传 DICOM 文件开始诊断
        </el-button>
        <input
          ref="fileInput"
          style="display: none"
          type="file"
          accept=".dcm"
          @change="handleFileChange"
        >
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Picture, PictureFilled, MagicStick, Upload } from '@element-plus/icons-vue'

defineProps({
  url1: String,
  url2: String,
  srcList: Array,
  srcList1: Array,
  loading: Boolean,
  showUploadButton: Boolean,
  waitReturn: String
})

const emit = defineEmits(['upload'])
const fileInput = ref(null)

const triggerUpload = () => {
  fileInput.value.click()
}

const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    emit('upload', file)
  }
}
</script>

<style scoped>
.image-workspace {
  height: 100%;
}

.image-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 10px;
}

.image-box {
  position: relative;
}

.image-wrapper {
  background-color: #1a1a1a;
  border-radius: 12px;
  overflow: hidden;
  aspect-ratio: 1 / 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #333;
  box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
}

.main-image {
  width: 100%;
  height: 100%;
}

.image-placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
  gap: 12px;
}

.image-label {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  color: white;
  padding: 4px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 1px;
  pointer-events: none;
  border: 1px solid rgba(255,255,255,0.1);
}

.image-label.diagnostic {
  background: rgba(64, 158, 255, 0.7);
}

.upload-overlay {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
