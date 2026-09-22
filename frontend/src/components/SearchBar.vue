<template>
  <div class="search-bar">
    <div class="search-input-wrapper">
      <input
        v-model="searchQuery"
        type="text"
        :placeholder="placeholder"
        class="search-input"
        @keyup.enter="handleSearch"
        @input="handleInput"
      />
      <button
        v-if="searchQuery"
        class="clear-button"
        @click="handleClear"
      >
        ✕
      </button>
    </div>
    <button
      class="search-button"
      @click="handleSearch"
      :disabled="!searchQuery.trim()"
    >
      {{ $t('searchBar.search') }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

defineProps<{
  placeholder?: string;
}>();

const emit = defineEmits<{
  (e: 'search', keyword: string): void;
  (e: 'clear'): void;
}>();

const searchQuery = ref('');

function handleSearch() {
  if (searchQuery.value.trim()) {
    emit('search', searchQuery.value.trim());
  }
}

function handleClear() {
  searchQuery.value = '';
  emit('clear');
}

function handleInput() {
  // 可以在这里添加实时搜索逻辑
}
</script>

<style scoped>
.search-bar {
  display: flex;
  gap: 8px;
  width: 100%;
}

.search-input-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.search-input {
  width: 100%;
  padding: 10px 40px 10px 16px;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  color: var(--text-primary);
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  background: var(--bg-card);
}

.search-input::placeholder {
  color: var(--text-secondary);
}

.clear-button {
  position: absolute;
  right: 8px;
  width: 24px;
  height: 24px;
  background: var(--bg-hover);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.clear-button:hover {
  background: var(--bg-card);
  color: var(--text-primary);
}

.search-button {
  padding: 10px 20px;
  background: var(--color-primary);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.search-button:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.search-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
