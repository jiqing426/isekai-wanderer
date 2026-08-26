import { ref, watch } from 'vue';

export type ThemeMode = 'dark' | 'light';

const STORAGE_KEY = 'theme-mode';

// 强制暗色模式
export const themeMode = ref<ThemeMode>('dark');

export function toggleTheme() {
  // 禁用切换，始终为暗色
  themeMode.value = 'dark';
}

export function setTheme(mode: ThemeMode) {
  // 强制暗色模式
  themeMode.value = 'dark';
}

watch(themeMode, (mode) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(STORAGE_KEY, 'dark');
    localStorage.setItem('theme', 'dark');
    applyTheme('dark');
  }
}, { immediate: true });

function applyTheme(mode: ThemeMode) {
  const root = document.documentElement;
  root.setAttribute('data-theme', 'dark');
  root.classList.add('dark');
  
  // 始终应用暗色主题
  root.style.setProperty('--bg-primary', '#0f0a1a');
  root.style.setProperty('--bg-secondary', '#1a1625');
  root.style.setProperty('--bg-card', 'rgba(15, 10, 26, 0.85)');
  root.style.setProperty('--text-main', '#f5f3ff');
  root.style.setProperty('--text-muted', '#7c6f9b');
  root.style.setProperty('--text-subtle', '#4a4458');
  root.style.setProperty('--border-color', 'rgba(167, 139, 250, 0.12)');
  root.style.setProperty('--glass-bg', 'rgba(15, 10, 26, 0.85)');
  root.style.setProperty('--glass-border', 'rgba(167, 139, 250, 0.12)');
  root.style.setProperty('--header-bg', 'rgba(15, 10, 26, 0.85)');
  root.style.setProperty('--page-bg-start', '#0f0a1a');
  root.style.setProperty('--page-bg-end', '#1a1625');
  root.style.setProperty('--card-shadow', '0 24px 64px rgba(0, 0, 0, 0.4)');
  root.style.setProperty('--brand-primary', '#4F46E5');
  root.style.setProperty('--brand-secondary', '#F472B6');
  root.style.setProperty('--brand-accent', '#fbbf24');
  root.style.setProperty('--input-bg', 'rgba(15, 10, 26, 0.6)');
  root.style.setProperty('--input-text', '#f1f5f9');
  root.style.setProperty('--input-border', 'rgba(167, 139, 250, 0.2)');
  root.style.setProperty('--nav-hover-bg', 'rgba(167, 139, 250, 0.08)');
  root.style.setProperty('--nav-active-bg', 'rgba(167, 139, 250, 0.12)');
  root.style.setProperty('--nav-active-color', '#818CF8');
}
