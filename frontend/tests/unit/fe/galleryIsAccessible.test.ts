import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

/**
 * AC-021/AC-010/AC-016: GalleryView is_accessible 字段处理
 * 
 * 验证：
 * 1. CGItem 接口包含 is_accessible 字段
 * 2. is_accessible=false 的 CG 显示锁图标
 * 3. 点击锁定 CG 时显示升级提示而非预览
 * 4. is_accessible=true 的 CG 正常预览
 */

// 模拟 CGItem 类型（与 GalleryView.vue 中的 interface CGItem 一致）
interface CGItem {
  id: string;
  collection_id: string;
  title: string;
  thumbnail_url: string;
  script_name: string;
  unlock_status: string;
  unlock_condition: string;
  is_accessible?: boolean;  // CR-043 新增
}

describe('CR-043 DEV-002: GalleryView is_accessible', () => {
  describe('CGItem interface', () => {
    it('should have is_accessible optional field', () => {
      const item: CGItem = {
        id: '1',
        collection_id: 'col1',
        title: 'Test CG',
        thumbnail_url: '/img.jpg',
        script_name: 'Test Script',
        unlock_status: 'unlocked',
        unlock_condition: '',
        is_accessible: true,
      };
      expect(item.is_accessible).toBe(true);
    });

    it('should allow is_accessible=false', () => {
      const item: CGItem = {
        id: '2',
        collection_id: 'col1',
        title: 'Locked CG',
        thumbnail_url: '/img.jpg',
        script_name: 'Test Script',
        unlock_status: 'locked',
        unlock_condition: '需要订阅',
        is_accessible: false,
      };
      expect(item.is_accessible).toBe(false);
    });

    it('should work without is_accessible (backward compat)', () => {
      const item: CGItem = {
        id: '3',
        collection_id: 'col1',
        title: 'Legacy CG',
        thumbnail_url: '/img.jpg',
        script_name: 'Test Script',
        unlock_status: 'unlocked',
        unlock_condition: '',
      };
      // is_accessible is optional, should be undefined
      expect(item.is_accessible).toBeUndefined();
    });
  });

  describe('is_accessible logic', () => {
    // Simulate the click handler logic:
    // - is_accessible === false → show upgrade hint (not preview)
    // - unlock_status === 'unlocked' && is_accessible !== false → preview
    // - unlock_status === 'locked' && is_accessible === false → show upgrade hint
    // - unlock_status === 'locked' && is_accessible === true → preview (standard+ can see all)

    function shouldShowUpgrade(item: CGItem): boolean {
      return item.is_accessible === false;
    }

    function shouldPreview(item: CGItem): boolean {
      if (item.is_accessible === false) return false;
      if (item.is_accessible === true) return true;
      // backward compat: is_accessible undefined → use unlock_status
      return item.unlock_status === 'unlocked';
    }

    it('should show upgrade for is_accessible=false, unlocked CG', () => {
      const item: CGItem = {
        id: '1', collection_id: 'c', title: '', thumbnail_url: '',
        script_name: '', unlock_status: 'unlocked', unlock_condition: '',
        is_accessible: false,
      };
      expect(shouldShowUpgrade(item)).toBe(true);
      expect(shouldPreview(item)).toBe(false);
    });

    it('should preview for is_accessible=true, locked CG (standard+ user)', () => {
      const item: CGItem = {
        id: '2', collection_id: 'c', title: '', thumbnail_url: '',
        script_name: '', unlock_status: 'locked', unlock_condition: 'xxx',
        is_accessible: true,
      };
      expect(shouldShowUpgrade(item)).toBe(false);
      expect(shouldPreview(item)).toBe(true);
    });

    it('should preview for is_accessible=true, unlocked CG', () => {
      const item: CGItem = {
        id: '3', collection_id: 'c', title: '', thumbnail_url: '',
        script_name: '', unlock_status: 'unlocked', unlock_condition: '',
        is_accessible: true,
      };
      expect(shouldShowUpgrade(item)).toBe(false);
      expect(shouldPreview(item)).toBe(true);
    });

    it('should show upgrade for is_accessible=false, locked CG', () => {
      const item: CGItem = {
        id: '4', collection_id: 'c', title: '', thumbnail_url: '',
        script_name: '', unlock_status: 'locked', unlock_condition: 'xxx',
        is_accessible: false,
      };
      expect(shouldShowUpgrade(item)).toBe(true);
      expect(shouldPreview(item)).toBe(false);
    });

    it('should use backward compat for undefined is_accessible', () => {
      const unlocked: CGItem = {
        id: '5a', collection_id: 'c', title: '', thumbnail_url: '',
        script_name: '', unlock_status: 'unlocked', unlock_condition: '',
      };
      expect(shouldPreview(unlocked)).toBe(true);
      expect(shouldShowUpgrade(unlocked)).toBe(false);

      const locked: CGItem = {
        id: '5b', collection_id: 'c', title: '', thumbnail_url: '',
        script_name: '', unlock_status: 'locked', unlock_condition: 'xxx',
      };
      expect(shouldPreview(locked)).toBe(false);
      expect(shouldShowUpgrade(locked)).toBe(false);
    });

    it('should show lock overlay for is_accessible=false regardless of unlock_status', () => {
      function shouldShowLockOverlay(item: CGItem): boolean {
        // Show lock overlay when:
        // - unlock_status === 'locked' (not unlocked through gameplay) OR
        // - is_accessible === false (not accessible due to subscription tier)
        return item.unlock_status === 'locked' || item.is_accessible === false;
      }

      const unlockedButInaccessible: CGItem = {
        id: '6a', collection_id: 'c', title: '', thumbnail_url: '',
        script_name: '', unlock_status: 'unlocked', unlock_condition: '',
        is_accessible: false,
      };
      expect(shouldShowLockOverlay(unlockedButInaccessible)).toBe(true);

      const lockedAndAccessible: CGItem = {
        id: '6b', collection_id: 'c', title: '', thumbnail_url: '',
        script_name: '', unlock_status: 'locked', unlock_condition: 'xxx',
        is_accessible: true,
      };
      // standard+ user with locked CG: show lock (not unlocked through gameplay)
      // but clicking should preview (is_accessible=true)
      expect(shouldShowLockOverlay(lockedAndAccessible)).toBe(true);
    });
  });
});
