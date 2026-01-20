import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import axios from './services/request'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as echarts from "echarts"

import './styles/global.css'

const app = createApp(App)
const pinia = createPinia()

app.config.globalProperties.$echarts = echarts
app.config.globalProperties.$http = axios

app.use(pinia)
app.use(ElementPlus)
app.use(router)
app.mount('#app')
