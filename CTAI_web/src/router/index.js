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
        meta: { title: "登录 - 直肠肿瘤辅助诊断系统", requiresAuth: false } 
    },
    {
        path: '/',
        component: () => import('../layouts/AppLayout.vue'),
        meta: { requiresAuth: true },
        children: [
            { 
                path: 'home', 
                component: () => import('../modules/dashboard/views/HomePage.vue'), 
                meta: { title: "首页 - 直肠肿瘤辅助诊断系统" } 
            },
            { 
                path: 'workspace', 
                component: () => import('../modules/imaging/views/WorkspaceHome.vue'), 
                meta: { title: "工作台 - 直肠肿瘤辅助诊断系统" } 
            },
            { 
                path: 'diagnosis/:part', 
                component: () => import('../modules/imaging/views/DiagnosisViewNew.vue'), 
                meta: { title: "诊断分析 - 直肠肿瘤辅助诊断系统" } 
            },
            {
                path: 'history',
                component: () => import('../modules/report/views/HistoryView.vue'),
                meta: { title: "历史记录 - 直肠肿瘤辅助诊断系统" }
            },
            {
                path: 'statistics',
                component: () => import('../modules/report/views/StatisticsView.vue'),
                meta: { title: "统计分析 - 直肠肿瘤辅助诊断系统", requiresAdmin: true }
            },
            {
                path: 'help',
                component: () => import('../modules/dashboard/views/HelpView.vue'),
                meta: { title: "使用帮助 - 直肠肿瘤辅助诊断系统" }
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
    
    // 检查当前路由或其父路由是否需要认证
    // 只要有一个父路由设置了 requiresAuth: true，就需要认证
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth === true)
    
    if (requiresAuth && !token) {
        console.log('[Router] 需要认证但未登录，跳转到登录页')
        ElMessage.warning('请先登录');
        next('/login');
    } else if (to.path === '/login' && token) {
        next('/home');
    } else {
        // 检查是否需要管理员权限
        const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin === true)
        if (requiresAdmin) {
            // 从 localStorage 获取用户信息判断角色
            const userInfoStr = localStorage.getItem('userInfo')
            const userInfo = userInfoStr ? JSON.parse(userInfoStr) : null
            if (!userInfo || userInfo.role !== 'admin') {
                console.log('[Router] 需要管理员权限但当前用户不是管理员')
                ElMessage.error('您没有权限访问该页面');
                next('/home');
                return;
            }
        }
        next();
    }
});

export default router
