import { createApp } from 'vue'
import App from './App.vue'
import Home from './components/Home.vue'
import Login from './components/Login.vue'
import { createRouter, createWebHistory } from 'vue-router'
import axios from 'axios'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as echarts from "echarts"
import { ElMessage } from 'element-plus'

import '../src/assets/style.css'

const app = createApp(App)

app.config.globalProperties.$echarts = echarts
app.config.globalProperties.$http = axios

app.use(ElementPlus)

// 配置axios默认携带token
axios.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
}, error => {
    return Promise.reject(error);
});

// 响应拦截器，处理401未授权
axios.interceptors.response.use(response => {
    return response;
}, error => {
    if (error.response && error.response.status === 401) {
        // 清除登录信息
        localStorage.removeItem('token');
        localStorage.removeItem('userInfo');
        // 跳转到登录页
        router.push('/login');
        ElMessage.error('登录已过期，请重新登录');
    }
    return Promise.reject(error);
});

const routes = [
    { path: '/', redirect: '/login' },
    { path: '/login', component: Login, meta: { title: "登录 - 肿瘤辅助诊断系统", requiresAuth: false } },
    { path: '/home', component: Home, meta: { title: "首页 - 肿瘤辅助诊断系统", requiresAuth: true } },
    // 兼容旧路由，重定向到home
    { path: "/App", redirect: '/home' },
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
    // 设置页面标题
    if (to.meta.title) {
        document.title = to.meta.title;
    }
    
    // 检查是否需要登录
    const token = localStorage.getItem('token');
    
    if (to.meta.requiresAuth && !token) {
        // 需要登录但未登录，跳转到登录页
        ElMessage.warning('请先登录');
        next('/login');
    } else if (to.path === '/login' && token) {
        // 已登录用户访问登录页，跳转到首页
        next('/home');
    } else {
        next();
    }
});

app.use(router)
app.mount('#app')
