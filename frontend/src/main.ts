import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { createHead } from '@vueuse/head';
import App from './App.vue';
import router from './router';
import { i18n } from './i18n';
import './styles/mobile.css';

const app = createApp(App);
const head = createHead();
app.use(createPinia());

app.use(router);
// naive-ui 全局注册（App.vue 使用了全局 provider 组件）
import naive from 'naive-ui';
app.use(naive);
app.use(i18n);
app.use(head);
app.mount('#app');

// Register service worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {
      // SW registration failed silently
    });
  });
}
