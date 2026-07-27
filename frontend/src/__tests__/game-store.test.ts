import { describe, it, expect, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useGameStore } from '@/stores/game';
import { useAffectionStore, getAffectionLevel, AFFECTION_LEVELS } from '@/stores/affection';

describe('Game Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
  });

  it('starts with empty state', () => {
    const store = useGameStore();
    expect(store.scripts).toEqual([]);
    expect(store.currentSession).toBeNull();
    expect(store.currentDialogue).toBeNull();
    expect(store.hasDialogue).toBe(false);
    expect(store.hasChoices).toBe(false);
    expect(store.isEnded).toBe(false);
  });

  it('hasDialogue tracks currentDialogue', () => {
    const store = useGameStore();
    expect(store.hasDialogue).toBe(false);
    store.currentDialogue = {
      type: 'dialogue',
      node_id: 'n1',
      text: 'Hello world',
      character_id: 'char_a',
      emotion: 'warm',
    };
    expect(store.hasDialogue).toBe(true);
  });

  it('hasChoices tracks pendingChoices', () => {
    const store = useGameStore();
    expect(store.hasChoices).toBe(false);
    store.pendingChoices = [
      { id: 'c1', text: 'Option A', affection_delta: 3 },
      { id: 'c2', text: 'Option B', affection_delta: -1 },
    ];
    expect(store.hasChoices).toBe(true);
    expect(store.pendingChoices).toHaveLength(2);
  });

  it('isEnded detects ending type', () => {
    const store = useGameStore();
    expect(store.isEnded).toBe(false);
    store.currentDialogue = {
      type: 'ending',
      node_id: 'n_end',
      text: 'Story complete',
      ending_type: 'good',
      ending_title: 'Good Ending',
    };
    expect(store.isEnded).toBe(true);
  });

  it('reset clears all state', () => {
    const store = useGameStore();
    store.currentDialogue = { type: 'dialogue', node_id: 'n1', text: 'Hi' };
    store.pendingChoices = [{ id: 'c1', text: 'A' }];
    store.choiceHistory.push({ choice_id: 'c1', node_id: 'n1' });
    store.currentSession = { id: 's1', script_id: 'sc1', current_node_id: 'n1', status: 'active' };
    store.reset();
    expect(store.currentDialogue).toBeNull();
    expect(store.pendingChoices).toEqual([]);
    expect(store.currentSession).toBeNull();
    expect(store.choiceHistory).toEqual([]);
    expect(store.currentScript).toBeNull();
  });
});

describe('Affection Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('starts empty', () => {
    const store = useAffectionStore();
    expect(store.affections).toEqual([]);
  });

  it('updateAffection clamps 0-100', () => {
    const store = useAffectionStore();
    store.affections = [{ character_id: 'a', character_name: 'A', value: 50, level: 'trust' }];
    store.updateAffection('a', 120);
    expect(store.affections[0].value).toBe(100);
    store.updateAffection('a', -10);
    expect(store.affections[0].value).toBe(0);
  });

  it('updateAffection updates level', () => {
    const store = useAffectionStore();
    store.affections = [{ character_id: 'a', character_name: 'A', value: 15, level: 'acquaintance' }];
    store.updateAffection('a', 25);
    expect(store.affections[0].level).toBe('ambiguous');
  });

  it('updateAffection creates new entry if not found', () => {
    const store = useAffectionStore();
    store.updateAffection('new_char', 45);
    expect(store.affections).toHaveLength(1);
    expect(store.affections[0].character_id).toBe('new_char');
    expect(store.affections[0].value).toBe(45);
    expect(store.affections[0].level).toBe('trust');
  });

  it('getAffectionLevel returns correct levels', () => {
    expect(getAffectionLevel(0)).toBe('acquaintance');
    expect(getAffectionLevel(19)).toBe('acquaintance');
    expect(getAffectionLevel(20)).toBe('ambiguous');
    expect(getAffectionLevel(39)).toBe('ambiguous');
    expect(getAffectionLevel(40)).toBe('trust');
    expect(getAffectionLevel(59)).toBe('trust');
    expect(getAffectionLevel(60)).toBe('bond');
    expect(getAffectionLevel(79)).toBe('bond');
    expect(getAffectionLevel(80)).toBe('love');
    expect(getAffectionLevel(100)).toBe('love');
  });
});

describe('AFFECTION_LEVELS', () => {
  it('has all 5 levels defined', () => {
    expect(Object.keys(AFFECTION_LEVELS)).toHaveLength(5);
    expect(AFFECTION_LEVELS.acquaintance.color).toBe('#9CA3AF');
    expect(AFFECTION_LEVELS.ambiguous.color).toBe('#F472B6');
    expect(AFFECTION_LEVELS.trust.color).toBe('#38BDF8');
    expect(AFFECTION_LEVELS.bond.color).toBe('#A78BFA');
    expect(AFFECTION_LEVELS.love.color).toBe('#F43F5E');
  });
});
