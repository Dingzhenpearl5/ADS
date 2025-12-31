import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'

const routes = [
    { 
        path: '/', 
        redirect: '/login' 
    },
    { 
        path: '/login', 
        component: () => import('../modules/auth/views/Login.vue'), 
        meta: { title: "登录 - 肿瘤辅助诊断系统", requiresAuth: false } 
    },
    {
        path: '/',
        component: () => import('../layouts/AppLayout.vue'),
        meta: { requiresAuth: true },
        children: [
            { 
                path: 'home', 
                component: () => import('../modules/imaging/views/DiagnosisView.vue'), 
                meta: { title: "工作台 - 肿瘤辅助诊断系统" } 
            },
            {
                path: 'history',
                component: () => import('../modules/report/views/HistoryView.vue'),
                meta: { title: "历史记录 - 肿瘤辅助诊断系统" }
            },
            {
                path: 'statistics',
                component: () => import('../modules/report/views/StatisticsView.vue'),
                meta: { title: "统计分析 - 肿瘤辅助诊断系统" }
            }
        ]
    },
    { 
        path: "/App", 
        redirect: '/home' 
    },
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
        ElMessage.warning('请先登录');
        next('/login');
    } else if (to.path === '/login' && token) {
        next('/home');
    } else {
        next();
    }
});

export default router
