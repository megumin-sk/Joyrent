import { createRouter, createWebHistory } from 'vue-router';

// Lazy load components
const Dashboard = () => import('../views/dashboard/index.vue');
const GameList = () => import('../views/game/gameManage.vue');
const Login = () => import('../views/login/index.vue');
// Placeholders for other modules to prevent errors if files don't exist yet
const Placeholder = { template: '<div style="color:white">Coming Soon</div>' };

const routes = [
    {
        path: '/',
        redirect: '/dashboard'
    },
    {
        path: '/login',
        name: 'login',
        component: Login
    },
    {
        path: '/dashboard',
        name: 'dashboard',
        component: Dashboard
    },
    {
        path: '/game',
        name: 'game',
        component: GameList
    },
    {
        path: '/order',
        name: 'order',
        component: Placeholder
    },
    {
        path: '/user',
        name: 'user',
        component: Placeholder
    },
    {
        path: '/review',
        name: 'review',
        component: Placeholder
    },
    {
        path: '/rag',
        name: 'rag',
        component: () => import('../views/rag/index.vue')
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

// 路由守卫
router.beforeEach((to, from, next) => {
    // 获取 token，这里直接从 localStorage 获取，避免循环依赖 store
    const hasToken = localStorage.getItem('Admin-Token');

    if (to.path === '/login') {
        if (hasToken) {
            // 已登录，跳转首页
            next({ path: '/' });
        } else {
            next();
        }
    } else {
        if (hasToken) {
            next();
        } else {
            // 未登录，跳转登录页
            next(`/login?redirect=${to.path}`);
        }
    }
});

export default router;
