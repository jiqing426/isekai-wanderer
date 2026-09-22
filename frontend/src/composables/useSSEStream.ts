import { ref, type Ref } from 'vue';

/**
 * SSE Stream Options — describes the request configuration.
 */
export interface SSEStreamOptions {
  /** API URL (relative or absolute) */
  url: string;
  /** HTTP method, defaults to POST */
  method?: 'POST' | 'GET';
  /** Request body (JSON-serializable) */
  body?: Record<string, any>;
  /** Extra headers (e.g. Authorization) */
  headers?: Record<string, string>;
}

/**
 * SSE Stream Callbacks — called when SSE events are parsed.
 * Only onText is required; all others are optional.
 */
export interface SSEStreamCallbacks {
  /** Called for each text chunk (type: "text") */
  onText: (content: string) => void;
  /** Called when stream is done (type: "done") — carries metadata */
  onDone?: (data: any) => void;
  /** Called on error event (type: "error") or stream/network error */
  onError?: (error: string) => void;
  /** Called for emotion event (type: "emotion") */
  onEmotion?: (data: { emotion: string; character_id?: string }) => void;
  /** Called for affection_update event (type: "affection_update") */
  onAffectionUpdate?: (data: { character_id: string; value: number; level?: string }) => void;
  /** Called for gm_update event (type: "gm_update") — Corvus path */
  onGmUpdate?: (data: any) => void;
}

/**
 * SSE Stream Result — returned by the composable.
 */
export interface SSEStreamResult {
  /** Start the SSE stream. Resolves when stream is complete or errored. */
  start: () => Promise<void>;
  /** Abort the stream (cancels the fetch and reader). */
  abort: () => void;
  /** Whether the stream is currently active. */
  isStreaming: Ref<boolean>;
}

/**
 * useSSEStream — extracts the fetch + ReadableStream reader + SSE event parsing
 * logic that is currently duplicated in submitChoice (Corvus) and submitCustomInput (Corvus)
 * and FreeChatView.
 *
 * This composable wraps:
 * 1. Cookie-based auth token extraction (same as current inline code)
 * 2. fetch() with POST + body + headers
 * 3. ReadableStream reader + TextDecoder
 * 4. SSE line splitting + "data: " prefix parsing
 * 5. Event dispatch via callbacks (onText, onDone, onError, onEmotion, onAffectionUpdate, onGmUpdate)
 *
 * Usage:
 * ```ts
 * const { start, abort, isStreaming } = useSSEStream(
 *   { url: '/api/v1/game/session/choice', method: 'POST', body: { choice_id: '...' } },
 *   {
 *     onText: (content) => { fullText += content; },
 *     onDone: (data) => { /* done */ },
 *     onError: (msg) => { console.error('error', msg); },
 *   }
 * );
 * await start();
 * ```
 */
export function useSSEStream(
  options: SSEStreamOptions,
  callbacks: SSEStreamCallbacks,
): SSEStreamResult {
  const isStreaming = ref(false);
  let controller: AbortController | null = null;
  let reader: ReadableStreamDefaultReader<Uint8Array> | null = null;

  /**
   * Extract auth token from cookie (same as existing inline code in game.ts).
   */
  function getAuthToken(): string | null {
    const match = document.cookie.match(/(^| )isekai_access_token=([^;]+)/);
    return match ? decodeURIComponent(match[2]) : null;
  }

  /**
   * Build fetch headers: merge provided headers with Content-Type and auth.
   */
  function buildHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    };

    // If no Authorization header provided, extract from cookie
    if (!headers['Authorization']) {
      const token = getAuthToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  /**
   * Dispatch a parsed SSE event to the appropriate callback.
   */
  function dispatchEvent(data: any): void {
    if (!data || typeof data.type !== 'string') return;

    switch (data.type) {
      case 'text':
        callbacks.onText(data.content || '');
        break;
      case 'done':
        callbacks.onDone?.(data);
        break;
      case 'error':
        callbacks.onError?.(data.message || 'Unknown error');
        break;
      case 'emotion':
        callbacks.onEmotion?.(data);
        break;
      case 'affection_update':
        callbacks.onAffectionUpdate?.(data);
        break;
      case 'gm_update':
        callbacks.onGmUpdate?.(data);
        break;
      default:
        // Unknown event type — ignore gracefully
        break;
    }
  }

  /**
   * Start the SSE stream.
   */
  async function start(): Promise<void> {
    isStreaming.value = true;
    controller = new AbortController();

    try {
      const fetchOptions: RequestInit = {
        method: options.method || 'POST',
        headers: buildHeaders(),
        signal: controller.signal,
      };

      if (options.body && (options.method || 'POST') !== 'GET') {
        fetchOptions.body = JSON.stringify(options.body);
      }

      const response = await fetch(options.url, fetchOptions);

      if (!response.ok) {
        // Try to read error from response body
        let errorMsg = `HTTP ${response.status}`;
        try {
          if (response.body) {
            const text = await response.text();
            const parsed = JSON.parse(text);
            errorMsg = parsed.message || errorMsg;
          }
        } catch {
          // Ignore parse failure — use HTTP status
        }
        callbacks.onError?.(errorMsg);
        return;
      }

      if (!response.body) {
        callbacks.onError?.('Response body is null');
        return;
      }

      reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Split by newlines and process complete lines
        const lines = buffer.split('\n');
        // Keep the last (possibly partial) line in the buffer
        buffer = lines.pop() || '';

        for (const line of lines) {
          processSSELine(line);
        }
      }

      // Process any remaining data in buffer
      if (buffer.trim()) {
        processSSELine(buffer);
      }
    } catch (err: any) {
      // AbortError is expected when abort() is called
      if (err?.name === 'AbortError') {
        // Stream was aborted — not an error
      } else {
        callbacks.onError?.(err?.message || 'Stream failed');
      }
    } finally {
      isStreaming.value = false;
      reader = null;
      controller = null;
    }
  }

  /**
   * Process a single SSE line.
   * Only processes lines starting with "data: " (SSE data lines).
   * Ignores comments (lines starting with ":") and event/id lines.
   */
  function processSSELine(line: string): void {
    const trimmed = line.trim();

    // Skip empty lines and comments
    if (!trimmed || trimmed.startsWith(':')) return;

    // Only process data lines
    if (!trimmed.startsWith('data: ')) return;

    const jsonStr = trimmed.slice(6); // Remove "data: " prefix

    try {
      const data = JSON.parse(jsonStr);
      dispatchEvent(data);
    } catch (e) {
      // Malformed JSON — log and skip
      console.error('SSE parse error:', e, 'raw:', jsonStr);
    }
  }

  /**
   * Abort the stream.
   */
  function abort(): void {
    if (controller) {
      controller.abort();
    }
    if (reader) {
      try {
        reader.cancel();
      } catch {
        // Ignore cancel errors
      }
    }
    isStreaming.value = false;
  }

  return {
    start,
    abort,
    isStreaming,
  };
}
