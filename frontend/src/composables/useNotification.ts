import { ref, computed } from 'vue';

/**
 * AC-056: PWA notification composable.
 *
 * Manages notification permission state and provides a reactive
 * interface for requesting and checking notification permissions.
 * Persists prompt-dismissed state to localStorage.
 */

export type NotificationState = 'default' | 'granted' | 'denied';

const STORAGE_KEY = 'notification_prompt_dismissed';

export function useNotification() {
  const state = ref<NotificationState>(
    typeof Notification !== 'undefined'
      ? (Notification.permission as NotificationState)
      : 'default',
  );

  const isSupported = computed(() => typeof Notification !== 'undefined');
  const isGranted = computed(() => state.value === 'granted');
  const isDenied = computed(() => state.value === 'denied');

  // Track whether the user has already interacted with the prompt
  const promptDismissed = ref(
    typeof localStorage !== 'undefined'
      ? localStorage.getItem(STORAGE_KEY) === 'true'
      : false,
  );

  const shouldShowPrompt = computed(
    () => isSupported.value && state.value === 'default' && !promptDismissed.value,
  );

  async function requestPermission(): Promise<NotificationState> {
    if (!isSupported.value) {
      state.value = 'denied';
      return state.value;
    }

    try {
      const permission = await Notification.requestPermission();
      state.value = permission as NotificationState;
      return state.value;
    } catch (err) {
      console.warn('Notification permission request failed:', err instanceof Error ? err.message : err);
      state.value = 'denied';
      return state.value;
    }
  }

  function dismissPrompt() {
    promptDismissed.value = true;
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, 'true');
    }
  }

  function resetPromptDismissed() {
    promptDismissed.value = false;
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem(STORAGE_KEY);
    }
  }

  return {
    state,
    isSupported,
    isGranted,
    isDenied,
    shouldShowPrompt,
    promptDismissed,
    requestPermission,
    dismissPrompt,
    resetPromptDismissed,
  };
}
