<template>
  <div class="page-bg">
    <div class="terms-page">
      <!-- Header -->
      <div class="page-header fade-in-up">
        <n-button text @click="router.back()" class="back-btn">← {{ $t('common.back') }}</n-button>
        <h1 class="gradient-text">{{ $t('terms.title') }}</h1>
        <p class="last-updated">{{ $t('terms.lastUpdated') }}: 2026-07-17</p>
      </div>

      <!-- Introduction -->
      <section class="content-section glass-card fade-in-up delay-1">
        <p class="intro-text">{{ $t('terms.intro') }}</p>
      </section>

      <!-- Service Description -->
      <section class="content-section glass-card fade-in-up delay-2">
        <h2 class="section-title">{{ $t('terms.serviceTitle') }}</h2>
        <p class="content-text">{{ $t('terms.serviceDesc') }}</p>
      </section>

      <!-- User Accounts -->
      <section class="content-section glass-card fade-in-up delay-3">
        <h2 class="section-title">{{ $t('terms.accountsTitle') }}</h2>
        <p class="content-text">{{ $t('terms.accountsDesc') }}</p>
        <ul class="info-list">
          <li>{{ $t('terms.accounts1') }}</li>
          <li>{{ $t('terms.accounts2') }}</li>
          <li>{{ $t('terms.accounts3') }}</li>
          <li>{{ $t('terms.accounts4') }}</li>
        </ul>
      </section>

      <!-- User Responsibilities -->
      <section class="content-section glass-card fade-in-up delay-4">
        <h2 class="section-title">{{ $t('terms.responsibilitiesTitle') }}</h2>
        <p class="content-text">{{ $t('terms.responsibilitiesDesc') }}</p>
        <ul class="info-list">
          <li>{{ $t('terms.resp1') }}</li>
          <li>{{ $t('terms.resp2') }}</li>
          <li>{{ $t('terms.resp3') }}</li>
          <li>{{ $t('terms.resp4') }}</li>
          <li>{{ $t('terms.resp5') }}</li>
        </ul>
      </section>

      <!-- Payment and Subscription -->
      <section class="content-section glass-card fade-in-up delay-5">
        <h2 class="section-title">{{ $t('terms.paymentTitle') }}</h2>
        <p class="content-text">{{ $t('terms.paymentDesc') }}</p>
        <ul class="info-list">
          <li>{{ $t('terms.payment1') }}</li>
          <li>{{ $t('terms.payment2') }}</li>
          <li>{{ $t('terms.payment3') }}</li>
          <li>{{ $t('terms.payment4') }}</li>
        </ul>
      </section>

      <!-- Intellectual Property -->
      <section class="content-section glass-card fade-in-up delay-6">
        <h2 class="section-title">{{ $t('terms.ipTitle') }}</h2>
        <p class="content-text">{{ $t('terms.ipDesc') }}</p>
      </section>

      <!-- Prohibited Activities -->
      <section class="content-section glass-card fade-in-up delay-7">
        <h2 class="section-title">{{ $t('terms.prohibitedTitle') }}</h2>
        <p class="content-text">{{ $t('terms.prohibitedDesc') }}</p>
        <ul class="info-list">
          <li>{{ $t('terms.prohibited1') }}</li>
          <li>{{ $t('terms.prohibited2') }}</li>
          <li>{{ $t('terms.prohibited3') }}</li>
          <li>{{ $t('terms.prohibited4') }}</li>
          <li>{{ $t('terms.prohibited5') }}</li>
        </ul>
      </section>

      <!-- Limitation of Liability -->
      <section class="content-section glass-card fade-in-up delay-8">
        <h2 class="section-title">{{ $t('terms.liabilityTitle') }}</h2>
        <p class="content-text">{{ $t('terms.liabilityDesc') }}</p>
      </section>

      <!-- Termination -->
      <section class="content-section glass-card fade-in-up delay-9">
        <h2 class="section-title">{{ $t('terms.terminationTitle') }}</h2>
        <p class="content-text">{{ $t('terms.terminationDesc') }}</p>
      </section>

      <!-- Dispute Resolution -->
      <section class="content-section glass-card fade-in-up delay-10">
        <h2 class="section-title">{{ $t('terms.disputeTitle') }}</h2>
        <p class="content-text">{{ $t('terms.disputeDesc') }}</p>
      </section>

      <!-- Changes to Terms -->
      <section class="content-section glass-card fade-in-up delay-11">
        <h2 class="section-title">{{ $t('terms.changesTitle') }}</h2>
        <p class="content-text">{{ $t('terms.changesDesc') }}</p>
      </section>

      <!-- Contact -->
      <section class="content-section glass-card fade-in-up delay-12">
        <h2 class="section-title">{{ $t('terms.contactTitle') }}</h2>
        <p class="content-text">{{ $t('terms.contactDesc') }}</p>
        <p class="contact-email">📧 legal@isekai-wanderer.com</p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();
</script>

<style scoped>
.terms-page {
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

.contact-email {
  font-size: 15px;
  color: var(--brand-primary);
  margin: 16px 0 0;
  font-weight: 600;
}

/* Mobile */
@media (max-width: 768px) {
  .terms-page {
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
