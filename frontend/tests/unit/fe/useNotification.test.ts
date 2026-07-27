import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// Mock Notification API for jsdom (which doesn't provide it)
class MockNotification {
  static permission = 'default';
  static requestPermission = vi.fn().mockResolvedValue('default');
}

(globalThis as Record<string, unknown>).Notification = MockNotification;

// Import after mock is set up
const { useNotification } = await import('@/composables/useNotification');

describe('useNotification', () => {
  // AC-056: Permission request logic
  beforeEach(() => {
    localStorage.clear();
    MockNotification.permission = 'default';
    MockNotification.requestPermission = vi.fn().mockResolvedValue('default');
    (globalThis as Record<string, unknown>).Notification = MockNotification;
  });

  afterEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('should report isSupported=true when Notification API is available', () => {
    const { isSupported } = useNotification();
    expect(isSupported.value).toBe(true);
  });

  it('should show prompt when permission is default and not dismissed', () => {
    MockNotification.permission = 'default';
    localStorage.removeItem('notification_prompt_dismissed');
    const { shouldShowPrompt } = useNotification();
    expect(shouldShowPrompt.value).toBe(true);
  });

  it('should NOT show prompt after dismissPrompt() is called', () => {
    const { shouldShowPrompt, dismissPrompt } = useNotification();
    dismissPrompt();
    expect(shouldShowPrompt.value).toBe(false);
    expect(localStorage.getItem('notification_prompt_dismissed')).toBe('true');
  });

  it('requestPermission should update state to granted on success', async () => {
    MockNotification.requestPermission = vi.fn().mockResolvedValue('granted');
    const { state, requestPermission } = useNotification();
    const result = await requestPermission();
    expect(result).toBe('granted');
    expect(state.value).toBe('granted');
  });

  it('requestPermission should update state to denied on user denial', async () => {
    MockNotification.requestPermission = vi.fn().mockResolvedValue('denied');
    const { state, requestPermission } = useNotification();
    const result = await requestPermission();
    expect(result).toBe('denied');
    expect(state.value).toBe('denied');
  });

  it('should persist prompt dismissed state to localStorage', () => {
    const { dismissPrompt, promptDismissed } = useNotification();
    dismissPrompt();
    expect(promptDismissed.value).toBe(true);
    expect(localStorage.getItem('notification_prompt_dismissed')).toBe('true');
  });

  it('resetPromptDismissed should clear localStorage and reset flag', () => {
    const { dismissPrompt, resetPromptDismissed, promptDismissed } = useNotification();
    dismissPrompt();
    expect(promptDismissed.value).toBe(true);

    resetPromptDismissed();
    expect(promptDismissed.value).toBe(false);
    expect(localStorage.getItem('notification_prompt_dismissed')).toBeNull();
  });

  it('should NOT show prompt when permission is already granted', () => {
    MockNotification.permission = 'granted';
    const { shouldShowPrompt } = useNotification();
    expect(shouldShowPrompt.value).toBe(false);
  });

  it('should NOT show prompt when permission is denied', () => {
    MockNotification.permission = 'denied';
    const { shouldShowPrompt } = useNotification();
    expect(shouldShowPrompt.value).toBe(false);
  });

  it('should report isSupported=false when Notification is not available', () => {
    const saved = (globalThis as Record<string, unknown>).Notification;
    delete (globalThis as Record<string, unknown>).Notification;
    // The composable checks typeof Notification at call time, so a fresh call works
    const { isSupported } = useNotification();
    expect(isSupported.value).toBe(false);
    // Restore for other tests
    (globalThis as Record<string, unknown>).Notification = saved;
  });
});
