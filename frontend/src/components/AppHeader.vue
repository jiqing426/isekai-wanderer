<template>
  <header class="app-header" :class="{ 'header-scrolled': isScrolled }">
    <div class="header-inner">
      <!-- Mobile Menu Toggle (left side on mobile) -->
      <button class="mobile-menu-toggle" @click="toggleMobileMenu">
        <span class="hamburger" :class="{ open: mobileMenuOpen }">
          <span></span>
          <span></span>
          <span></span>
        </span>
      </button>

      <!-- Logo -->
      <a href="/" class="header-logo" @click.prevent="goHome">
        <span class="logo-icon">✦</span>
        <span class="logo-text">{{ $t("common.appName") }}</span>
      </a>

      <!-- Desktop Navigation -->
      <nav class="header-nav desktop-nav">
        <!-- FE-O26: 未登录也展示所有 tab，点击需登录的 tab 时跳转登录页 -->
        <a
          v-for="tab in navTabs"
          :key="tab.path"
          :href="tab.path"
          class="nav-link"
          :class="{ active: isActive(tab.path) }"
          @click.prevent="handleNavClick(tab)"
        >
          <span class="nav-icon">{{ tab.icon }}</span>
          <span>{{ tab.label }}</span>
        </a>
      </nav>

      <!-- Right Tools -->
      <div class="header-tools">
        <!-- Language Switch -->
        <n-dropdown :options="langOptions" @select="handleLangSelect">
          <n-button quaternary size="small" class="tool-btn">
            <span class="lang-icon">🌐</span>
            <span class="tool-label">{{ currentLangLabel }}</span>
          </n-button>
        </n-dropdown>

        <!-- User Menu (Logged In) -->
        <template v-if="isAuthenticated">
          <n-dropdown :options="userOptions" @select="handleUserSelect">
            <n-button quaternary size="small" class="tool-btn user-btn">
              <div class="user-avatar-small">
                <img v-if="auth.user?.avatar && !headerAvatarFailed" :src="auth.user.avatar" :alt="userInitial" class="user-avatar-img" @error="headerAvatarFailed = true" />
                <span v-else>{{ userInitial }}</span>
              </div>
            </n-button>
          </n-dropdown>
        </template>
        <!-- Login/Register Buttons (Not Logged In) -->
        <template v-else>
          <router-link to="/login" class="login-btn desktop-only">
            {{ $t('auth.login') }}
          </router-link>
          <router-link to="/register" class="register-btn desktop-only">
            {{ $t('auth.register') }}
          </router-link>
        </template>
      </div>
    </div>

    <!-- Mobile Navigation Menu -->
    <transition name="slide-down">
      <div v-if="mobileMenuOpen" class="mobile-nav">
        <!-- FE-O26: 未登录也展示所有 tab -->
        <a
          v-for="tab in navTabs"
          :key="'m-' + tab.path"
          :href="tab.path"
          class="mobile-nav-link"
          @click.prevent="handleNavClick(tab, true)"
        >
          <span class="nav-icon">{{ tab.icon }}</span>
          <span>{{ tab.label }}</span>
        </a>
        <div class="mobile-nav-divider"></div>
        <template v-if="isAuthenticated">
          <router-link to="/personal-center" class="mobile-nav-link" @click="closeMobileMenu">
            <span class="nav-icon">👤</span>
            <span>{{ $t('nav.profile') }}</span>
          </router-link>
          <router-link to="/settings" class="mobile-nav-link" @click="closeMobileMenu">
            <span class="nav-icon">⚙️</span>
            <span>{{ $t('nav.settings') }}</span>
          </router-link>
        </template>
        <template v-else>
          <router-link to="/login" class="mobile-nav-link" @click="closeMobileMenu">
            <span class="nav-icon">🔑</span>
            <span>{{ $t('auth.login') }}</span>
          </router-link>
          <router-link to="/register" class="mobile-nav-link" @click="closeMobileMenu">
            <span class="nav-icon">✨</span>
            <span>{{ $t('auth.register') }}</span>
          </router-link>
        </template>
      </div>
    </transition>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/stores/auth';

const { t, locale } = useI18n();
const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

const isScrolled = ref(false);
const mobileMenuOpen = ref(false);
const headerAvatarFailed = ref(false);

const isAuthenticated = computed(() => auth.isAuthenticated);
const userInitial = computed(() => {
  const name = auth.user?.displayName || auth.user?.email || '';
  return name.charAt(0).toUpperCase();
});

// FE-O26: 导航 tabs 配置
const navTabs = computed(() => [
  { path: '/discover', icon: '📚', label: t('nav.scripts'), requiresAuth: false },
  { path: '/character-chat', icon: '💬', label: '角色聊天', requiresAuth: true },
  { path: '/gallery', icon: '🖼️', label: t('nav.gallery'), requiresAuth: true },
  { path: '/fragment', icon: '💠', label: t('nav.fragment'), requiresAuth: true },
  { path: '/subscribe', icon: '⭐', label: t('nav.subscription'), requiresAuth: true },
  { path: '/community', icon: '🌐', label: t('nav.community'), requiresAuth: false },
]);

// FE-O26: 处理导航点击，未登录时跳转登录页
function handleNavClick(tab: { path: string; requiresAuth: boolean }, isMobile = false) {
  if (tab.requiresAuth && !isAuthenticated.value) {
    // 未登录，跳转登录页
    router.push({ path: '/login', query: { redirect: tab.path } });
  } else {
    // 已登录或无需登录，直接跳转
    router.push(tab.path);
  }
  if (isMobile) {
    closeMobileMenu();
  }
}

const currentLangLabel = computed(() => {
  const map: Record<string, string> = { 'zh-CN': '中', 'en-US': 'EN', 'ja-JP': '日' };
  return map[locale.value] || locale.value.slice(0, 2).toUpperCase();
});

const langOptions = [
  { label: '🇨🇳 中文', key: 'zh-CN' },
  { label: '🇺🇸 English', key: 'en-US' },
  { label: '🇯🇵 日本語', key: 'ja-JP' },
];

const userOptions = [
  { label: () => t('nav.profile'), key: 'profile' },
  { label: () => t('nav.settings'), key: 'settings' },
  { type: 'divider', key: 'd1' },
  { label: () => t('common.logout'), key: 'logout' },
];

function isActive(path: string): boolean {
  return route.path === path || route.path.startsWith(path + '/');
}

function goHome() {
  router.push('/');
}

function handleLangSelect(key: string) {
  locale.value = key;
  localStorage.setItem('locale', key);
}

function handleUserSelect(key: string) {
  if (key === 'logout') {
    auth.logout();
    router.push('/login');
  } else if (key === 'profile') {
    router.push('/personal-center');
  } else if (key === 'settings') {
    router.push('/settings');
  }
}

function toggleMobileMenu() {
  mobileMenuOpen.value = !mobileMenuOpen.value;
}

function closeMobileMenu() {
  mobileMenuOpen.value = false;
}

function onScroll() {
  isScrolled.value = window.scrollY > 10;
}

onMounted(() => {
  window.addEventListener('scroll', onScroll);
});

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll);
});
</script>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(10, 10, 15, 0.85);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(167, 139, 250, 0.1);
  transition: all 0.3s ease;
}

.header-scrolled {
  background: rgba(10, 10, 15, 0.95);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.header-inner {
  max-width: 1600px;
  margin: 0 auto;
  height: 72px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 32px;
}

/* Logo */
.header-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  flex-shrink: 0;
}

.logo-icon {
  font-size: 28px;
  color: #a78bfa;
  filter: drop-shadow(0 0 12px rgba(167, 139, 250, 0.4));
}

.logo-text {
  font-family: 'Source Han Serif SC', 'Songti SC', 'STSong', Georgia, 'Times New Roman', serif;
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #fff 0%, #a78bfa 50%, #FF6B9D 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  white-space: nowrap;
}

/* Desktop Navigation */
.desktop-nav {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 12px;
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
  transition: all 0.2s ease;
  white-space: nowrap;
}

.nav-link:hover {
  color: #fff;
  background: rgba(167, 139, 250, 0.1);
}

.nav-link.active {
  color: #fff;
  background: rgba(167, 139, 250, 0.15);
  font-weight: 600;
}

.nav-icon {
  font-size: 18px;
}

/* Right Tools */
.header-tools {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.tool-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px !important;
  border-radius: 10px !important;
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: rgba(255, 255, 255, 0.8) !important;
  transition: all 0.2s ease;
}

.tool-btn:hover {
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(167, 139, 250, 0.3) !important;
  color: #fff !important;
}

.lang-icon {
  font-size: 16px;
}

.tool-label {
  font-size: 13px;
  font-weight: 600;
}

.user-btn {
  padding: 0 !important;
  margin: 0 !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  min-width: auto !important;
  min-height: auto !important;
  width: auto !important;
  height: auto !important;
}

.user-btn:hover {
  background: transparent !important;
}

.user-btn:focus {
  background: transparent !important;
}

.user-avatar-small {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #a78bfa, #FF6B9D);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  overflow: hidden;
}

.user-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Login/Register Buttons */
.login-btn,
.register-btn {
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.login-btn {
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.login-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(167, 139, 250, 0.3);
}

.register-btn {
  color: #fff;
  background: linear-gradient(135deg, #a78bfa, #FF6B9D);
  border: 1px solid transparent;
}

.register-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(167, 139, 250, 0.3);
}

/* Mobile Menu Toggle */
.mobile-menu-toggle {
  display: none;
  background: transparent;
  border: none;
  padding: 8px;
  cursor: pointer;
  flex-shrink: 0;
}

.hamburger {
  display: flex;
  flex-direction: column;
  gap: 5px;
  width: 24px;
}

.hamburger span {
  display: block;
  height: 2px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 2px;
  transition: all 0.3s ease;
}

.hamburger.open span:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}

.hamburger.open span:nth-child(2) {
  opacity: 0;
}

.hamburger.open span:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

/* Mobile Navigation */
.mobile-nav {
  display: none;
  flex-direction: column;
  padding: 16px 24px;
  background: rgba(10, 10, 15, 0.98);
  border-top: 1px solid rgba(167, 139, 250, 0.1);
}

.mobile-nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 12px;
  text-decoration: none;
  font-size: 16px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  transition: all 0.2s ease;
}

.mobile-nav-link:hover {
  background: rgba(167, 139, 250, 0.1);
  color: #fff;
}

.mobile-nav-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 8px 0;
}

/* Slide Down Animation */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Responsive */
@media (max-width: 767px) {
  .header-inner {
    padding: 0 16px;
    gap: 12px;
    justify-content: space-between;
  }

  /* Mobile layout: 菜单按钮 | Logo | 头像 */
  .mobile-menu-toggle {
    display: block;
    order: 1;
  }

  .header-logo {
    order: 2;
    flex: 0 0 auto;
  }

  .header-tools {
    order: 3;
  }

  .logo-text {
    font-size: 16px;
  }

  .desktop-nav {
    display: none;
  }

  .mobile-nav {
    display: flex;
  }

  .tool-label {
    display: none;
  }

  .tool-btn {
    padding: 8px !important;
  }

  /* Hide desktop login/register buttons on mobile */
  .desktop-only {
    display: none;
  }
}
</style>
