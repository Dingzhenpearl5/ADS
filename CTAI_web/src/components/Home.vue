<template>
  <div class="home-layout">
    <Header 
      @download-template="handleDownloadTemplate"
      @upload-file="handleUploadFile"
    />
    
    <main class="main-content">
      <div class="content-wrapper">
        <Content ref="content" />
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Header from './Header.vue'
import Footer from './Footer.vue'
import Content from './Content.vue'

const content = ref(null)

const handleDownloadTemplate = () => {
  content.value?.downTemplate()
}

const handleUploadFile = (file) => {
  content.value?.handleFile(file)
}
</script>

<style scoped>
.home-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f0f2f5;
  background-image: 
    radial-gradient(at 0% 0%, rgba(64, 158, 255, 0.05) 0px, transparent 50%),
    radial-gradient(at 100% 0%, rgba(103, 194, 58, 0.05) 0px, transparent 50%);
}

.main-content {
  flex: 1;
  padding: 24px 0;
  overflow-y: auto;
}

.content-wrapper {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 30px;
}
</style>
