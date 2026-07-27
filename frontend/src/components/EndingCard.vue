<template>
  <div class="ending-card" :class="[endingType]">
    <div class="card-inner">
      <div class="card-header">
        <span class="ending-badge" :class="endingType">
          {{ badgeText }}
        </span>
      </div>
      <h2 class="ending-title">{{ title }}</h2>
      <p class="ending-desc">{{ description }}</p>
      <blockquote v-if="monologue" class="ending-quote">
        "{{ monologue }}"
      </blockquote>
      <div v-if="cgImage" class="ending-cg">
        <img :src="cgImage" alt="CG" class="cg-img" />
      </div>
      <div v-if="stats" class="ending-stats">
        <div class="stat">
          <span class="stat-num">{{ stats.choices }}</span>
          <span class="stat-lbl">选择</span>
        </div>
        <div class="stat">
          <span class="stat-num">{{ stats.finalAffection }}</span>
          <span class="stat-lbl">好感</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

export type EndingType = 'good' | 'bad' | 'normal' | 'true_end' | 'hidden';

const props = defineProps<{
  title: string;
  description: string;
  endingType: EndingType;
  monologue?: string;
  cgImage?: string;
  stats?: { choices: number; finalAffection: number };
}>();

const BADGE_MAP: Record<EndingType, string> = {
  good: '✦ 好结局',
  bad: '✧ 坏结局',
  normal: '◈ 普通结局',
  true_end: '★ 真结局',
  hidden: '✦ 隐藏结局',
};

const badgeText = computed(() => BADGE_MAP[props.endingType] || props.endingType);
</script>

<style scoped>
.ending-card {
  border-radius: 20px;
  overflow: hidden;
  background: var(--glass-bg, rgba(15, 10, 26, 0.85));
  backdrop-filter: blur(20px);
  border: 1px solid rgba(167, 139, 250, 0.12);
}
.ending-card.good {
  border-color: rgba(192, 132, 252, 0.25);
  box-shadow: 0 0 40px rgba(192, 132, 252, 0.08);
}
.ending-card.bad {
  border-color: rgba(252, 165, 165, 0.2);
  box-shadow: 0 0 40px rgba(252, 165, 165, 0.06);
}
.ending-card.normal {
  border-color: rgba(148, 163, 184, 0.2);
  box-shadow: 0 0 40px rgba(148, 163, 184, 0.06);
}
.ending-card.true_end {
  border-color: rgba(251, 191, 36, 0.3);
  box-shadow: 0 0 40px rgba(251, 191, 36, 0.1);
}
.ending-card.hidden {
  border-color: rgba(139, 92, 246, 0.3);
  box-shadow: 0 0 40px rgba(139, 92, 246, 0.12);
  background: linear-gradient(135deg, rgba(15, 10, 26, 0.9), rgba(30, 20, 50, 0.9));
}

.card-inner { padding: 28px; }
.card-header { margin-bottom: 16px; }
.ending-badge {
  display: inline-block;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}
.ending-badge.good { background: rgba(192, 132, 252, 0.15); color: var(--brand-primary); }
.ending-badge.bad { background: rgba(252, 165, 165, 0.12); color: #fca5a5; }
.ending-badge.normal { background: rgba(148, 163, 184, 0.12); color: #94a3b8; }
.ending-badge.true_end { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }
.ending-badge.hidden { background: rgba(139, 92, 246, 0.2); color: #a78bfa; }

.ending-title { font-size: 22px; font-weight: 700; color: var(--text-main); margin: 0 0 10px; }
.ending-desc { color: var(--text-muted); font-size: 14px; line-height: 1.6; margin: 0; }
.ending-quote {
  margin: 20px 0 0;
  padding: 14px 18px;
  border-left: 3px solid var(--brand-primary);
  background: rgba(192, 132, 252, 0.04);
  border-radius: 0 12px 12px 0;
  font-style: italic;
  color: #c4b5fd;
  font-size: 14px;
  line-height: 1.6;
}
.ending-cg { margin-top: 20px; border-radius: 12px; overflow: hidden; }
.cg-img { width: 100%; display: block; }
.ending-stats {
  display: flex;
  gap: 24px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(167, 139, 250, 0.1);
}
.stat { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.stat-num { font-size: 20px; font-weight: 700; color: var(--brand-primary); font-variant-numeric: tabular-nums; }
.stat-lbl { font-size: 12px; color: var(--text-muted); }
</style>
