import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { defineComponent } from 'vue';
import AudioPlayer from '@/components/AudioPlayer.vue';

// Minimal wrapper to mount AudioPlayer
const TestWrapper = defineComponent({
  components: { AudioPlayer },
  template: '<AudioPlayer />',
});

describe('AudioPlayer', () => {
  // AC-048: Emotion volume multiplier
  describe('emotion volume multiplier', () => {
    it('should have default emotionVolumeMultiplier of 1', () => {
      const wrapper = mount(TestWrapper);
      const player = wrapper.findComponent(AudioPlayer);
      expect(player.vm.emotionVolumeMultiplier).toBe(1);
    });

    it('should set tense volume multiplier (0.7x)', () => {
      const wrapper = mount(TestWrapper);
      const player = wrapper.findComponent(AudioPlayer);
      player.vm.setEmotionVolumeMultiplier('tense');
      expect(player.vm.emotionVolumeMultiplier).toBe(0.7);
    });

    it('should set warm volume multiplier (0.8x)', () => {
      const wrapper = mount(TestWrapper);
      const player = wrapper.findComponent(AudioPlayer);
      player.vm.setEmotionVolumeMultiplier('warm');
      expect(player.vm.emotionVolumeMultiplier).toBe(0.8);
    });

    it('should set sad volume multiplier (0.5x)', () => {
      const wrapper = mount(TestWrapper);
      const player = wrapper.findComponent(AudioPlayer);
      player.vm.setEmotionVolumeMultiplier('sad');
      expect(player.vm.emotionVolumeMultiplier).toBe(0.5);
    });

    it('should set excited volume multiplier (1.2x)', () => {
      const wrapper = mount(TestWrapper);
      const player = wrapper.findComponent(AudioPlayer);
      player.vm.setEmotionVolumeMultiplier('excited');
      expect(player.vm.emotionVolumeMultiplier).toBe(1.2);
    });

    it('should set angry volume multiplier (1.1x)', () => {
      const wrapper = mount(TestWrapper);
      const player = wrapper.findComponent(AudioPlayer);
      player.vm.setEmotionVolumeMultiplier('angry');
      expect(player.vm.emotionVolumeMultiplier).toBe(1.1);
    });

    it('should set normal volume multiplier (1x)', () => {
      const wrapper = mount(TestWrapper);
      const player = wrapper.findComponent(AudioPlayer);
      player.vm.setEmotionVolumeMultiplier('normal');
      expect(player.vm.emotionVolumeMultiplier).toBe(1);
    });

    it('should fall back to 1x for unknown emotion', () => {
      const wrapper = mount(TestWrapper);
      const player = wrapper.findComponent(AudioPlayer);
      player.vm.setEmotionVolumeMultiplier('unknown_emotion');
      expect(player.vm.emotionVolumeMultiplier).toBe(1);
    });
  });

  // Mute toggle
  it('should toggle mute state', () => {
    const wrapper = mount(TestWrapper);
    const player = wrapper.findComponent(AudioPlayer);
    expect(player.vm.isMuted).toBe(false);
    player.vm.toggleMute();
    expect(player.vm.isMuted).toBe(true);
    player.vm.toggleMute();
    expect(player.vm.isMuted).toBe(false);
  });
});
