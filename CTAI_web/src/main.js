import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from './utils/request'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as echarts from "echarts"

import '../src/assets/style.css'

const app = createApp(App)

app.config.globalProperties.$echarts = echarts
app.config.globalProperties.$http = axios

app.use(ElementPlus)
app.use(router)
app.mount('#app')
