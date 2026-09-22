<template>
  <header class="game-header">
    <button class="back-btn" @click="router.back()">{{ $t('gameHeader.back') }}</button>
    <h1 class="game-title">{{ scriptTitle }}</h1>
    <button class="settings-btn" @click="openSettings">⚙️</button>
  </header>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const router = useRouter();

interface Props {
  scriptTitle?: string;
}

withDefaults(defineProps<Props>(), {
  scriptTitle: t('gameHeader.inProgress')
});

function openSettings() {
  // TODO: 打开设置面板
}
</script>

<style scoped>
.game-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 48px;
  background: rgba(15, 10, 26, 0.85);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(167, 139, 250, 0.12);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  z-index: 1000;
}

.back-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: rgba(167, 139, 250, 0.1);
  color: #fff;
}

.game-title {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin: 0;
  flex: 1;
  text-align: center;
}

.settings-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  font-size: 18px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.settings-btn:hover {
  background: rgba(167, 139, 250, 0.1);
  color: #fff;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .game-header {
    padding: 0 12px;
  }

  .back-btn,
  .settings-btn {
    padding: 8px;
  }

  .game-title {
    font-size: 14px;
  }
}
</style>
