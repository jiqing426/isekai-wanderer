<template>
  <div class="cg-unlock-card" :class="[`rarity-${rarity}`]">
    <div class="card-inner">
      <!-- 稀有度标签 -->
      <div class="rarity-badge">
        <span class="rarity-text">{{ rarity }}</span>
      </div>

      <!-- CG 图片容器 -->
      <div class="image-container">
        <div class="image-wrapper">
          <img v-if="image" :src="image" :alt="title" class="cg-image" />
          <div v-else class="cg-placeholder">
            <span class="placeholder-icon">🖼️</span>
          </div>
        </div>
        <!-- 高光扫过效果 -->
        <div class="highlight-sweep"></div>
      </div>

      <!-- 文字信息 -->
      <div class="info-section">
        <div class="unlock-label">CG 已解锁</div>
        <h3 class="cg-title">{{ title }}</h3>
        <p v-if="description" class="cg-description">{{ description }}</p>
      </div>

      <!-- 按钮组 -->
      <div class="button-group">
        <button class="btn-view" @click="$emit('view')">
          立即查看
        </button>
        <button class="btn-later" @click="$emit('later')">
          稍后
        </button>
      </div>
    </div>

    <!-- 粒子效果 -->
    <div class="particles">
      <span v-for="i in 12" :key="i" class="particle" :style="particleStyle(i)"></span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Rarity } from '@/types/unlock'

defineProps<{
  title: string
  description?: string
  image?: string
  rarity: Rarity
}>()

defineEmits<{
  (e: 'view'): void
  (e: 'later'): void
}>()

function particleStyle(index: number) {
  const angle = (index / 12) * 360
  const delay = index * 0.1
  return {
    '--angle': `${angle}deg`,
    '--delay': `${delay}s`
  }
}
</script>

<style scoped>
.cg-unlock-card {
  position: relative;
  width: 320px;
  max-width: 90vw;
  perspective: 1000px;
}

.card-inner {
  position: relative;
  background: linear-gradient(135deg, rgba(20, 20, 40, 0.95), rgba(30, 30, 50, 0.95));
  border-radius: 16px;
  padding: 20px;
  overflow: hidden;
  animation: cardSlideIn 400ms cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
  transform: translateY(100px) scale(0.8);
  opacity: 0;
}

@keyframes cardSlideIn {
  0% {
    transform: translateY(100px) scale(0.8);
    opacity: 0;
  }
  100% {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

/* 稀有度边框 */
.rarity-R .card-inner {
  border: 2px solid #4a9eff;
  box-shadow: 0 0 20px rgba(74, 158, 255, 0.3);
}

.rarity-SR .card-inner {
  border: 2px solid #a855f7;
  box-shadow: 0 0 20px rgba(168, 85, 247, 0.3);
}

.rarity-SSR .card-inner {
  border: 2px solid #ffd700;
  box-shadow: 0 0 30px rgba(255, 215, 0, 0.4);
}

/* 稀有度标签 */
.rarity-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 12px;
  z-index: 10;
}

.rarity-R .rarity-badge {
  background: linear-gradient(135deg, #4a9eff, #2563eb);
  color: #fff;
}

.rarity-SR .rarity-badge {
  background: linear-gradient(135deg, #a855f7, #7c3aed);
  color: #fff;
}

.rarity-SSR .rarity-badge {
  background: linear-gradient(135deg, #ffd700, #ffaa00);
  color: #1a1a2e;
}

/* 图片容器 */
.image-container {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 16px;
}

.image-wrapper {
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3);
}

.cg-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  animation: imageReveal 500ms ease forwards;
  filter: blur(10px);
}

@keyframes imageReveal {
  0% {
    filter: blur(10px);
    opacity: 0.5;
  }
  100% {
    filter: blur(0);
    opacity: 1;
  }
}

.cg-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(74, 158, 255, 0.1), rgba(168, 85, 247, 0.1));
}

.placeholder-icon {
  font-size: 48px;
  opacity: 0.5;
}

/* 高光扫过效果 */
.highlight-sweep {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  animation: sweepHighlight 1.5s ease 0.5s;
}

@keyframes sweepHighlight {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}

/* 信息区域 */
.info-section {
  text-align: center;
  margin-bottom: 20px;
}

.unlock-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 8px;
  opacity: 0;
  animation: fadeIn 600ms ease 0.6s forwards;
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}

.cg-title {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px 0;
  opacity: 0;
  animation: fadeIn 600ms ease 0.7s forwards;
}

.cg-description {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  line-height: 1.5;
  opacity: 0;
  animation: fadeIn 600ms ease 0.8s forwards;
}

/* 按钮组 */
.button-group {
  display: flex;
  gap: 12px;
  opacity: 0;
  animation: fadeIn 400ms ease 0.8s forwards;
}

.btn-view {
  flex: 1;
  padding: 12px 24px;
  background: linear-gradient(135deg, #ffd700, #ffaa00);
  border: none;
  border-radius: 8px;
  color: #1a1a2e;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 200ms ease;
}

.btn-view:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 215, 0, 0.4);
}

.btn-later {
  flex: 1;
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 200ms ease;
}

.btn-later:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

/* 粒子效果 */
.particles {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  pointer-events: none;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: #ffd700;
  border-radius: 50%;
  animation: particleFloat 2s ease-in-out infinite;
  animation-delay: var(--delay);
}

@keyframes particleFloat {
  0%, 100% {
    transform: translate(0, 0) scale(0);
    opacity: 0;
  }
  50% {
    opacity: 1;
    transform: 
      translate(
        calc(cos(var(--angle)) * 80px),
        calc(sin(var(--angle)) * 80px)
      )
      scale(1);
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .cg-unlock-card {
    width: 280px;
  }

  .cg-title {
    font-size: 18px;
  }

  .button-group {
    flex-direction: column;
  }
}
</style>
