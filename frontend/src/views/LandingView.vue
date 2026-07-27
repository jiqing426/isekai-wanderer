<template>
  <div class="landing-page" ref="pageRef">
    <!-- Hero Section -->
    <section class="hero-section">
      <!-- Particle background -->
      <div class="hero-bg-effects">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="orb orb-3"></div>
        <div class="star-field" ref="starsRef"></div>
        <div class="particles" ref="particlesRef"></div>
      </div>

      <div class="hero-content">
        <!-- 1. Badge -->
        <div class="hero-badge fade-in-up">
          <span class="badge-icon">🤖</span>
          <span>{{ $t('landing.badge') }}</span>
        </div>

        <!-- 2. H1 gradient -->
        <h1 class="hero-title fade-in-up delay-1">
          {{ $t('landing.heroTitle') }}
        </h1>

        <!-- 3. Rotating subtitle (typewriter) -->
        <p class="hero-subtitle fade-in-up delay-2">
          {{ rotatingSubtitle }}<span class="cursor" v-if="!subtitleTypingDone">|</span>
        </p>

        <!-- 4. English subtitle -->
        <p class="hero-subtitle-en fade-in-up delay-2">
          {{ $t('landing.heroSubtitleEn') }}
        </p>

        <!-- 5. Demo Box (inside hero) -->
        <div class="demo-box fade-in-up delay-3">
          <div class="demo-header">
            <div class="demo-avatar">🌸</div>
            <div class="demo-info">
              <span class="demo-name">{{ $t('landing.demoName') }}</span>
              <span class="demo-bond">💕 Lv.3 {{ $t('landing.demoBond') }}</span>
            </div>
          </div>
          <div class="demo-text">
            {{ demoDialogue }}<span class="cursor" v-if="!demoTypingDone">|</span>
          </div>
          <div class="demo-choices" v-if="!demoReplied">
            <button class="demo-choice-btn" @click="handleDemoChoice(0)">
              🤝 {{ $t('landing.demoChoice1') }}
            </button>
            <button class="demo-choice-btn" @click="handleDemoChoice(1)">
              🌙 {{ $t('landing.demoChoice2') }}
            </button>
          </div>
          <div class="demo-reply" v-else>
            {{ demoReply }}
          </div>
        </div>

        <!-- 6. CTA buttons -->
        <div class="hero-actions fade-in-up delay-4">
          <button class="cta-primary" @click="handlePrimaryCta">
            🌸 {{ $t('landing.ctaPrimary') }}
          </button>
          <button class="cta-secondary" @click="router.push('/discover')">
            📚 {{ $t('landing.ctaSecondary') }}
          </button>
        </div>

        <!-- 7. Social proof (pill capsule) -->
        <div class="social-proof fade-in-up delay-4">
          <span class="proof-pill">{{ $t('landing.proof1') }}</span>
          <span class="proof-pill">{{ $t('landing.proof2') }}</span>
          <span class="proof-pill">{{ $t('landing.proof3') }}</span>
        </div>
      </div>
    </section>

    <!-- Features Section (6 cards, 4-column grid) -->
    <section id="features" class="features-section">
      <div class="section-header">
        <h2 class="section-title gradient-text reveal">✨ {{ $t('landing.featuresTitle') }}</h2>
      </div>
      <div class="features-grid">
        <div v-for="(feature, i) in features" :key="i" class="feature-card reveal-scale" :style="{ transitionDelay: `${i * 0.1}s` }">
          <div class="feature-icon float" :style="{ animationDelay: `${i * 0.5}s` }">{{ feature.icon }}</div>
          <h3 class="feature-title">{{ $t(feature.titleKey) }}</h3>
          <p class="feature-desc">{{ $t(feature.descKey) }}</p>
        </div>
      </div>
    </section>

    <!-- Testimonials Section -->
    <section class="testimonials-section">
      <div class="section-header">
        <h2 class="section-title gradient-text reveal">{{ $t('landing.testimonialsTitle') }}</h2>
        <p class="section-desc reveal delay-1">{{ $t('landing.testimonialsDesc') }}</p>
      </div>
      <div class="testimonials-grid">
        <div v-for="(testimonial, i) in testimonials" :key="i" class="testimonial-card reveal-scale" :style="{ transitionDelay: `${i * 0.15}s` }">
          <div class="testimonial-avatar"><span class="avatar-emoji">{{ testimonial.avatar }}</span></div>
          <div class="testimonial-content">
            <div class="testimonial-header">
              <h3 class="testimonial-name">{{ testimonial.name }}</h3>
              <p class="testimonial-role">{{ testimonial.title }}</p>
            </div>
            <div class="testimonial-rating">
              <span v-for="star in 5" :key="star" class="star" :class="{ filled: star <= testimonial.rating }">★</span>
            </div>
            <p class="testimonial-text">{{ testimonial.text }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section class="how-section">
      <div class="section-header">
        <h2 class="section-title gradient-text reveal">{{ $t('landing.howTitle') }}</h2>
      </div>
      <div class="steps-container">
        <div v-for="(step, i) in steps" :key="i" class="step-item reveal-left" :style="{ transitionDelay: `${i * 0.15}s` }">
          <div class="step-number">{{ String(i + 1).padStart(2, '0') }}</div>
          <div class="step-content">
            <h3 class="step-title">{{ $t(step.titleKey) }}</h3>
            <p class="step-desc">{{ $t(step.descKey) }}</p>
          </div>
          <div class="step-connector" v-if="i < steps.length - 1"></div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="cta-card reveal-scale">
        <h2 class="cta-title gradient-text">{{ $t('landing.ctaTitle') }}</h2>
        <p class="cta-desc">{{ $t('landing.heroSubtitle') }}</p>
        <n-button type="primary" size="large" class="cta-final-btn" @click="handlePrimaryCta">
          {{ auth.isAuthenticated ? '开始冒险' : '立即注册' }}
        </n-button>
        <div class="social-links">
          <a href="#" class="social-link" aria-label="Discord">💬</a>
          <a href="#" class="social-link" aria-label="Twitter">🐦</a>
          <a href="#" class="social-link" aria-label="GitHub">🐙</a>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="landing-footer">
      <p>{{ $t('landing.footerText') }}</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useHead } from '@vueuse/head';
import { useAuthStore } from '@/stores/auth';
import { useScrollReveal } from '@/composables/useScrollReveal';

useHead({
  title: 'Isekai Wanderer - 穿越异世界，书写你的传奇',
  meta: [
    { name: 'description', content: '沉浸式 AI 互动叙事游戏，每一个选择都改变命运。探索精彩剧本，与角色建立羁绊，收集精美 CG。' },
    { property: 'og:title', content: 'Isekai Wanderer - 穿越异世界，书写你的传奇' },
    { property: 'og:description', content: 'AI 驱动的沉浸式叙事游戏，每一个选择都改变命运。' },
    { property: 'og:image', content: '/og-image.png' },
    { property: 'og:type', content: 'website' },
    { name: 'twitter:card', content: 'summary_large_image' },
  ],
});

const router = useRouter();
const auth = useAuthStore();
const pageRef = ref<HTMLElement | null>(null);
const starsRef = ref<HTMLElement | null>(null);
const particlesRef = ref<HTMLElement | null>(null);

useScrollReveal(pageRef);

// Rotating subtitle (3 sentences, typewriter effect, 3s interval)
const rotatingSubtitles = [
  'AI驱动的互动视觉小说平台',
  '每一次选择，都改变世界',
  '穿越异世界，书写你的传奇'
];
const rotatingSubtitle = ref('');
const subtitleTypingDone = ref(false);
let currentSubtitleIndex = 0;
let subtitleTypingInterval: ReturnType<typeof setInterval> | null = null;
let subtitleRotationInterval: ReturnType<typeof setInterval> | null = null;

function typeSubtitle(text: string) {
  rotatingSubtitle.value = '';
  subtitleTypingDone.value = false;
  let idx = 0;
  
  if (subtitleTypingInterval) clearInterval(subtitleTypingInterval);
  
  subtitleTypingInterval = setInterval(() => {
    idx++;
    rotatingSubtitle.value = text.slice(0, idx);
    if (idx >= text.length) {
      if (subtitleTypingInterval) clearInterval(subtitleTypingInterval);
      subtitleTypingDone.value = true;
    }
  }, 50);
}

function rotateSubtitle() {
  typeSubtitle(rotatingSubtitles[currentSubtitleIndex]);
  currentSubtitleIndex = (currentSubtitleIndex + 1) % rotatingSubtitles.length;
}

// Demo dialogue (3 sentences, typewriter effect, 3s interval)
const demoDialogues = [
  '「你知道吗……我一直在想你昨天说过的话。关于故事不是被讲述的——而是被经历的。」',
  '「和你在一起的每一刻，都像是被星光笼罩。时间仿佛在这一刻停住了。」',
  '「我想告诉你一件事……一件我从未告诉过任何人的事。你愿意听吗？」'
];
const demoDialogue = ref('');
const demoTypingDone = ref(false);
const demoReplied = ref(false);
const demoReply = ref('');
let currentDialogueIndex = 0;
let demoTypingInterval: ReturnType<typeof setInterval> | null = null;
let demoRotationInterval: ReturnType<typeof setInterval> | null = null;

function typeDemoDialogue(text: string) {
  demoDialogue.value = '';
  demoTypingDone.value = false;
  demoReplied.value = false;
  demoReply.value = '';
  let idx = 0;
  
  if (demoTypingInterval) clearInterval(demoTypingInterval);
  
  demoTypingInterval = setInterval(() => {
    idx++;
    demoDialogue.value = text.slice(0, idx);
    if (idx >= text.length) {
      if (demoTypingInterval) clearInterval(demoTypingInterval);
      demoTypingDone.value = true;
    }
  }, 50);
}

function rotateDemoDialogue() {
  typeDemoDialogue(demoDialogues[currentDialogueIndex]);
  currentDialogueIndex = (currentDialogueIndex + 1) % demoDialogues.length;
}

function handleDemoChoice(choiceIndex: number) {
  demoReplied.value = true;
  if (choiceIndex === 0) {
    demoReply.value = '雪乃微微一笑，握紧了你的手。💕 好感度+5';
  } else {
    demoReply.value = '雪乃低下头，嘴角微微上扬。💕 好感度+3';
  }
  
  // Reset after 3 seconds
  setTimeout(() => {
    rotateDemoDialogue();
  }, 3000);
}

// Particle animation
function createParticles() {
  if (!particlesRef.value) return;
  
  const colors = ['#FF6B9D', '#764ba2', '#667eea', '#fbbf24', '#a78bfa'];
  
  for (let i = 0; i < 30; i++) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    particle.style.left = Math.random() * 100 + '%';
    particle.style.animationDelay = Math.random() * 5 + 's';
    particle.style.animationDuration = (Math.random() * 3 + 2) + 's';
    particle.style.background = colors[Math.floor(Math.random() * colors.length)];
    particlesRef.value.appendChild(particle);
  }
}

// 6 Features
const features = [
  { icon: '🤖', titleKey: 'landing.feature1Title', descKey: 'landing.feature1Desc' },
  { icon: '🔀', titleKey: 'landing.feature2Title', descKey: 'landing.feature2Desc' },
  { icon: '💕', titleKey: 'landing.feature3Title', descKey: 'landing.feature3Desc' },
  { icon: '🖼️', titleKey: 'landing.feature4Title', descKey: 'landing.feature4Desc' },
  { icon: '🧠', titleKey: 'landing.feature5Title', descKey: 'landing.feature5Desc' },
  { icon: '🌐', titleKey: 'landing.feature6Title', descKey: 'landing.feature6Desc' },
];

// 4 Pricing Plans
const steps = [
  { titleKey: 'landing.step1Title', descKey: 'landing.step1Desc' },
  { titleKey: 'landing.step2Title', descKey: 'landing.step2Desc' },
  { titleKey: 'landing.step3Title', descKey: 'landing.step3Desc' },
];

const testimonials = [
  { name: '资深玩家', title: '游戏评论家', rating: 5, text: '这是我玩过的最沉浸的 AI 叙事游戏，每个选择都让我欲罢不能！', avatar: '🎮' },
  { name: '二次元爱好者', title: '剧情党', rating: 5, text: '角色刻画太细腻了，每个角色都有自己的故事线，好感度系统让我更有代入感。', avatar: '🌸' },
  { name: '独立游戏开发者', title: '行业观察者', rating: 5, text: 'AI 驱动的叙事生成技术非常前沿，每次游玩都是独一无二的体验。', avatar: '💻' },
];

function handlePrimaryCta() {
  router.push(auth.isAuthenticated ? '/discover' : '/register');
}

let scrollHandler: (() => void) | null = null;

onMounted(() => {
  // Start rotating subtitle
  rotateSubtitle();
  subtitleRotationInterval = setInterval(() => {
    rotateSubtitle();
  }, 3000);
  
  // Start demo dialogue
  rotateDemoDialogue();
  demoRotationInterval = setInterval(() => {
    rotateDemoDialogue();
  }, 3000);
  
  // Create particles
  createParticles();

  scrollHandler = () => {
    if (starsRef.value) {
      starsRef.value.style.transform = `translateY(${window.scrollY * 0.3}px)`;
    }
  };
  window.addEventListener('scroll', scrollHandler, { passive: true });
});

onUnmounted(() => {
  if (subtitleTypingInterval) clearInterval(subtitleTypingInterval);
  if (subtitleRotationInterval) clearInterval(subtitleRotationInterval);
  if (demoTypingInterval) clearInterval(demoTypingInterval);
  if (demoRotationInterval) clearInterval(demoRotationInterval);
  if (scrollHandler) window.removeEventListener('scroll', scrollHandler);
});
</script>

<style scoped>
.landing-page {
  min-height: 100vh;
  overflow-x: hidden;
  background: var(--bg-main, #0a0a0f);
}

/* Hero */
.hero-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 100px 24px 60px;
  overflow: hidden;
}

.hero-bg-effects {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
  animation: orbFloat 8s ease-in-out infinite;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: #4F46E5;
  top: -100px;
  left: -100px;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: #F472B6;
  bottom: -50px;
  right: -50px;
  animation-delay: 2s;
}

.orb-3 {
  width: 200px;
  height: 200px;
  background: #fbbf24;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: 4s;
}

@keyframes orbFloat {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(20px, -20px); }
}

.star-field {
  position: absolute;
  inset: 0;
  background-image: 
    radial-gradient(2px 2px at 15% 25%, rgba(192,132,252,.6) 0%, transparent 100%),
    radial-gradient(2px 2px at 35% 55%, rgba(249,168,212,.5) 0%, transparent 100%),
    radial-gradient(1px 1px at 55% 15%, rgba(251,191,36,.4) 0%, transparent 100%),
    radial-gradient(2px 2px at 75% 70%, rgba(192,132,252,.5) 0%, transparent 100%),
    radial-gradient(1px 1px at 85% 35%, rgba(249,168,212,.4) 0%, transparent 100%),
    radial-gradient(1px 1px at 25% 80%, rgba(251,191,36,.3) 0%, transparent 100%);
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 800px;
  text-align: center;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  border-radius: 50px;
  background: rgba(167,139,250,.12);
  border: 1px solid rgba(167,139,250,.2);
  color: #a78bfa;
  font-size: 13px;
  margin-bottom: 1rem;
}

.badge-icon {
  font-size: 16px;
}

.hero-title {
  font-size: clamp(32px, 6vw, 56px);
  font-weight: 800;
  line-height: 1.2;
  margin: 0 0 20px;
  background: linear-gradient(135deg, #fff 0%, #a78bfa 50%, #FF6B9D 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: clamp(16px, 2.5vw, 20px);
  color: var(--text-muted, #7c6f9b);
  margin: 0 0 12px;
  line-height: 1.6;
  min-height: 1.6em;
}

.hero-subtitle-en {
  font-size: clamp(14px, 2vw, 16px);
  color: var(--text-muted, #7c6f9b);
  margin: 0 0 32px;
  line-height: 1.6;
  opacity: 0.7;
  font-style: italic;
}

.cursor {
  display: inline-block;
  animation: blink 0.7s step-end infinite;
  color: #a78bfa;
  font-weight: 300;
}

@keyframes blink {
  50% { opacity: 0; }
}

/* Character Preview */
.character-preview {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  background: rgba(167,139,250,.08);
  border: 1px solid rgba(167,139,250,.2);
  border-radius: 16px;
  margin-bottom: 32px;
}

.character-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(192,132,252,.3), rgba(249,168,212,.2));
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-emoji {
  font-size: 28px;
}

.character-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.character-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-main, #f5f3ff);
}

.character-level {
  font-size: 13px;
  color: var(--text-muted, #7c6f9b);
}

.hero-stats {
  display: flex;
  gap: 32px;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 40px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  background: linear-gradient(135deg, #4F46E5, #818CF8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted, #7c6f9b);
  margin-top: 4px;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.social-proof {
  display: flex;
  gap: 2rem;
  justify-content: center;
  flex-wrap: wrap;
  margin: 4rem 0 1rem;
  font-size: 0.85rem;
  color: var(--text-muted, #7c6f9b);
}

.proof-pill {
  padding: 0.5rem 1rem;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 50px;
}

.proof-pill strong {
  color: var(--text-primary, #fff);
}

.cta-primary, .cta-secondary {
  min-height: 52px;
  padding: 14px 32px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
}

.cta-primary {
  background: linear-gradient(135deg, #4F46E5, #818CF8);
  border: none;
  box-shadow: 0 4px 20px rgba(79,70,229,.4);
}

.cta-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(79,70,229,.5);
}

.cta-secondary {
  background: rgba(255,255,255,.08);
  border: 1px solid rgba(167,139,250,.3);
  color: var(--text-main, #f5f3ff);
}

.cta-secondary:hover {
  background: rgba(255,255,255,.12);
  border-color: rgba(167,139,250,.5);
}

/* Demo Box */
.demo-box {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.1);
  border-radius: 16px;
  padding: 1.25rem;
  margin: 3rem auto 2rem;
  max-width: 440px;
  text-align: left;
  backdrop-filter: blur(8px);
}

.demo-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.75rem;
}

.demo-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FF6B9D, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.demo-info {
  display: flex;
  align-items: center;
  gap: 0;
}

.demo-name {
  font-weight: 700;
  font-size: 0.9rem;
  color: #fff;
}

.demo-bond {
  font-size: 0.7rem;
  color: #FF6B9D;
  background: rgba(255,107,157,.15);
  padding: 0.1rem 0.4rem;
  border-radius: 50px;
  margin-left: 0.5rem;
}

.demo-text {
  font-size: 0.9rem;
  color: #aaa;
  min-height: 2.5em;
  line-height: 1.6;
  padding: 0.5rem 0;
  font-style: normal;
}

.demo-choices {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.demo-choice-btn {
  padding: 0.6rem 0.8rem;
  background: rgba(102,126,234,.08);
  border: 1px solid rgba(102,126,234,.25);
  border-radius: 8px;
  color: var(--text-primary, #fff);
  font-size: 0.8rem;
  cursor: pointer;
  transition: 0.2s;
  text-align: left;
  width: auto;
  font-weight: normal;
}

.demo-choice-btn:hover {
  border-color: #667eea;
  background: rgba(102,126,234,.15);
  transform: translateX(3px);
}

.demo-reply {
  color: #4ECDC4;
  font-size: 0.85rem;
  padding: 0.5rem 0;
  margin-top: 0.5rem;
}

/* Section Common */
.section-header {
  text-align: center;
  margin-bottom: 48px;
}

.section-title {
  font-size: clamp(24px, 4vw, 36px);
  font-weight: 800;
  margin: 0 0 12px;
}

.section-desc {
  font-size: 16px;
  color: var(--text-muted, #7c6f9b);
  margin: 0;
}

/* Features - 6 cards, 4-column grid */
.features-section {
  padding: 40px 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.feature-card {
  padding: 32px 24px;
  background: rgba(167,139,250,.05);
  border: 1px solid rgba(167,139,250,.1);
  border-radius: 20px;
  text-align: center;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  background: rgba(167,139,250,.08);
  border-color: rgba(167,139,250,.2);
  box-shadow: 0 12px 40px rgba(139,92,246,.15);
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.feature-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 8px;
  color: var(--text-main, #f5f3ff);
}

.feature-desc {
  font-size: 14px;
  color: var(--text-muted, #7c6f9b);
  margin: 0;
  line-height: 1.6;
}

/* Pricing Section */
.pricing-section {
  padding: 40px 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.pricing-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.pricing-card {
  padding: 32px 24px;
  background: rgba(167,139,250,.05);
  border: 1px solid rgba(167,139,250,.1);
  border-radius: 20px;
  text-align: center;
  transition: all 0.3s ease;
  position: relative;
}

.pricing-card.featured {
  background: rgba(79,70,229,.1);
  border-color: rgba(79,70,229,.3);
  transform: scale(1.05);
}

.pricing-card:hover {
  transform: translateY(-4px);
  border-color: rgba(167,139,250,.3);
  box-shadow: 0 12px 40px rgba(139,92,246,.15);
}

.pricing-card.featured:hover {
  transform: scale(1.05) translateY(-4px);
}

.plan-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  padding: 4px 12px;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
  color: #000;
  white-space: nowrap;
}

.plan-name {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 4px;
  color: var(--text-main, #f5f3ff);
}

.plan-name-en {
  font-size: 14px;
  color: var(--text-muted, #7c6f9b);
  margin-bottom: 16px;
}

.plan-price {
  margin-bottom: 24px;
}

.price-trial {
  display: block;
  font-size: 13px;
  color: #10b981;
  margin-bottom: 8px;
}

.price-amount {
  font-size: 36px;
  font-weight: 800;
  color: var(--text-main, #f5f3ff);
}

.price-period {
  font-size: 14px;
  color: var(--text-muted, #7c6f9b);
}

.plan-features {
  list-style: none;
  padding: 0;
  margin: 0 0 24px;
  text-align: left;
}

.plan-features li {
  padding: 8px 0;
  font-size: 14px;
  color: var(--text-main, #f5f3ff);
  border-bottom: 1px solid rgba(167,139,250,.1);
}

.plan-features li:last-child {
  border-bottom: none;
}

/* Scripts Section */
.scripts-section {
  padding: 40px 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.section-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.view-all-link {
  color: #a78bfa;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.2s;
}

.view-all-link:hover {
  color: #c4b5fd;
}

.scripts-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.script-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.script-card:hover {
  transform: translateY(-4px);
  border-color: rgba(167, 139, 250, 0.3);
  box-shadow: 0 12px 40px rgba(139, 92, 246, 0.15);
}

.script-cover {
  height: 160px;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.2), rgba(236, 72, 153, 0.2));
  display: flex;
  align-items: center;
  justify-content: center;
}

.script-emoji {
  font-size: 64px;
}

.script-info {
  padding: 20px;
}

.script-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main, #f5f3ff);
  margin: 0 0 4px;
}

.script-title-en {
  font-size: 13px;
  color: var(--text-muted, #7c6f9b);
  margin: 0 0 12px;
  font-style: italic;
}

.script-meta {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: var(--text-muted, #7c6f9b);
}

.script-rating {
  color: #fbbf24;
}

.script-routes {
  color: var(--text-muted, #7c6f9b);
}

/* Testimonials */
.testimonials-section {
  padding: 40px 40px;
  max-width: 1100px;
  margin: 0 auto;
}

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
}

.testimonial-card {
  display: flex;
  gap: 20px;
  padding: 24px;
  background: linear-gradient(135deg, rgba(192,216,255,.08) 0%, rgba(167,139,250,.05) 100%);
  border: 1px solid rgba(167,139,250,.12);
  border-radius: 20px;
  text-align: left;
  transition: all 0.3s ease;
}

.testimonial-card:hover {
  transform: translateY(-4px);
  border-color: rgba(167,139,250,.25);
  box-shadow: 0 12px 40px rgba(139,92,246,.12);
}

.testimonial-avatar {
  flex-shrink: 0;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(192,132,252,.2), rgba(249,168,212,.15));
  display: flex;
  align-items: center;
  justify-content: center;
}

.testimonial-content {
  flex: 1;
  min-width: 0;
}

.testimonial-header {
  margin-bottom: 8px;
}

.testimonial-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-main, #f5f3ff);
  margin: 0 0 2px;
}

.testimonial-role {
  font-size: 12px;
  color: var(--text-muted, #7c6f9b);
  margin: 0;
}

.testimonial-rating {
  display: flex;
  gap: 2px;
  margin-bottom: 12px;
}

.star {
  font-size: 14px;
  color: rgba(167,139,250,.3);
}

.star.filled {
  color: #fbbf24;
}

.testimonial-text {
  font-size: 14px;
  color: var(--text-main, #f5f3ff);
  line-height: 1.6;
  margin: 0;
}

/* How It Works */
.how-section {
  padding: 40px 40px;
  max-width: 700px;
  margin: 0 auto;
}

.steps-container {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 24px;
  position: relative;
}

.step-number {
  font-size: 48px;
  font-weight: 800;
  background: linear-gradient(135deg, rgba(192,132,252,.4), rgba(249,168,212,.3));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  flex-shrink: 0;
  min-width: 60px;
  text-align: center;
}

.step-content {
  flex: 1;
  padding-top: 8px;
}

.step-title {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 8px;
  color: var(--text-main, #f5f3ff);
}

.step-desc {
  font-size: 15px;
  color: var(--text-muted, #7c6f9b);
  margin: 0;
  line-height: 1.6;
}

.step-connector {
  position: absolute;
  left: 30px;
  bottom: -32px;
  width: 2px;
  height: 32px;
  background: linear-gradient(to bottom, rgba(192,132,252,.3), transparent);
}

/* CTA */
.cta-section {
  padding: 80px 24px;
  display: flex;
  justify-content: center;
}

.cta-card {
  max-width: 600px;
  width: 100%;
  padding: 48px 32px;
  background: rgba(167,139,250,.05);
  border: 1px solid rgba(167,139,250,.15);
  border-radius: 24px;
  text-align: center;
}

.cta-title {
  font-size: clamp(24px, 4vw, 32px);
  font-weight: 800;
  margin: 0 0 16px;
}

.cta-desc {
  font-size: 16px;
  color: var(--text-muted, #7c6f9b);
  margin: 0 0 32px;
}

.cta-final-btn {
  min-height: 52px;
  padding: 14px 40px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #4F46E5, #818CF8);
  border: none;
  box-shadow: 0 4px 20px rgba(79,70,229,.4);
  margin-bottom: 24px;
}

.cta-final-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(79,70,229,.5);
}

.social-links {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.social-link {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(167,139,250,.1);
  border: 1px solid rgba(167,139,250,.2);
  border-radius: 50%;
  font-size: 20px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.social-link:hover {
  background: rgba(167,139,250,.2);
  border-color: rgba(167,139,250,.4);
  transform: translateY(-2px);
}

/* Footer */
.landing-footer {
  text-align: center;
  padding: 24px;
  border-top: 1px solid rgba(167,139,250,.1);
  color: var(--text-muted, #7c6f9b);
  font-size: 13px;
}

.landing-footer p {
  margin: 0;
}

/* Scroll Reveal */
.reveal, .reveal-left, .reveal-right, .reveal-scale {
  opacity: 0;
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.reveal {
  transform: translateY(30px);
}

.reveal-left {
  transform: translateX(-30px);
}

.reveal-right {
  transform: translateX(30px);
}

.reveal-scale {
  transform: scale(0.9);
}

.reveal.revealed, .reveal-left.revealed, .reveal-right.revealed, .reveal-scale.revealed {
  opacity: 1;
  transform: none;
}

/* Fade-in */
.fade-in-up {
  opacity: 0;
  transform: translateY(20px);
  animation: fadeInUp 0.6s ease forwards;
}

.delay-1 { animation-delay: 0.1s; }
.delay-2 { animation-delay: 0.2s; }
.delay-3 { animation-delay: 0.3s; }
.delay-4 { animation-delay: 0.4s; }

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Float */
.float {
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

/* Mobile ≤767px */
@media (max-width: 767px) {
  .hero-section {
    padding: 80px 16px 40px;
    min-height: auto;
  }

  .hero-badge {
    padding: 6px 16px;
    font-size: 13px;
    margin-bottom: 20px;
  }

  .hero-title {
    font-size: clamp(28px, 8vw, 40px);
    margin-bottom: 16px;
  }

  .hero-subtitle {
    font-size: 15px;
    margin-bottom: 24px;
  }

  .character-preview {
    padding: 10px 16px;
    margin-bottom: 24px;
  }

  .character-avatar {
    width: 40px;
    height: 40px;
  }

  .avatar-emoji {
    font-size: 24px;
  }

  .hero-stats {
    gap: 16px;
    margin-bottom: 32px;
  }

  .stat-value {
    font-size: 18px;
  }

  .stat-label {
    font-size: 11px;
  }

  .hero-actions {
    flex-direction: column;
    gap: 12px;
    margin-bottom: 40px;
  }

  .cta-primary, .cta-secondary {
    width: 100%;
    min-height: 52px;
    font-size: 16px;
  }

  .features-section, .pricing-section, .testimonials-section, .how-section {
    padding: 60px 16px;
  }

  .section-header {
    margin-bottom: 32px;
  }

  .section-title {
    font-size: 24px;
  }

  .section-desc {
    font-size: 14px;
  }

  /* Features: 2 columns on mobile */
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .feature-card {
    padding: 20px 16px;
  }

  .feature-icon {
    font-size: 36px;
  }

  .feature-title {
    font-size: 14px;
  }

  .feature-desc {
    font-size: 12px;
  }

  /* Pricing: single column on mobile */
  .pricing-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .pricing-card.featured {
    transform: none;
  }

  .pricing-card.featured:hover {
    transform: translateY(-4px);
  }

  .plan-name {
    font-size: 18px;
  }

  .price-amount {
    font-size: 32px;
  }

  /* Testimonials: single column */
  .testimonials-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  /* Scripts: single column on mobile */
  .scripts-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .section-header-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .testimonial-card {
    padding: 20px;
    gap: 16px;
  }

  .testimonial-avatar {
    width: 56px;
    height: 56px;
  }

  .testimonial-name {
    font-size: 15px;
  }

  .testimonial-text {
    font-size: 13px;
  }

  /* Steps */
  .steps-container {
    gap: 24px;
  }

  .step-item {
    gap: 16px;
  }

  .step-number {
    font-size: 36px;
    min-width: 48px;
  }

  .step-title {
    font-size: 17px;
  }

  .step-desc {
    font-size: 14px;
  }

  .step-connector {
    left: 24px;
    bottom: -24px;
    height: 24px;
  }

  /* CTA */
  .cta-section {
    padding: 60px 16px;
  }

  .cta-card {
    padding: 32px 20px;
  }

  .cta-title {
    font-size: 22px;
  }

  .cta-desc {
    font-size: 14px;
    margin-bottom: 24px;
  }

  .cta-final-btn {
    width: 100%;
    min-height: 52px;
  }

  .social-link {
    width: 48px;
    height: 48px;
    font-size: 22px;
  }

  .landing-footer {
    padding: 20px 16px;
  }
}

/* Tablet 768-1023px */
@media (min-width: 768px) and (max-width: 1023px) {
  /* Features: 3 columns on tablet */
  .features-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  /* Pricing: 2 columns on tablet */
  .pricing-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .testimonials-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Desktop ≥1024px */
@media (min-width: 1024px) {
  .hero-section {
    padding: 120px 40px 80px;
  }

  .features-section, .pricing-section, .testimonials-section, .how-section {
    padding: 40px 40px;
  }

  .feature-card:hover {
    transform: translateY(-8px);
  }

  .testimonial-card:hover {
    transform: translateY(-8px);
  }
}

/* Touch-friendly */
@media (pointer: coarse) {
  .cta-primary, .cta-secondary, .cta-final-btn, .social-link {
    min-height: 48px;
  }
}
</style>