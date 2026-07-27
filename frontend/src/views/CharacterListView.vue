<template>
  <div class="page-bg">
    <div class="character-list-page">
      <!-- Header -->
      <header class="page-header">
        <h1 class="gradient-text">💫 {{ $t('character.guideTitle') }}</h1>
        <p class="subtitle">{{ $t('character.guideSubtitle') }}</p>
      </header>

      <!-- Filter by script -->
      <div class="filter-bar" v-if="scriptOptions.length > 1">
        <n-select
          v-model:value="selectedScriptId"
          :options="scriptOptions"
          :placeholder="$t('character.allScripts')"
          clearable
          size="small"
          style="width: 200px"
          @update:value="loadCharacters"
        />
      </div>

      <!-- Character Grid -->
      <n-spin :show="loading">
        <n-empty v-if="!loading && characters.length === 0" :description="$t('character.noCharacters')" />
        <div
          v-else
          class="character-grid mobile-carousel"
          ref="characterCarouselRef"
          @mouseenter="characterCarousel.pause()"
          @mouseleave="characterCarousel.resume()"
          @touchstart.passive="characterCarousel.pause()"
          @touchend="characterCarousel.resume()"
        >
          <div
            v-for="(char, i) in characters"
            :key="char.id"
            class="char-card glass-card fade-in-up carousel-item"
            :style="{ animationDelay: `${i * 0.06}s` }"
            @click="goToDetail(char.id)"
          >
            <div class="char-avatar-wrap">
              <div class="char-avatar">{{ nameInitial(char.name) }}</div>
            </div>
            <div class="char-info">
              <div class="char-name">{{ char.name }}</div>
              <div class="char-style">{{ styleLabel(char.dialogue_style) }}</div>
              <p class="char-desc">{{ char.description }}</p>
            </div>
            <div class="char-affection" v-if="char.affection_value != null">
              <AffectionMeter :value="char.affection_value" :label="char.name" compact />
            </div>
          </div>
        </div>
        <div class="carousel-indicators" v-if="!loading && characters.length > 1">
          <span
            v-for="(_, i) in characters"
            :key="i"
            class="carousel-dot"
            :class="{ active: characterCarousel.currentIndex.value === i }"
            @click="characterCarousel.scrollToIndex(i)"
          ></span>
        </div>
      </n-spin>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage } from 'naive-ui';
import { useHead } from '@vueuse/head';
import { useI18n } from 'vue-i18n';
import { gameApi } from '@/api/game';
import type { CharacterCard } from '@/api/game';
import AffectionMeter from '@/components/AffectionMeter.vue';
import { useMobileCarousel } from '@/composables/useMobileCarousel';

const { t } = useI18n();

useHead({
  title: 'Isekai Wanderer - Characters',
  meta: [{ name: 'description', content: () => t('character.metaDesc') }],
});

const router = useRouter();
const message = useMessage();

const characters = ref<CharacterCard[]>([]);
const loading = ref(false);
const selectedScriptId = ref<string | null>(null);
const scriptOptions = ref<Array<{ label: string; value: string | null }>>([
  { label: t('character.allScripts'), value: null },
]);

// Mobile carousel
const characterCarouselRef = ref<HTMLElement | null>(null);
const characterCount = computed(() => characters.value.length);
const characterCarousel = useMobileCarousel(characterCarouselRef, characterCount);

function nameInitial(name: string): string {
  return name.charAt(0);
}

function styleLabel(style: string): string {
  const map: Record<string, () => string> = {
    gentle: () => t('character.gentle'),
    tsundere: () => t('character.tsundere'),
    cool: () => t('character.cool'),
    energetic: () => t('character.energetic'),
    mysterious: () => t('character.mysterious'),
    formal: () => t('character.formal'),
  };
  return map[style] ? map[style]() : style;
}

function goToDetail(id: string) {
  router.push(`/characters/${id}`);
}

async function loadScriptOptions() {
  try {
    const resp = await gameApi.getScripts();
    for (const s of resp.scripts) {
      scriptOptions.value.push({ label: s.title, value: s.id });
    }
  } catch (err) {
    console.warn('loadScriptOptions failed:', err instanceof Error ? err.message : err);
  }
}

async function loadCharacters() {
  loading.value = true;
  try {
    const resp = await gameApi.getCharacters({
      script_id: selectedScriptId.value || undefined,
      limit: 50,
    });
    characters.value = resp.characters;
  } catch (err) {
    message.error(t('common.error'));
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadScriptOptions();
  loadCharacters();
});
</script>

<style scoped>
.character-list-page { max-width: 960px; margin: 0 auto; padding: 24px 16px 48px; }
.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 24px; font-weight: 700; margin: 0; }
.subtitle { color: var(--text-muted); font-size: 14px; margin: 4px 0 0; }
.filter-bar { margin-bottom: 20px; }
.character-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.char-card {
  cursor: pointer;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  transition: all 0.3s ease;
}
.char-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(139, 92, 246, 0.12);
}
.char-avatar-wrap { margin-bottom: 12px; }
.char-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 700;
  color: white;
  background: linear-gradient(135deg, #818CF8, #C084FC);
  box-shadow: 0 4px 16px rgba(139, 92, 246, 0.25);
}
.char-info { width: 100%; }
.char-name { font-size: 16px; font-weight: 600; color: var(--text-main); margin-bottom: 4px; }
.char-script { font-size: 11px; color: var(--brand-primary); margin-bottom: 4px; font-weight: 500; }
.char-style { font-size: 12px; color: var(--text-muted); margin-bottom: 8px; }
.char-desc {
  font-size: 12px;
  color: var(--text-subtle);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0;
}
.char-affection { width: 100%; margin-top: 12px; }
</style>
