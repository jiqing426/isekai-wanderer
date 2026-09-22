<template>
  <div class="page-bg">
    <div class="share-page">
      <!-- Loading -->
      <div v-if="loading" class="share-loading">
        <n-spin size="large" />
        <p>{{ $t('shareExtra.loadingCard') }}</p>
      </div>

      <!-- Share card -->
      <div v-else-if="shareData" class="share-container fade-in-up">
        <div class="share-card glass-card">
          <div class="card-brand">
            <span class="brand-logo">✦</span>
            <span class="brand-name">Isekai Wanderer</span>
          </div>

          <div class="card-character">
            <h2 class="char-name-large">{{ shareData.title }}</h2>
            <div v-if="shareData.description" class="char-script-large">{{ shareData.description }}</div>
          </div>

          <div v-if="shareData.extra_data && Object.keys(shareData.extra_data).length > 0" class="card-stats">
            <div v-for="(val, key) in shareData.extra_data" :key="key" class="stat-block small">
              <div class="stat-label">{{ key }}</div>
              <div class="stat-value">{{ val }}</div>
            </div>
          </div>

          <div class="card-footer">
            <div class="footer-date">{{ formatDate(shareData.created_at) }}</div>
            <div class="footer-id">{{ shareData.id.slice(0, 8) }}</div>
          </div>
        </div>

        <div class="share-actions fade-in-up" style="animation-delay: 0.3s">
          <n-button size="large" block secondary @click="copyLink">
            🔗 {{ $t('shareExtra.copyLink') }}
          </n-button>
          <n-button v-if="isAuthenticated" size="large" block text @click="$router.push('/discover')">
            {{ $t('common.home') }}
          </n-button>
          <n-button v-else size="large" block text @click="$router.push('/login')">
            {{ $t('common.login') }}
          </n-button>
        </div>
      </div>

      <!-- Error -->
      <div v-else class="share-error">
        <n-result status="404" :title="$t('shareExtra.cardNotFound')" :description="$t('shareExtra.cardNotFound')">
          <template #footer>
            <n-button type="primary" @click="$router.push('/login')">{{ $t('common.login') }}</n-button>
          </template>
        </n-result>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/stores/auth';
import { api } from '@/api/http';

const { t } = useI18n();

interface ShareCard {
  id: string;
  share_type: string;
  title: string;
  description?: string;
  image_url?: string;
  extra_data: Record<string, string>;
  created_at: string;
}

const route = useRoute();
const message = useMessage();
const auth = useAuthStore();

const loading = ref(true);
const shareData = ref<ShareCard | null>(null);

const isAuthenticated = computed(() => auth.isAuthenticated);

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });
}

onMounted(async () => {
  const shareId = route.params.shareId as string;
  try {
    const resp = await api.get<ShareCard>(`/share/${shareId}`);
    shareData.value = resp;
  } catch {
    shareData.value = null;
  } finally {
    loading.value = false;
  }
});

async function copyLink() {
  try {
    await navigator.clipboard.writeText(window.location.href);
    message.success(t('shareExtra.linkCopied'));
  } catch {
    message.error(t('shareExtra.copyFailed'));
  }
}
</script>

<style scoped>
.share-page { max-width: 480px; margin: 0 auto; padding: 32px 16px 48px; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.share-loading { display: flex; flex-direction: column; align-items: center; gap: 16px; }
.share-loading p { color: var(--text-muted); font-size: 14px; }
.share-container { width: 100%; }
.share-card { padding: 32px 28px; text-align: center; }
.card-brand { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 28px; }
.brand-logo { font-size: 20px; color: var(--brand-primary); filter: drop-shadow(0 0 8px rgba(192, 132, 252, 0.4)); }
.brand-name { font-size: 14px; color: var(--text-muted); font-weight: 600; letter-spacing: 1px; }
.card-character { margin-bottom: 28px; }
.char-name-large { font-size: 24px; font-weight: 700; margin: 0 0 4px; background: linear-gradient(135deg, #4F46E5, #818CF8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.char-script-large { font-size: 13px; color: var(--text-muted); }
.card-stats { margin-bottom: 24px; display: grid; grid-template-columns: repeat(auto-fit, minmax(80px, 1fr)); gap: 12px; }
.stat-block { text-align: center; }
.stat-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
.stat-value { font-size: 14px; font-weight: 700; color: var(--text-main); }
.card-footer { display: flex; justify-content: space-between; align-items: center; padding-top: 16px; border-top: 1px solid rgba(167, 139, 250, 0.12); }
.footer-date { font-size: 12px; color: var(--text-muted); }
.footer-id { font-size: 11px; color: var(--text-muted); opacity: 0.6; }
.share-actions { display: flex; flex-direction: column; gap: 12px; margin-top: 24px; }
.share-error { width: 100%; }

/* Mobile Responsive */
@media (max-width: 768px) {
  .share-page { padding: 16px 12px 32px; min-height: auto; }
  .share-card { padding: 24px 18px; }
  .card-brand { margin-bottom: 20px; }
  .brand-logo { font-size: 18px; }
  .brand-name { font-size: 13px; }
  .card-character { margin-bottom: 20px; }
  .char-name-large { font-size: 20px; }
  .char-script-large { font-size: 12px; }
  .card-stats { grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 18px; }
  .stat-label { font-size: 10px; }
  .stat-value { font-size: 13px; }
  .card-footer { padding-top: 12px; }
  .footer-date { font-size: 11px; }
  .footer-id { font-size: 10px; }
  .share-actions { gap: 10px; margin-top: 16px; }
}
</style>
