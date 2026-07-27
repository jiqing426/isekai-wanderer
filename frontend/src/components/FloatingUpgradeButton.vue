<template>
  <div class="floating-upgrade-button" @click="handleUpgrade">
    <span class="upgrade-icon">💎</span>
    <span class="upgrade-text">升级会员</span>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

const handleUpgrade = () => {
  router.push('/subscription');
};
</script>

<style scoped>
.floating-upgrade-button {
  position: fixed;
  right: 24px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 12px;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.9), rgba(236, 72, 153, 0.9));
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 20px rgba(167, 139, 250, 0.4);
  z-index: 100;
}

.floating-upgrade-button:hover {
  transform: translateY(-50%) scale(1.05);
  box-shadow: 0 6px 24px rgba(167, 139, 250, 0.5);
}

.upgrade-icon {
  font-size: 24px;
}

.upgrade-text {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  writing-mode: vertical-rl;
  text-orientation: upright;
  letter-spacing: 2px;
}

@media (max-width: 768px) {
  .floating-upgrade-button {
    right: 16px;
    padding: 12px 10px;
  }

  .upgrade-icon {
    font-size: 20px;
  }

  .upgrade-text {
    font-size: 12px;
  }
}
</style>
