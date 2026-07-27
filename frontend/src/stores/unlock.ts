import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UnlockData, UnlockRecord } from '@/types/unlock'
import { recordUnlock, getUnlockList, getPendingUnlocks, markUnlockViewed, batchRecordUnlock } from '@/api/unlock'

export const useUnlockStore = defineStore('unlock', () => {
  const unlockHistory = ref<UnlockRecord[]>([])
  const pendingQueue = ref<UnlockData[]>([])
  const currentUnlock = ref<UnlockData | null>(null)
  const isVisible = ref(false)
  const loading = ref(false)

  const hasPending = computed(() => pendingQueue.value.length > 0)

  async function fetchHistory() {
    loading.value = true
    try {
      const res = await getUnlockList()
      unlockHistory.value = res.unlocks
    } catch (err) {
      console.error('Failed to fetch unlock history:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchPending() {
    try {
      const res = await getPendingUnlocks()
      pendingQueue.value = res.pending
    } catch (err) {
      console.error('Failed to fetch pending unlocks:', err)
    }
  }

  async function record(data: Omit<UnlockData, 'onConfirm' | 'onLater'>) {
    try {
      await recordUnlock({
        type: data.type,
        content_id: data.contentId || '',
        title: data.title,
        description: data.description,
        image: data.image,
        rarity: data.rarity,
        reward: data.reward,
        rewards: data.rewards
      })
    } catch (err) {
      console.error('Failed to record unlock:', err)
    }
  }

  async function batchRecord(items: Array<Omit<UnlockData, 'onConfirm' | 'onLater'>>) {
    try {
      await batchRecordUnlock({
        unlocks: items.map(item => ({
          type: item.type,
          content_id: item.contentId || '',
          title: item.title,
          description: item.description,
          image: item.image,
          rarity: item.rarity,
          reward: item.reward,
          rewards: item.rewards
        }))
      })
    } catch (err) {
      console.error('Failed to batch record unlocks:', err)
    }
  }

  async function markViewed(id: number) {
    try {
      await markUnlockViewed(id)
    } catch (err) {
      console.error('Failed to mark unlock viewed:', err)
    }
  }

  function show(data: UnlockData) {
    currentUnlock.value = data
    isVisible.value = true
  }

  function hide() {
    isVisible.value = false
    setTimeout(() => {
      currentUnlock.value = null
    }, 300)
  }

  function pushToQueue(data: UnlockData) {
    pendingQueue.value.push(data)
  }

  function pushBatchToQueue(items: UnlockData[]) {
    pendingQueue.value.push(...items)
  }

  function shiftQueue(): UnlockData | undefined {
    return pendingQueue.value.shift()
  }

  function $reset() {
    unlockHistory.value = []
    pendingQueue.value = []
    currentUnlock.value = null
    isVisible.value = false
    loading.value = false
  }

  return {
    unlockHistory,
    pendingQueue,
    currentUnlock,
    isVisible,
    loading,
    hasPending,
    fetchHistory,
    fetchPending,
    record,
    batchRecord,
    markViewed,
    show,
    hide,
    pushToQueue,
    pushBatchToQueue,
    shiftQueue,
    $reset
  }
})
