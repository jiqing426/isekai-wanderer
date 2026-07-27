import { describe, it, expect } from 'vitest';
import zhCN from '@/i18n/zh-CN';
import enUS from '@/i18n/en-US';

// AC-052: i18n translation completeness
function flattenKeys(obj: Record<string, unknown>, prefix = ''): string[] {
  const keys: string[] = [];
  for (const key of Object.keys(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    const value = obj[key];
    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      keys.push(...flattenKeys(value as Record<string, unknown>, fullKey));
    } else {
      keys.push(fullKey);
    }
  }
  return keys;
}

describe('i18n translation completeness', () => {
  const zhKeys = flattenKeys(zhCN);
  const enKeys = flattenKeys(enUS);

  it('zh-CN should have at least 50 translation keys', () => {
    expect(zhKeys.length).toBeGreaterThanOrEqual(50);
  });

  it('en-US should have at least 50 translation keys', () => {
    expect(enKeys.length).toBeGreaterThanOrEqual(50);
  });

  it('all zh-CN keys should exist in en-US', () => {
    const missing = zhKeys.filter((key) => !enKeys.includes(key));
    expect(missing).toEqual([]);
  });

  it('all en-US keys should exist in zh-CN', () => {
    const missing = enKeys.filter((key) => !zhKeys.includes(key));
    expect(missing).toEqual([]);
  });

  it('no zh-CN value should be empty string', () => {
    const emptyKeys: string[] = [];
    function checkEmpty(obj: Record<string, unknown>, prefix = '') {
      for (const key of Object.keys(obj)) {
        const fullKey = prefix ? `${prefix}.${key}` : key;
        const value = obj[key];
        if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
          checkEmpty(value as Record<string, unknown>, fullKey);
        } else if (typeof value === 'string' && value.trim() === '') {
          emptyKeys.push(fullKey);
        }
      }
    }
    checkEmpty(zhCN);
    expect(emptyKeys).toEqual([]);
  });

  it('no en-US value should be empty string', () => {
    const emptyKeys: string[] = [];
    function checkEmpty(obj: Record<string, unknown>, prefix = '') {
      for (const key of Object.keys(obj)) {
        const fullKey = prefix ? `${prefix}.${key}` : key;
        const value = obj[key];
        if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
          checkEmpty(value as Record<string, unknown>, fullKey);
        } else if (typeof value === 'string' && value.trim() === '') {
          emptyKeys.push(fullKey);
        }
      }
    }
    checkEmpty(enUS);
    expect(emptyKeys).toEqual([]);
  });

  // CR-002 specific keys
  it('should have settings-related keys', () => {
    expect(zhKeys).toContain('settings.title');
    expect(zhKeys).toContain('settings.language');
    expect(enKeys).toContain('settings.title');
    expect(enKeys).toContain('settings.language');
  });

  it('should have notification-related keys', () => {
    expect(zhKeys).toContain('notification.title');
    expect(zhKeys).toContain('notification.enable');
    expect(enKeys).toContain('notification.title');
    expect(enKeys).toContain('notification.enable');
  });
});
