<template>
  <div class="page-bg">
    <div class="privacy-page">
      <!-- Header -->
      <div class="page-header fade-in-up">
        <n-button text @click="router.back()" class="back-btn">← {{ $t('common.back') }}</n-button>
        <h1 class="gradient-text">{{ $t('privacy.title') }}</h1>
        <p class="last-updated">{{ $t('privacy.lastUpdated') }}: 2026-07-17</p>
      </div>

      <!-- Introduction -->
      <section class="content-section glass-card fade-in-up delay-1">
        <p class="intro-text">{{ $t('privacy.intro') }}</p>
      </section>

      <!-- Data Collection -->
      <section class="content-section glass-card fade-in-up delay-2">
        <h2 class="section-title">{{ $t('privacy.dataCollectionTitle') }}</h2>
        <p class="section-desc">{{ $t('privacy.dataCollectionDesc') }}</p>
        <ul class="info-list">
          <li v-for="(item, index) in dataCollectionItems" :key="index">
            <strong>{{ item.title }}:</strong> {{ item.desc }}
          </li>
        </ul>
      </section>

      <!-- Data Usage -->
      <section class="content-section glass-card fade-in-up delay-3">
        <h2 class="section-title">{{ $t('privacy.dataUsageTitle') }}</h2>
        <p class="section-desc">{{ $t('privacy.dataUsageDesc') }}</p>
        <ul class="info-list">
          <li v-for="(item, index) in dataUsageItems" :key="index">
            {{ item }}
          </li>
        </ul>
      </section>

      <!-- User Rights -->
      <section class="content-section glass-card fade-in-up delay-4">
        <h2 class="section-title">{{ $t('privacy.userRightsTitle') }}</h2>
        <p class="section-desc">{{ $t('privacy.userRightsDesc') }}</p>
        <ul class="info-list">
          <li v-for="(item, index) in userRightsItems" :key="index">
            <strong>{{ item.title }}:</strong> {{ item.desc }}
          </li>
        </ul>
      </section>

      <!-- Data Security -->
      <section class="content-section glass-card fade-in-up delay-5">
        <h2 class="section-title">{{ $t('privacy.securityTitle') }}</h2>
        <p class="content-text">{{ $t('privacy.securityDesc') }}</p>
      </section>

      <!-- Cookies -->
      <section class="content-section glass-card fade-in-up delay-6">
        <h2 class="section-title">{{ $t('privacy.cookiesTitle') }}</h2>
        <p class="content-text">{{ $t('privacy.cookiesDesc') }}</p>
      </section>

      <!-- Third Party -->
      <section class="content-section glass-card fade-in-up delay-7">
        <h2 class="section-title">{{ $t('privacy.thirdPartyTitle') }}</h2>
        <p class="content-text">{{ $t('privacy.thirdPartyDesc') }}</p>
      </section>

      <!-- Children Privacy -->
      <section class="content-section glass-card fade-in-up delay-8">
        <h2 class="section-title">{{ $t('privacy.childrenTitle') }}</h2>
        <p class="content-text">{{ $t('privacy.childrenDesc') }}</p>
      </section>

      <!-- Changes -->
      <section class="content-section glass-card fade-in-up delay-9">
        <h2 class="section-title">{{ $t('privacy.changesTitle') }}</h2>
        <p class="content-text">{{ $t('privacy.changesDesc') }}</p>
      </section>

      <!-- Contact -->
      <section class="content-section glass-card fade-in-up delay-10">
        <h2 class="section-title">{{ $t('privacy.contactTitle') }}</h2>
        <p class="content-text">{{ $t('privacy.contactDesc') }}</p>
        <p class="contact-email">📧 privacy@isekai-wanderer.com</p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';

const router = useRouter();
const { t } = useI18n();

const dataCollectionItems = [
  {
    title: t('privacy.accountInfo'),
    desc: t('privacy.accountInfoDesc')
  },
  {
    title: t('privacy.usageData'),
    desc: t('privacy.usageDataDesc')
  },
  {
    title: t('privacy.deviceInfo'),
    desc: t('privacy.deviceInfoDesc')
  },
  {
    title: t('privacy.gameData'),
    desc: t('privacy.gameDataDesc')
  }
];

const dataUsageItems = [
  t('privacy.usage1'),
  t('privacy.usage2'),
  t('privacy.usage3'),
  t('privacy.usage4'),
  t('privacy.usage5')
];

const userRightsItems = [
  {
    title: t('privacy.rightAccess'),
    desc: t('privacy.rightAccessDesc')
  },
  {
    title: t('privacy.rightRectify'),
    desc: t('privacy.rightRectifyDesc')
  },
  {
    title: t('privacy.rightDelete'),
    desc: t('privacy.rightDeleteDesc')
  },
  {
    title: t('privacy.rightRestrict'),
    desc: t('privacy.rightRestrictDesc')
  },
  {
    title: t('privacy.rightPortability'),
    desc: t('privacy.rightPortabilityDesc')
  }
];
</script>

<style scoped>
.privacy-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 16px 48px;
}

.page-header {
  margin-bottom: 32px;
}

.back-btn {
  color: var(--text-muted) !important;
  font-size: 13px !important;
  padding: 0 !important;
  margin-bottom: 12px;
}

.page-header h1 {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px;
}

.last-updated {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}

.content-section {
  padding: 32px;
  margin-bottom: 24px;
}

.section-title {
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 16px;
  color: var(--text-main);
}

.section-desc {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-main);
  margin: 0 0 16px;
}

.intro-text,
.content-text {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-main);
  margin: 0;
}

.info-list {
  margin: 16px 0 0;
  padding-left: 24px;
}

.info-list li {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-main);
  margin-bottom: 12px;
}

.info-list li:last-child {
  margin-bottom: 0;
}

.info-list strong {
  color: var(--brand-primary);
}

.contact-email {
  font-size: 15px;
  color: var(--brand-primary);
  margin: 16px 0 0;
  font-weight: 600;
}

/* Mobile */
@media (max-width: 768px) {
  .privacy-page {
    padding: 24px 12px 36px;
  }

  .page-header h1 {
    font-size: 28px;
  }

  .content-section {
    padding: 24px 20px;
  }

  .section-title {
    font-size: 20px;
  }

  .info-list {
    padding-left: 20px;
  }
}
</style>
