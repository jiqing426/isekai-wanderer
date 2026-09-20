import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useThemeStore = defineStore('theme', () => {
  // 强制暗色模式
  const isDark = ref(true);

  function toggle() {
    // 禁用切换，始终为暗色
    isDark.value = true;
    localStorage.setItem('theme', 'dark');
    document.documentElement.classList.add('dark');
  }

  function init() {
    // 初始化时强制暗色
    isDark.value = true;
    localStorage.setItem('theme', 'dark');
    document.documentElement.classList.add('dark');
  }

  return { isDark, toggle, init };
});
