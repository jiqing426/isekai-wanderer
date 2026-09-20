import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { authApi } from '@/api/auth';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Landing',
    component: () => import('@/views/LandingView.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { guest: true },
  },
  {
    path: '/onboarding',
    name: 'Onboarding',
    component: () => import('@/views/OnboardingView.vue'),
    meta: { requiresAuth: true },
  },

  // CR3-005: Discover page
  {
    path: '/discover',
    name: 'Discover',
    component: () => import('@/views/DiscoverView.vue'),
    meta: { requiresAuth: true },
  },
  // CR3-010: Character detail
  {
    path: '/characters/:characterId',
    name: 'CharacterDetail',
    component: () => import('@/views/CharacterDetailView.vue'),
    meta: { requiresAuth: true },
  },
  // Gift sending
  {
    path: '/characters/:characterId/gift',
    name: 'Gift',
    component: () => import('@/views/GiftView.vue'),
    meta: { requiresAuth: true },
  },
  // CR3-015: Save Manager
  {
    path: '/saves',
    name: 'SaveManager',
    component: () => import('@/views/SaveManagerView.vue'),
    meta: { requiresAuth: true },
  },
  // Fragment Mall (碎片商城)
  {
    path: '/fragment',
    name: 'FragmentMall',
    component: () => import('@/views/FragmentMallView.vue'),
    meta: { requiresAuth: true },
  },
  // CR3-022: Achievement Wall
  {
    path: '/achievements',
    name: 'Achievements',
    component: () => import('@/views/AchievementView.vue'),
    meta: { requiresAuth: true },
  },
  // CR-008: Personal Center
  {
    path: '/personal-center',
    name: 'PersonalCenter',
    component: () => import('@/views/PersonalCenterView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/game',
    name: 'Game',
    component: () => import('@/views/GameView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/game/:sessionId/ending',
    name: 'Ending',
    component: () => import('@/views/EndingView.vue'),
    meta: { requiresAuth: true },
  },
  // CR3-012: Recap system
  {
    path: '/game/:sessionId/recap',
    name: 'Recap',
    component: () => import('@/views/RecapView.vue'),
    meta: { requiresAuth: true },
  },
  // AC-045: Route map
  {
    path: '/game/:sessionId/route-map',
    name: 'RouteMap',
    component: () => import('@/views/RouteMap.vue'),
    meta: { requiresAuth: true },
  },
  // AC-058: Free chat
  {
    path: '/game/:sessionId/free-chat',
    name: 'FreeChat',
    component: () => import('@/views/FreeChatView.vue'),
    meta: { requiresAuth: true },
  },
  // CR-021: Character chat
  {
    path: '/character-chat',
    name: 'CharacterChat',
    component: () => import('@/views/CharacterChatView.vue'),
    meta: { requiresAuth: true },
  },
  // AC-045: Script detail (public browse, auth needed to play)
  {
    path: '/scripts/:scriptId',
    name: 'ScriptDetail',
    component: () => import('@/views/ScriptDetailView.vue'),
  },
  // Phase 3 routes
  {
    path: '/subscribe',
    name: 'Subscription',
    component: () => import('@/views/SubscriptionView.vue'),
    // CEO-UI-7: Subscription page browseable without login; prompt on subscribe action
  },
  {
    path: '/community',
    name: 'Community',
    component: () => import('@/views/CommunityView.vue'),
    // CEO-UI-6: Community/script hall browseable without login
  },
  {
    path: '/gallery',
    name: 'Gallery',
    component: () => import('@/views/GalleryView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/ForgotPasswordView.vue'),
    meta: { guest: true },
  },
  {
    path: '/reset-password/:token',
    name: 'ResetPassword',
    component: () => import('@/views/ResetPasswordView.vue'),
    meta: { guest: true },
  },
  {
    path: '/share/:shareId',
    name: 'Share',
    component: () => import('@/views/ShareView.vue'),
    meta: { guest: true }, // Public page, no auth required
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SettingsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/oauth/callback',
    name: 'OAuthCallback',
    component: () => import('@/views/OAuthCallbackView.vue'),
    meta: { guest: true },
  },
  // W14: About, Privacy, Terms pages (public access)
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/AboutView.vue'),
  },
  {
    path: '/privacy',
    name: 'Privacy',
    component: () => import('@/views/PrivacyView.vue'),
  },
  {
    path: '/terms',
    name: 'Terms',
    component: () => import('@/views/TermsView.vue'),
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

  // 从 cookie 同步 token（用于多 tab 场景）
  auth.syncFromCookie();

  // If authenticated but profile not loaded (e.g. after page refresh), fetch it
  if (auth.isAuthenticated && !auth.user) {
    try {
      const profile = await authApi.getProfile();
      auth.setUser({
        id: profile.id,
        email: profile.email,
        displayName: profile.display_name,
        onboardingCompleted: profile.onboarding_completed,
        emailVerified: profile.email_verified,
        avatar: profile.avatar_url,
      });

      // CR-043 AC-020: 登录/页面刷新后自动加载订阅状态
      const { useSubscriptionStore } = await import('@/stores/subscription');
      const subscriptionStore = useSubscriptionStore();
      await subscriptionStore.fetchSubscriptionStatus();
    } catch (err: any) {
      console.warn('路由守卫验证 Token 失败:', err instanceof Error ? err.message : err);
      // Only clear tokens if it's an auth error (401)
      const isAuthError = err?.response?.status === 401 || 
                         err?.errorCode === 'AUTH_TOKEN_EXPIRED' ||
                         err?.errorCode === 'AUTH_TOKEN_INVALID';
      
      if (isAuthError) {
        auth.logout();
        if (to.meta.requiresAuth) {
          return { name: 'Login', query: { redirect: to.fullPath, expired: '1' } };
        }
      }
      // For other errors (network, server error), don't clear tokens - let user continue
    }
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return {
      name: 'Login',
      query: { redirect: to.fullPath },
    };
  }

  if (to.meta.guest && auth.isAuthenticated) {
    if (auth.user && !auth.user.onboardingCompleted) {
      return { name: 'Onboarding' };
    }
    return { name: 'Landing' };
  }

  // Landing 页对所有人可见，不再强制跳转

  // Authenticated users that haven't completed onboarding should go to onboarding
  if (to.name !== 'Onboarding' && to.name !== 'Login' && to.name !== 'Register' && auth.user && !auth.user.onboardingCompleted) {
    return { name: 'Onboarding' };
  }

  return true;
});

export default router;
