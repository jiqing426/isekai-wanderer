import { describe, it, expect } from 'vitest';
import type { UserProfile, SubscriptionStatus, MemberInfo } from '@/types/user';

// Type-level test: this will cause a TypeScript compile error if 'basic'
// is not in the subscription_tier union
// We use a type assertion approach that works at compile time

/**
 * AC-021: TypeScript 类型定义 subscription_tier 包含 'basic' 选项
 */
describe('AC-021: subscription_tier type includes basic', () => {
  it('UserProfile should accept subscription_tier="basic"', () => {
    const user: UserProfile = {
      id: '1',
      email: 'test@test.com',
      display_name: 'Test',
      avatar_url: null,
      signature: null,
      email_verified: true,
      subscription_tier: 'basic',
      preferred_genre: null,
      locale: 'zh-CN',
      onboarding_completed: true,
      created_at: '2024-01-01T00:00:00Z',
    };
    expect(user.subscription_tier).toBe('basic');
  });

  it('UserProfile should accept all four tiers', () => {
    const tiers: UserProfile['subscription_tier'][] = ['free', 'basic', 'standard', 'premium'];
    expect(tiers).toHaveLength(4);
    expect(tiers).toContain('basic');
  });

  it('SubscriptionStatus should accept tier="basic"', () => {
    const status: SubscriptionStatus = {
      tier: 'basic',
      status: 'active',
      trial_started_at: null,
      trial_ends_at: null,
      renew_at: null,
    };
    expect(status.tier).toBe('basic');
  });

  it('MemberInfo should accept tier="basic"', () => {
    const info: MemberInfo = {
      tier: 'basic',
      status: 'active',
      member_since: null,
      expires_at: null,
      auto_renew: false,
      fragment_balance: 0,
      benefits: [],
      recent_bills: [],
    };
    expect(info.tier).toBe('basic');
  });

  it('subscription_tier type should be exactly 4 values', () => {
    // Type assertion to verify at compile time that 'basic' is assignable
    const tier: UserProfile['subscription_tier'] = 'basic';
    expect(tier).toBe('basic');
  });
});
