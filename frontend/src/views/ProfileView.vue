<template>
  <div class="page-bg">
    <div class="profile-page">
      <header class="profile-header glass-card">
        <div class="avatar-area">
          <div class="avatar-circle">
            <span class="avatar-emoji">{{ (auth.user as any)?.avatar || '👤' }}</span>
          </div>
          <div class="user-info">
            <h2 class="user-name">{{ (auth.user as any)?.username || $t('profile.adventurer') }}</h2>
            <span class="user-email">{{ auth.user?.email }}</span>
          </div>
        </div>
        <div class="profile-stats">
          <div class="pstat">
            <span class="pstat-num">{{ stats.total_plays }}</span>
            <span class="pstat-label">{{ $t('profile.totalPlays') }}</span>
          </div>
          <div class="pstat">
            <span class="pstat-num">{{ stats.scripts_completed }}</span>
            <span class="pstat-label">{{ $t('profile.completedScripts') }}</span>
          </div>
          <div class="pstat">
            <span class="pstat-num">{{ stats.total_hours }}</span>
            <span class="pstat-label">{{ $t('profile.hours') }}</span>
          </div>
          <div class="pstat">
            <span class="pstat-num">{{ stats.achievements_unlocked }}</span>
            <span class="pstat-label">{{ $t('profile.achievements') }}</span>
          </div>
        </div>
      </header>

      <!-- Quick links -->
      <div class="quick-grid">
        <router-link to="/achievements" class="quick-card glass-card">
          <span class="q-icon">🏆</span>
          <span class="q-label">{{ $t('profile.achievementWall') }}</span>
        </router-link>
        <router-link to="/saves" class="quick-card glass-card">
          <span class="q-icon">💾</span>
          <span class="q-label">{{ $t('profile.saveManager') }}</span>
        </router-link>
        <router-link to="/characters" class="quick-card glass-card">
          <span class="q-icon">👥</span>
          <span class="q-label">{{ $t('profile.characterGuide') }}</span>
        </router-link>
        <router-link to="/shards" class="quick-card glass-card">
          <span class="q-icon">💎</span>
          <span class="q-label">{{ $t('profile.shardCenter') }}</span>
        </router-link>
        <router-link to="/subscription" class="quick-card glass-card">
          <span class="q-icon">👑</span>
          <span class="q-label">{{ $t('profile.subscription') }}</span>
        </router-link>
      </div>

      <!-- Activity Chest (CR3-026) -->
      <section class="section glass-card">
        <ActivityChest />
      </section>

      <!-- Task Panel (CR3-025) -->
      <section class="section glass-card">
        <TaskPanel />
      </section>

      <!-- Actions -->
      <div class="profile-actions">
        <n-button type="error" secondary @click="handleLogout">🚪 {{ $t('profile.logout') }}</n-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage } from 'naive-ui';
import { useHead } from '@vueuse/head';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/stores/auth';
import ActivityChest from '@/components/ActivityChest.vue';
import TaskPanel from '@/components/TaskPanel.vue';

const { t } = useI18n();

useHead({
  title: 'Isekai Wanderer - Profile',
  meta: [{ name: 'description', content: () => t('profile.metaDesc') }],
});

const router = useRouter();
const message = useMessage();
const auth = useAuthStore();

const stats = reactive({
  total_plays: 0,
  scripts_completed: 0,
  total_hours: 0,
  achievements_unlocked: 0,
});

function handleLogout() {
  auth.logout();
  message.success(t('profile.logoutSuccess'));
  router.push('/');
}

onMounted(() => {
  // Stats will come from API when available
});
</script>

<style scoped>
.profile-page { max-width: 600px; margin: 0 auto; padding: 24px 16px 100px; }
.profile-header { padding: 20px; margin-bottom: 16px; }
.avatar-area { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; }
.avatar-circle {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.15), rgba(244, 114, 182, 0.15));
  display: flex;
  align-items: center;
  justify-content: center;
}
.avatar-emoji { font-size: 36px; }
.user-name { font-size: 20px; font-weight: 700; color: var(--text-main); margin: 0; }
.user-email { font-size: 12px; color: var(--text-muted); }
.profile-stats {
  display: flex;
  justify-content: space-around;
  padding-top: 16px;
  border-top: 1px solid rgba(167, 139, 250, 0.1);
}
.pstat { text-align: center; }
.pstat-num { display: block; font-size: 20px; font-weight: 800; color: var(--brand-primary); font-variant-numeric: tabular-nums; }
.pstat-label { font-size: 11px; color: var(--text-muted); }
.quick-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}
.quick-card {
  text-align: center;
  padding: 16px 8px;
  text-decoration: none;
  transition: all 0.2s;
}
.quick-card:hover { transform: translateY(-2px); }
.q-icon { font-size: 28px; display: block; margin-bottom: 6px; }
.q-label { font-size: 12px; font-weight: 500; color: var(--text-main); }
.section { padding: 16px; margin-bottom: 16px; }
.profile-actions { display: flex; justify-content: center; margin-top: 24px; }
</style>
