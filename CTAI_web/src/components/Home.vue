<template>
  <div class="home">
    <app-header 
      @download-template="handleDownloadTemplate"
      @upload-file="handleUploadFile"
    ></app-header>
    <app-content ref="content"></app-content>
    <app-footer></app-footer>
  </div>
</template>

<script>
import Header from './Header'
import Footer from './Footer'
import Content from './Content'

export default {
  name: "AppHome",
  components:{
    "app-header":Header,
    "app-footer":Footer,
    "app-content":Content
  },
  methods: {
    handleDownloadTemplate() {
      this.$refs.content.downTemplate();
    },
    handleUploadFile(file) {
      this.$refs.content.handleFile(file);
    }
  }
};
</script>

<style scoped>
</style>
