import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from '@/api/http';

export interface Affection {
  character_id: string;
  character_name?: string;
  value: number;
  level: AffectionLevel;
}

export type AffectionLevel = 'acquaintance' | 'ambiguous' | 'trust' | 'bond' | 'love';

export const AFFECTION_LEVELS: Record<AffectionLevel, { min: number; max: number; color: string; label: string }> = {
  acquaintance: { min: 0, max: 19, color: '#9CA3AF', label: '相识' },
  ambiguous: { min: 20, max: 39, color: '#F472B6', label: '暧昧' },
  trust: { min: 40, max: 59, color: '#38BDF8', label: '信赖' },
  bond: { min: 60, max: 79, color: '#A78BFA', label: '羁绊' },
  love: { min: 80, max: 100, color: '#F43F5E', label: '挚友' },
};

export function getAffectionLevel(value: number): AffectionLevel {
  if (value >= 80) return 'love';
  if (value >= 60) return 'bond';
  if (value >= 40) return 'trust';
  if (value >= 20) return 'ambiguous';
  return 'acquaintance';
}

export const useAffectionStore = defineStore('affection', () => {
  const affections = ref<Affection[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const getAffection = computed(() => (characterId: string) => {
    return affections.value.find((a) => a.character_id === characterId);
  });

  function resolveName(characterId: string, apiName?: string): string {
    if (apiName) return apiName;
    return characterId.slice(0, 8) + '…';
  }

  async function loadAffections() {
    loading.value = true;
    try {
      const resp = await api.get<{ affections: (Omit<Affection, 'level'> & { character_name?: string; level_label?: string })[] }>('/affection');
      affections.value = (resp.affections || []).map((a) => ({
        character_id: a.character_id,
        character_name: resolveName(a.character_id, a.character_name),
        value: a.value,
        level: getAffectionLevel(a.value),
      }));
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load affections';
    } finally {
      loading.value = false;
    }
  }

  /** Update or create affection entry. Optionally supply characterName from dialogue context. */
  function updateAffection(characterId: string, value: number, characterName?: string) {
    const existing = affections.value.find((a) => a.character_id === characterId);
    if (existing) {
      existing.value = Math.min(100, Math.max(0, value));
      existing.level = getAffectionLevel(existing.value);
      if (characterName) existing.character_name = characterName;
    } else {
      affections.value.push({
        character_id: characterId,
        character_name: resolveName(characterId, characterName),
        value: Math.min(100, Math.max(0, value)),
        level: getAffectionLevel(value),
      });
    }
  }

  function reset() {
    affections.value = [];
    error.value = null;
  }

  return {
    affections,
    loading,
    error,
    getAffection,
    loadAffections,
    updateAffection,
    reset,
  };
});
