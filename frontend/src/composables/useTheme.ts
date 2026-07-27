import { ref, watch } from 'vue';

export type ThemeMode = 'dark' | 'light';

const STORAGE_KEY = 'theme-mode';

function getSavedTheme(): ThemeMode {
  if (typeof window === 'undefined') return 'dark';
  // Support both old (stores/theme.ts 'theme' key) and new ('theme-mode' key) for backward compat
  const saved = localStorage.getItem(STORAGE_KEY) || localStorage.getItem('theme');
  if (saved === 'light') return 'light';
  return 'dark';
}

export const themeMode = ref<ThemeMode>(getSavedTheme());

export function toggleTheme() {
  themeMode.value = themeMode.value === 'dark' ? 'light' : 'dark';
}

export function setTheme(mode: ThemeMode) {
  themeMode.value = mode;
}

watch(themeMode, (mode) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(STORAGE_KEY, mode);
    localStorage.setItem('theme', mode); // backward compat with stores/theme.ts
    applyTheme(mode);
  }
}, { immediate: true });

function applyTheme(mode: ThemeMode) {
  const root = document.documentElement;
  root.setAttribute('data-theme', mode);

  // Toggle the .dark class so html:not(.dark) and html.dark selectors work in global.css
  root.classList.toggle('dark', mode === 'dark');

  if (mode === 'light') {
    root.style.setProperty('--bg-primary', '#ffffff');
    root.style.setProperty('--bg-secondary', '#f8f9fa');
    root.style.setProperty('--bg-card', 'rgba(255, 255, 255, 0.95)');
    root.style.setProperty('--text-main', '#1a1a2e');
    root.style.setProperty('--text-muted', '#6c757d');
    root.style.setProperty('--text-subtle', '#adb5bd');
    root.style.setProperty('--border-color', 'rgba(0, 0, 0, 0.08)');
    root.style.setProperty('--glass-bg', 'rgba(255, 255, 255, 0.8)');
    root.style.setProperty('--glass-border', 'rgba(0, 0, 0, 0.06)');
    root.style.setProperty('--header-bg', 'rgba(255, 255, 255, 0.85)');
    root.style.setProperty('--page-bg-start', '#f8f9fa');
    root.style.setProperty('--page-bg-end', '#e9ecef');
    root.style.setProperty('--card-shadow', '0 4px 24px rgba(0, 0, 0, 0.06)');
    root.style.setProperty('--brand-primary', '#4F46E5');
    root.style.setProperty('--brand-secondary', '#F472B6');
    root.style.setProperty('--brand-accent', '#fbbf24');
    root.style.setProperty('--input-bg', '#ffffff');
    root.style.setProperty('--input-text', '#1a1a2e');
    root.style.setProperty('--input-border', 'rgba(0, 0, 0, 0.15)');
    root.style.setProperty('--nav-hover-bg', 'rgba(0, 0, 0, 0.06)');
    root.style.setProperty('--nav-active-bg', 'rgba(79, 70, 229, 0.08)');
    root.style.setProperty('--nav-active-color', '#4F46E5');
  } else {
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
}
