<template>
  <footer class="app-footer">
    <div class="footer-content">
      <div class="footer-links">
        <el-link :underline="false">关于系统</el-link>
        <el-divider direction="vertical" />
        <el-link :underline="false">使用指南</el-link>
        <el-divider direction="vertical" />
        <el-link :underline="false">隐私政策</el-link>
        <el-divider direction="vertical" />
        <el-link :underline="false">联系我们</el-link>
      </div>
      <div class="copyright">
        <p>&copy; {{ currentYear }} 肿瘤辅助诊断系统. All Rights Reserved.</p>
        <p class="tech-stack">Powered by Vue 3 & Element Plus & AI Engine</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
const currentYear = new Date().getFullYear()
</script>

<style scoped>
.app-footer {
  padding: 40px 0 20px;
  margin-top: 40px;
  border-top: 1px solid #e2e8f0;
  background-color: transparent;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.footer-links {
  display: flex;
  align-items: center;
  gap: 10px;
}

.footer-links :deep(.el-link) {
  font-size: 14px;
  color: #64748b;
}

.footer-links :deep(.el-link:hover) {
  color: var(--primary-color);
}

.copyright {
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
}

.copyright p {
  margin: 4px 0;
}

.tech-stack {
  font-size: 11px;
  opacity: 0.7;
  letter-spacing: 0.5px;
}
</style>


