<template>
  <div class="image-workspace">
    <el-card
      class="box-card"
      style="border-radius: 8px; width: 800px; height: 360px; margin-bottom: -30px;"
    >
      <div class="demo-image__preview1">
        <div v-loading="loading" element-loading-text="上传图片中">
          <el-image
            :src="url1"
            class="image_1"
            :preview-src-list="srcList"
            style="border-radius: 3px 3px 0 0"
          >
            <template #error>
              <div class="error">
                <el-button
                  v-show="showUploadButton"
                  type="primary"
                  :icon="Upload"
                  class="download_bt"
                  @click="triggerUpload"
                >
                  上传dcm文件
                  <input
                    ref="fileInput"
                    style="display: none"
                    type="file"
                    @change="handleFileChange"
                  >
                </el-button>
              </div>
            </template>
          </el-image>
        </div>
        <div class="img_info_1" style="border-radius:0 0 5px 5px;">
          <span style="color:white;letter-spacing:6px;">原CT图像</span>
        </div>
      </div>

      <div class="demo-image__preview2">
        <div v-loading="loading" element-loading-text="处理中,请耐心等待">
          <el-image
            :src="url2"
            class="image_1"
            :preview-src-list="srcList1"
            style="border-radius: 3px 3px 0 0;"
          >
            <template #error>
              <div class="error">{{ waitReturn }}</div>
            </template>
          </el-image>
        </div>
        <div class="img_info_1" style="border-radius: 0 0 5px 5px;">
          <span style="color:white;letter-spacing:4px;">标出肿瘤的CT图像</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import { Upload } from '@element-plus/icons-vue'

const props = defineProps({
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
.demo-image__preview1, .demo-image__preview2 {
  display: inline-block;
  width: 48%;
  margin: 1%;
  text-align: center;
}
.image_1 {
  width: 100%;
  height: 250px;
  background-color: #f5f7fa;
}
.img_info_1 {
  background-color: #409EFF;
  padding: 5px 0;
}
.error {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 250px;
  color: #909399;
  background-color: #f5f7fa;
}
</style>
