/**
 * 订阅相关 API (CR-011, CR-012, CR-016)
 */
import { api } from './http';
import type {
  SubscriptionInfo,
  SubscriptionStatus,
  DialogueQuotaStatus,
  SubscriptionPlansResponse,
  SubscribeRequest,
  SubscribeResponse,
  ExchangeRequest,
  ExchangeResponse,
  PaywallCheckResponse
} from '@/types/subscription';

/**
 * 获取当前用户订阅信息
 */
export function getMySubscription(): Promise<SubscriptionInfo> {
  return api.get('/users/me/subscription');
}

/**
 * 获取订阅套餐列表
 */
export function getSubscriptionPlans(): Promise<SubscriptionPlansResponse> {
  return api.get('/subscription/plans');
}

/**
 * 订阅套餐
 */
export function subscribe(data: SubscribeRequest): Promise<SubscribeResponse> {
  return api.post('/subscription/subscribe', data);
}

/**
 * 购买额外对话额度
 */
export function exchangeQuota(data: ExchangeRequest): Promise<ExchangeResponse> {
  return api.post('/fragment/exchange', data);
}

/**
 * 检查付费墙触发
 */
export function checkPaywall(scene: string): Promise<PaywallCheckResponse> {
  return api.get(`/cr016/paywall/check-trigger?scene=${scene}`);
}

/**
 * 创建订阅订单 (CR-012)
 */
export function createOrder(data: { planId: string; cycleType: 'monthly' | 'yearly' }): Promise<{
  orderId: string;
  payUrl: string;
  amount: number;
  currency: string;
}> {
  return api.post('/order/create', data);
}

/**
 * 获取当前订阅状态 (CR-016)
 * GET /api/subscription/status
 */
export function getSubscriptionStatus(): Promise<SubscriptionStatus> {
  return api.get('/cr016/subscription/status');
}

/**
 * 获取当日对话额度 (CR-016)
 * GET /api/dialogue/quota
 */
export function getDialogueQuota(): Promise<DialogueQuotaStatus> {
  return api.get('/cr016/dialogue/quota/status');
}

/**
 * 使用碎片购买额外对话额度 (CR-016)
 * POST /api/subscription/fragment-purchase
 */
export function purchaseFragmentQuota(data: { amount: number }): Promise<{ success: boolean; new_quota: number }> {
  return api.post('/cr016/subscription/fragment-purchase', data);
}

/**
 * 创建订阅 (CR-016)
 * POST /api/subscription/create
 */
export function createSubscription(tier: string): Promise<{ subscription_id: string }> {
  return api.post('/cr016/subscription/create', { tier });
}

/**
 * 取消订阅 (CR-016)
 * POST /api/subscription/cancel
 */
export function cancelSubscription(): Promise<{ cancelled_at: string }> {
  return api.post('/cr016/subscription/cancel');
}

/**
 * 记录付费墙事件 (CR-016)
 * POST /cr016/paywall/record-event
 */
export function recordPaywallEvent(data: { scene: string; event_type: string }): Promise<{ success: boolean }> {
  return api.post('/cr016/paywall/record-event', data);
}

/**
 * 获取当日付费墙触发次数 (CR-016)
 * GET /cr016/paywall/daily-count
 */
export function getPaywallDailyCount(): Promise<{ date: string; count: number; limit: number }> {
  return api.get('/cr016/paywall/daily-count');
}

/**
 * 获取对话生命周期状态 (CR-016)
 * GET /cr016/dialogue/lifecycle
 */
export function getDialogueLifecycle(): Promise<{ stage: string; day_count: number; next_stage_at: string | null }> {
  return api.get('/cr016/dialogue/lifecycle');
}
