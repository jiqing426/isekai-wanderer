<template>
  <div class="page-bg">
    <div class="about-page">
      <!-- Header -->
      <div class="page-header fade-in-up">
        <n-button text @click="router.back()" class="back-btn">← {{ $t('common.back') }}</n-button>
        <h1 class="gradient-text">{{ $t('about.title') }}</h1>
      </div>

      <!-- Brand Introduction -->
      <section class="content-section glass-card fade-in-up delay-1">
        <h2 class="section-title">{{ $t('about.brandTitle') }}</h2>
        <div class="content-text">
          <p>{{ $t('about.brandDesc1') }}</p>
          <p>{{ $t('about.brandDesc2') }}</p>
          <p>{{ $t('about.brandDesc3') }}</p>
        </div>
      </section>

      <!-- Vision & Mission -->
      <section class="content-section glass-card fade-in-up delay-2">
        <h2 class="section-title">{{ $t('about.visionTitle') }}</h2>
        <div class="vision-grid">
          <div class="vision-item">
            <div class="vision-icon">🎯</div>
            <h3>{{ $t('about.mission') }}</h3>
            <p>{{ $t('about.missionDesc') }}</p>
          </div>
          <div class="vision-item">
            <div class="vision-icon">🌟</div>
            <h3>{{ $t('about.vision') }}</h3>
            <p>{{ $t('about.visionDesc') }}</p>
          </div>
          <div class="vision-item">
            <div class="vision-icon">💎</div>
            <h3>{{ $t('about.values') }}</h3>
            <p>{{ $t('about.valuesDesc') }}</p>
          </div>
        </div>
      </section>

      <!-- Team -->
      <section class="content-section glass-card fade-in-up delay-3">
        <h2 class="section-title">{{ $t('about.teamTitle') }}</h2>
        <p class="team-intro">{{ $t('about.teamIntro') }}</p>
        <div class="team-grid">
          <div v-for="(member, index) in teamMembers" :key="index" class="team-member">
            <div class="member-avatar">{{ member.emoji }}</div>
            <h3 class="member-name">{{ member.name }}</h3>
            <p class="member-role">{{ member.role }}</p>
            <p class="member-desc">{{ member.desc }}</p>
          </div>
        </div>
      </section>

      <!-- Contact -->
      <section class="content-section glass-card fade-in-up delay-4">
        <h2 class="section-title">{{ $t('about.contactTitle') }}</h2>
        <div class="contact-info">
          <div class="contact-item">
            <span class="contact-icon">📧</span>
            <div>
              <h4>{{ $t('about.email') }}</h4>
              <p>support@isekai-wanderer.com</p>
            </div>
          </div>
          <div class="contact-item">
            <span class="contact-icon">💬</span>
            <div>
              <h4>{{ $t('about.discord') }}</h4>
              <p>discord.gg/isekai-wanderer</p>
            </div>
          </div>
          <div class="contact-item">
            <span class="contact-icon">🐦</span>
            <div>
              <h4>{{ $t('about.twitter') }}</h4>
              <p>@isekai_wanderer</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';

const router = useRouter();
const { t } = useI18n();

const teamMembers = [
  {
    emoji: '👨‍💻',
    name: t('about.team1Name'),
    role: t('about.team1Role'),
    desc: t('about.team1Desc')
  },
  {
    emoji: '👩‍🎨',
    name: t('about.team2Name'),
    role: t('about.team2Role'),
    desc: t('about.team2Desc')
  },
  {
    emoji: '👨‍🔬',
    name: t('about.team3Name'),
    role: t('about.team3Role'),
    desc: t('about.team3Desc')
  },
  {
    emoji: '👩‍💼',
    name: t('about.team4Name'),
    role: t('about.team4Role'),
    desc: t('about.team4Desc')
  }
];
</script>

<style scoped>
.about-page {
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
  margin: 0;
}

.content-section {
  padding: 32px;
  margin-bottom: 24px;
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 20px;
  color: var(--text-main);
}

.content-text p {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-main);
  margin: 0 0 16px;
}

.content-text p:last-child {
  margin-bottom: 0;
}

/* Vision Grid */
.vision-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.vision-item {
  text-align: center;
}

.vision-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.vision-item h3 {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 8px;
  color: var(--text-main);
}

.vision-item p {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-muted);
  margin: 0;
}

/* Team */
.team-intro {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-main);
  margin: 0 0 24px;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
}

.team-member {
  text-align: center;
}

.member-avatar {
  font-size: 64px;
  margin-bottom: 12px;
}

.member-name {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 4px;
  color: var(--text-main);
}

.member-role {
  font-size: 14px;
  font-weight: 600;
  color: var(--brand-primary);
  margin: 0 0 8px;
}

.member-desc {
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-muted);
  margin: 0;
}

/* Contact */
.contact-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.contact-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.contact-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.contact-item h4 {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 4px;
  color: var(--text-main);
}

.contact-item p {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}

/* Mobile */
@media (max-width: 768px) {
  .about-page {
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

  .vision-grid,
  .team-grid {
    grid-template-columns: 1fr;
  }
}
</style>
