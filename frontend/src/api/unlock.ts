/**
 * 解锁动效系统 API (CR-017)
 */
import { api } from './http'
import type {
  UnlockListResponse,
  PendingUnlockResponse,
  RecordUnlockRequest,
  RecordUnlockResponse,
  BatchUnlockRequest,
  BatchUnlockResponse
} from '@/types/unlock'

/**
 * 记录解锁事件
 */
export function recordUnlock(data: RecordUnlockRequest): Promise<RecordUnlockResponse> {
  return api.post('/cr017/unlock/record', data)
}

/**
 * 获取解锁列表
 */
export function getUnlockList(): Promise<UnlockListResponse> {
  return api.get('/cr017/unlock/list')
}

/**
 * 获取待展示解锁队列
 */
export function getPendingUnlocks(): Promise<PendingUnlockResponse> {
  return api.get('/cr017/unlock/pending')
}

/**
 * 标记解锁为已查看
 */
export function markUnlockViewed(id: number): Promise<{ success: boolean }> {
  return api.post('/cr017/unlock/mark-viewed', { id })
}

/**
 * 批量记录解锁
 */
export function batchRecordUnlock(data: BatchUnlockRequest): Promise<BatchUnlockResponse> {
  return api.post('/cr017/unlock/batch', data)
}
