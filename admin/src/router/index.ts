import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { guest: true },
  },
  {
    path: '/',
    component: () => import('@/views/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue'),
      },
      {
        path: 'lorebook',
        name: 'LorebookManage',
        component: () => import('@/views/LorebookManage.vue'),
      },
      {
        path: 'scene-config',
        name: 'SceneConfig',
        component: () => import('@/views/SceneConfig.vue'),
      },
      {
        path: 'characters',
        name: 'CharacterList',
        component: () => import('@/views/CharacterList.vue'),
      },
      {
        path: 'characters/:characterId',
        name: 'CharacterEdit',
        component: () => import('@/views/CharacterEdit.vue'),
        props: true,
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue'),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  auth.syncFromStorage();

  // Fetch profile if authenticated but user not loaded
  if (auth.isAuthenticated && !auth.user) {
    try {
      await auth.fetchProfile();
    } catch {
      auth.logout();
      if (to.meta.requiresAuth) {
        return { name: 'Login' };
      }
    }
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'Login', query: { redirect: to.fullPath } };
  }

  if (to.meta.requiresAdmin && !auth.isAdmin) {
    // If user is authenticated but not admin, show error
    if (auth.isAuthenticated) {
      return { name: 'Dashboard' }; // Will show access denied in layout
    }
    return { name: 'Login' };
  }

  if (to.meta.guest && auth.isAuthenticated) {
    return { name: 'Dashboard' };
  }

  return true;
});

export default router;
