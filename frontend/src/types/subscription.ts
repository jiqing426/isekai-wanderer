/**
 * 订阅相关类型定义 (CR-011, CR-012, CR-016)
 */

// CR-016: 订阅档位类型
export type SubscriptionTier = 'free' | 'basic' | 'standard' | 'premium'

// CR-016: 档位权限配置
export interface TierPermissions {
  tier: SubscriptionTier
  dialogue_limit: number  // -1 = 无限
  archive_limit: number   // -1 = 无限
  script_access: 'trial_only' | 'all_normal' | 'all_including_exclusive'
  voice_enabled: boolean
  rewind_c15: boolean
  ugc_access: boolean
  fragment_discount: number  // 0~1, 0=无折扣
  hidden_options: boolean
}

// CR-016: 订阅状态
export interface SubscriptionStatus {
  tier: SubscriptionTier
  status: 'active' | 'cancelled' | 'expired' | null
  started_at: string | null
  expires_at: string | null
  permissions: TierPermissions
}

// CR-016: 对话额度状态
export interface DialogueQuotaStatus {
  base_quota: number
  consumed: number
  fragment_extra: number
  fragment_consumed: number
  remaining: number
  lifecycle_stage: 'honeymoon' | 'growth' | 'regular' | 'returnee'
  is_subscriber: boolean
}

// CR-016: 付费墙触发指令
export interface PaywallTrigger {
  scene: 'T1_quota' | 'T2_archive' | 'T3_premium' | 'T4_trial' | 'T5_gallery' | 'T6_voice' | 'T7_rewind' | 'T8_fragment'
  display_type: 'modal' | 'banner' | 'toast'
  payload: Record<string, any>
}

// CR-016: 剧本进度信息（用于弹窗展示）
export interface ScriptProgressInfo {
  script_id: string
  script_title: string
  chapter: number
  total_chapters: number
  play_duration_minutes: number
}

// CR-011: 旧版订阅信息（保留兼容）
export interface SubscriptionInfo {
  tier: 'free' | 'basic' | 'standard' | 'premium';
  quota: {
    total: number;
    used: number;
    remaining: number;
    period: 'honeymoon' | 'nurture' | 'regular';
  };
  expires_at: string | null;
  auto_renew: boolean;
}

// CR-012: 订阅套餐类型（匹配 API 契约）
export interface SubscriptionPlan {
  planId: string;
  name: string;
  priceMonthly: number;
  priceYearly: number;
  featureList: string[];
  fragmentDiscountRate: number;
  recommend: boolean;
  is_current?: boolean;
}

export interface SubscriptionPlansResponse {
  plans: SubscriptionPlan[];
}

export interface SubscribeRequest {
  tier: 'basic' | 'standard' | 'premium';
  payment_method: string;
}

export interface SubscribeResponse {
  status: 'success' | 'pending';
  subscription_id: string;
  tier: string;
  expires_at: string;
  quota_updated: boolean;
}

export interface ExchangeRequest {
  goods_id: string;
  quantity: number;
}

export interface ExchangeResponse {
  status: 'success';
  new_quota: number;
  fragments_spent: number;
  quota_added: number;
}

export interface PaywallCheckResponse {
  should_show: boolean;
  type: 'fullscreen' | 'banner' | 'toast';
  message: string;
  scene: string;
  cooldown_remaining: number;
}

// CR-012: 创建订单请求/响应
export interface CreateOrderRequest {
  planId: string;
  cycleType: 'monthly' | 'yearly';
}

export interface CreateOrderResponse {
  orderId: string;
  payUrl: string;
  amount: number;
  currency: string;
}
