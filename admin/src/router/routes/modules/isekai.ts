import type { AppRouteModule } from '@/router/types';

import { LAYOUT } from '@/router/constant';

const isekai: AppRouteModule = {
  path: '/isekai',
  name: 'Isekai',
  component: LAYOUT,
  redirect: '/isekai/dashboard',
  meta: {
    orderNo: 500,
    icon: 'ion:globe-outline',
    title: '异世界漫游',
  },
  children: [
    {
      path: 'dashboard',
      name: 'IsekaiDashboard',
      component: () => import('@/views/isekai/dashboard/index.vue'),
      meta: {
        title: '管理首页',
        icon: 'ion:home-outline',
      },
    },
    {
      path: 'characters',
      name: 'IsekaiCharacterList',
      component: () => import('@/views/isekai/character/list.vue'),
      meta: {
        title: '角色管理',
        icon: 'ion:people-outline',
      },
    },
    {
      path: 'characters/:id/edit',
      name: 'IsekaiCharacterEdit',
      component: () => import('@/views/isekai/character/edit.vue'),
      meta: {
        title: '编辑角色',
        hideMenu: true,
        currentActiveMenu: '/isekai/characters',
      },
    },
    {
      path: 'lorebook',
      name: 'IsekaiLorebook',
      component: () => import('@/views/isekai/lorebook/index.vue'),
      meta: {
        title: 'Lorebook 管理',
        icon: 'ion:book-outline',
      },
    },
    {
      path: 'scene',
      name: 'IsekaiScene',
      component: () => import('@/views/isekai/scene/index.vue'),
      meta: {
        title: '场景配置',
        icon: 'ion:map-outline',
      },
    },
    {
      path: 'system-config',
      name: 'IsekaiSystemConfig',
      component: () => import('@/views/isekai/system-config/index.vue'),
      meta: {
        title: '系统配置',
        icon: 'ion:settings-outline',
      },
    },
    {
      path: 'user-management',
      name: 'IsekaiUserManagement',
      component: () => import('@/views/isekai/user-management/index.vue'),
      meta: {
        title: '用户管理',
        icon: 'ion:people-outline',
      },
    },
  ],
};

export default isekai;
