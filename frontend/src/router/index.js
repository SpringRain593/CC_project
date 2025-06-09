import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true },
  },
  // NEW: 新增 admin 專用路由
  {
    path: '/admin/users',
    name: 'AdminUserManagement',
    component: () => import('@/views/admin/UserManagement.vue'),
    meta: { requiresAuth: true, requiresRole: 'admin' } // 標記需要 admin 角色
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

// UPDATED: 升級路由守衛
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  // 1. 檢查路由是否需要驗證
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // 如果需要驗證但未登入，導向登入頁
    return next({ name: 'Login' });
  }

  // 2. 檢查路由是否需要特定角色
  if (to.meta.requiresRole && to.meta.requiresRole !== authStore.userRole) {
    // 如果需要特定角色但當前使用者角色不符，導向儀表板
    alert('權限不足！');
    return next({ name: 'Dashboard' });
  }

  // 如果一切檢查通過，正常進行
  next();
});

export default router;