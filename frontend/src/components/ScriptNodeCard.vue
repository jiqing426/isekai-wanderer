<template>
  <div class="node-card" :class="[`node-${node.type}`, { locked: !node.isUnlocked }]">
    <div class="node-header">
      <div class="node-icon">{{ getNodeIcon(node.type) }}</div>
      <h4 class="node-title">{{ node.title }}</h4>
      <span v-if="!node.isUnlocked" class="lock-badge">🔒</span>
    </div>

    <div class="node-content">
      <!-- fixed_scene -->
      <template v-if="node.type === 'fixed_scene'">
        <div v-if="node.background" class="scene-background" :style="{ backgroundImage: `url(${node.background})` }"></div>
        <p v-if="node.content">{{ node.content }}</p>
      </template>

      <!-- ai_dialog -->
      <template v-else-if="node.type === 'ai_dialog'">
        <div class="dialog-character">
          <span class="character-name">{{ node.characterName }}</span>
        </div>
        <div v-if="node.dialogueOptions" class="dialog-options">
          <span v-for="(option, idx) in node.dialogueOptions" :key="idx" class="option-tag">
            {{ option }}
          </span>
        </div>
      </template>

      <!-- choice_point -->
      <template v-else-if="node.type === 'choice_point'">
        <div class="choices-list">
          <div v-for="(choice, idx) in node.choices" :key="idx" class="choice-item">
            <span class="choice-text">{{ choice.text }}</span>
          </div>
        </div>
      </template>

      <!-- converge_node -->
      <template v-else-if="node.type === 'converge_node'">
        <p class="converge-desc">{{ node.description }}</p>
      </template>

      <!-- cg_trigger -->
      <template v-else-if="node.type === 'cg_trigger'">
        <div v-if="node.cgUrl" class="cg-preview">
          <img :src="node.cgUrl" :alt="node.title" />
        </div>
      </template>

      <!-- ending_node -->
      <template v-else-if="node.type === 'ending_node'">
        <div class="ending-info">
          <span class="ending-type" :class="node.endingType">
            {{ getEndingLabel(node.endingType) }}
          </span>
          <p v-if="node.description">{{ node.description }}</p>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ScriptNode } from '@/types/script';

defineProps<{
  node: ScriptNode;
}>();

function getNodeIcon(type: string): string {
  const icons: Record<string, string> = {
    fixed_scene: '🎬',
    ai_dialog: '💬',
    choice_point: '🔀',
    converge_node: '🎯',
    cg_trigger: '🖼️',
    ending_node: '🏁',
  };
  return icons[type] || '📍';
}

function getEndingLabel(type?: string): string {
  const labels: Record<string, string> = {
    good: '好结局',
    normal: '普通结局',
    bad: '坏结局',
  };
  return labels[type || ''] || '结局';
}
</script>

<style scoped>
.node-card {
  background: var(--bg-card);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  transition: all 0.2s ease;
}

.node-card:hover:not(.locked) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.node-card.locked {
  opacity: 0.6;
  cursor: not-allowed;
}

.node-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.node-icon {
  font-size: 20px;
}

.node-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  flex: 1;
}

.lock-badge {
  font-size: 16px;
}

.node-content {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
}

/* fixed_scene */
.scene-background {
  width: 100%;
  height: 120px;
  background-size: cover;
  background-position: center;
  border-radius: 8px;
  margin-bottom: 8px;
}

/* ai_dialog */
.dialog-character {
  margin-bottom: 8px;
}

.character-name {
  font-weight: 600;
  color: var(--color-primary);
}

.dialog-options {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.option-tag {
  background: var(--bg-hover);
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 13px;
}

/* choice_point */
.choices-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.choice-item {
  background: var(--bg-hover);
  padding: 10px 14px;
  border-radius: 8px;
  border-left: 3px solid var(--color-primary);
}

.choice-text {
  font-size: 14px;
}

/* converge_node */
.converge-desc {
  font-style: italic;
  color: var(--text-muted);
}

/* cg_trigger */
.cg-preview img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 8px;
}

/* ending_node */
.ending-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ending-type {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  width: fit-content;
}

.ending-type.good {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.ending-type.normal {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.ending-type.bad {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

/* Node type specific styles */
.node-fixed_scene {
  border-color: rgba(59, 130, 246, 0.3);
}

.node-ai_dialog {
  border-color: rgba(168, 85, 247, 0.3);
}

.node-choice_point {
  border-color: rgba(245, 158, 11, 0.3);
}

.node-converge_node {
  border-color: rgba(107, 114, 128, 0.3);
}

.node-cg_trigger {
  border-color: rgba(236, 72, 153, 0.3);
}

.node-ending_node {
  border-color: rgba(34, 197, 94, 0.3);
}
</style>
