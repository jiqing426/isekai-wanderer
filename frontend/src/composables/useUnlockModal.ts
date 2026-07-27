import { ref, computed } from 'vue'
import type { UnlockData } from '@/types/unlock'

// 全局单例状态
const globalQueue = ref<UnlockData[]>([])
const globalCurrent = ref<UnlockData | null>(null)
const globalVisible = ref(false)
let isProcessing = false

export function useUnlockModal() {
  const currentUnlock = computed(() => globalCurrent.value)
  const isVisible = computed(() => globalVisible.value)

  function processQueue() {
    if (isProcessing) return
    if (globalQueue.value.length === 0) {
      globalVisible.value = false
      setTimeout(() => {
        globalCurrent.value = null
      }, 300)
      return
    }

    isProcessing = true
    const next = globalQueue.value.shift()!
    globalCurrent.value = next
    globalVisible.value = true
  }

  function show(data: UnlockData) {
    globalQueue.value.push(data)
    if (!globalVisible.value) {
      processQueue()
    }
  }

  function queue(items: UnlockData[]) {
    globalQueue.value.push(...items)
    if (!globalVisible.value) {
      processQueue()
    }
  }

  function batch(items: UnlockData[]) {
    // 合并为单个 multi_reward 展示
    const merged: UnlockData = {
      type: 'multi_reward',
      title: '获得奖励',
      description: '',
      rewards: items.reduce((acc, item) => {
        if (!acc) acc = []
        if (item.reward) acc.push(item.reward)
        if (item.rewards) acc.push(...item.rewards)
        return acc
      }, [] as NonNullable<UnlockData['rewards']>),
      onConfirm: () => {
        items.forEach(item => item.onConfirm?.())
      }
    }
    globalQueue.value.push(merged)
    if (!globalVisible.value) {
      processQueue()
    }
  }

  function skip() {
    globalCurrent.value?.onLater?.()
    isProcessing = false
    processQueue()
  }

  function confirm() {
    globalCurrent.value?.onConfirm?.()
    isProcessing = false
    processQueue()
  }

  function close() {
    isProcessing = false
    processQueue()
  }

  return {
    show,
    queue,
    batch,
    skip,
    confirm,
    close,
    currentUnlock,
    isVisible
  }
}
