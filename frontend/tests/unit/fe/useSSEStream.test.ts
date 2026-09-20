import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ref } from 'vue';
import { useSSEStream } from '@/composables/useSSEStream';

// Helper: create a mock ReadableStream that emits SSE chunks
function createMockSSEStream(chunks: string[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  let index = 0;
  return new ReadableStream({
    pull(controller) {
      if (index < chunks.length) {
        controller.enqueue(encoder.encode(chunks[index]));
        index++;
      } else {
        controller.close();
      }
    },
  });
}

// Helper: mock fetch response with SSE body
function mockSSEResponse(chunks: string[], headers: Record<string, string> = {}) {
  return {
    ok: true,
    status: 200,
    headers: {
      get: (name: string) => headers[name] ?? (name === 'Content-Type' ? 'text/event-stream' : null),
    },
    body: createMockSSEStream(chunks),
  };
}

// Helper: mock fetch that rejects (network error)
function mockFetchError() {
  return Promise.reject(new Error('Network error'));
}

// Helper: mock fetch that returns non-ok response
function mockNonOkResponse(status: number, message: string) {
  return Promise.resolve({
    ok: false,
    status,
    headers: { get: () => null },
    body: null,
    json: () => Promise.resolve({ message }),
  });
}

describe('useSSEStream composable (AC-020)', () => {
  let originalFetch: typeof globalThis.fetch;

  beforeEach(() => {
    originalFetch = globalThis.fetch;
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
    vi.restoreAllMocks();
  });

  describe('SSE event parsing', () => {
    it('should parse text events and call onText callback', async () => {
      const sseChunks = [
        'data: {"type":"text","content":"Hello"}\n\n',
        'data: {"type":"text","content":" World"}\n\n',
      ];
      globalThis.fetch = vi.fn(() => Promise.resolve(mockSSEResponse(sseChunks))) as any;

      const receivedText: string[] = [];
      const { start } = useSSEStream(
        { url: '/api/v1/test', method: 'POST', body: {} },
        {
          onText: (content) => receivedText.push(content),
        }
      );

      await start();

      expect(receivedText).toEqual(['Hello', ' World']);
    });

    it('should parse done event and call onDone callback', async () => {
      const sseChunks = [
        'data: {"type":"text","content":"response text"}\n\n',
        'data: {"type":"done","session_id":"abc","node_id":"node-1","choices":[{"id":"c1","text":"Choice 1"}]}\n\n',
      ];
      globalThis.fetch = vi.fn(() => Promise.resolve(mockSSEResponse(sseChunks))) as any;

      let doneData: any = null;
      const { start } = useSSEStream(
        { url: '/api/v1/test', method: 'POST', body: {} },
        {
          onText: () => {},
          onDone: (data) => { doneData = data; },
        }
      );

      await start();

      expect(doneData).not.toBeNull();
      expect(doneData.type).toBe('done');
      expect(doneData.session_id).toBe('abc');
      expect(doneData.node_id).toBe('node-1');
      expect(doneData.choices).toEqual([{ id: 'c1', text: 'Choice 1' }]);
    });

    it('should parse error event and call onError callback', async () => {
      const sseChunks = [
        'data: {"type":"error","message":"Something went wrong"}\n\n',
      ];
      globalThis.fetch = vi.fn(() => Promise.resolve(mockSSEResponse(sseChunks))) as any;

      let errorMsg: string | null = null;
      const { start } = useSSEStream(
        { url: '/api/v1/test', method: 'POST', body: {} },
        {
          onText: () => {},
          onError: (msg) => { errorMsg = msg; },
        }
      );

      await start();

      expect(errorMsg).toBe('Something went wrong');
    });

    it('should parse emotion event and call onEmotion callback', async () => {
      const sseChunks = [
        'data: {"type":"emotion","emotion":"happy","character_id":"char-1"}\n\n',
        'data: {"type":"text","content":"Hi there!"}\n\n',
        'data: {"type":"done","session_id":"s1"}\n\n',
      ];
      globalThis.fetch = vi.fn(() => Promise.resolve(mockSSEResponse(sseChunks))) as any;

      let emotionData: any = null;
      const { start } = useSSEStream(
        { url: '/api/v1/test', method: 'POST', body: {} },
        {
          onText: () => {},
          onEmotion: (data) => { emotionData = data; },
        }
      );

      await start();

      expect(emotionData).not.toBeNull();
      expect(emotionData.emotion).toBe('happy');
      expect(emotionData.character_id).toBe('char-1');
    });

    it('should parse affection_update event and call onAffectionUpdate callback', async () => {
      const sseChunks = [
        'data: {"type":"affection_update","character_id":"char-1","value":45,"level":"trust"}\n\n',
        'data: {"type":"done","session_id":"s1"}\n\n',
      ];
      globalThis.fetch = vi.fn(() => Promise.resolve(mockSSEResponse(sseChunks))) as any;

      let affData: any = null;
      const { start } = useSSEStream(
        { url: '/api/v1/test', method: 'POST', body: {} },
        {
          onText: () => {},
          onAffectionUpdate: (data) => { affData = data; },
        }
      );

      await start();

      expect(affData).not.toBeNull();
      expect(affData.character_id).toBe('char-1');
      expect(affData.value).toBe(45);
      expect(affData.level).toBe('trust');
    });

    it('should parse gm_update event and call onGmUpdate callback (Corvus)', async () => {
      const sseChunks = [
        'data: {"type":"text","content":"GM says hi"}\n\n',
        'data: {"type":"gm_update","player_options":[{"id":"o1","text":"Option 1"}],"affinity_current":50,"new_characters":["Alice"]}\n\n',
        'data: {"type":"done","session_id":"s1"}\n\n',
      ];
      globalThis.fetch = vi.fn(() => Promise.resolve(mockSSEResponse(sseChunks))) as any;

      let gmData: any = null;
      const { start } = useSSEStream(
        { url: '/api/v1/test', method: 'POST', body: {} },
        {
          onText: () => {},
          onGmUpdate: (data) => { gmData = data; },
        }
      );

      await start();

      expect(gmData).not.toBeNull();
      expect(gmData.player_options).toEqual([{ id: 'o1', text: 'Option 1' }]);
      expect(gmData.affinity_current).toBe(50);
      expect(gmData.new_characters).toEqual(['Alice']);
    });
  });

  describe('stream lifecycle', () => {
    it('should set isStreaming to true during stream and false after', async () => {
      const sseChunks = [
        'data: {"type":"text","content":"hi"}\n\n',
        'data: {"type":"done","session_id":"s1"}\n\n',
      ];
      globalThis.fetch = vi.fn(() => Promise.resolve(mockSSEResponse(sseChunks))) as any;

      const { start, isStreaming } = useSSEStream(
        { url: '/api/v1/test', method: 'POST', body: {} },
        { onText: () => {} }
      );

      expect(isStreaming.value).toBe(false);
      const promise = start();
      expect(isStreaming.value).toBe(true);
      await promise;
      expect(isStreaming.value).toBe(false);
    });

    it('should handle network errors gracefully', async () => {
      globalThis.fetch = vi.fn(mockFetchError) as any;

      let errorMsg: string | null = null;
      const { start, isStreaming } = useSSEStream(
        { url: '/api/v1/test', method: 'POST', body: {} },
        {
          onText: () => {},
          onError: (msg) => { errorMsg = msg; },
        }
      );

      await start();

      expect(isStreaming.value).toBe(false);
      expect(errorMsg).not.toBeNull();
      expect(errorMsg).toContain('Network error');
    });

    it('should handle non-ok HTTP response', async () => {
      globalThis.fetch = vi.fn(() => mockNonOkResponse(403, 'Forbidden')) as any;

      let errorMsg: string | null = null;
      const { start } = useSSEStream(
        { url: '/api/v1/test', method: 'POST', body: {} },
        {
          onText: () => {},
          onError: (msg) => { errorMsg = msg; },
        }
      );

      await start();

      expect(errorMsg).toContain('403');
    });

    it('should abort stream when abort() is called', async () => {
      // Create a stream that never closes on its own
      let pullCount = 0;
      const slowStream = new ReadableStream({
        pull(controller) {
          pullCount++;
          // Never close, just enqueue a text event periodically
          if (pullCount === 1) {
            controller.enqueue(new TextEncoder().encode('data: {"type":"text","content":"start"}\n\n'));
          }
          // Don't close - let abort handle it
        },
      });

      globalThis.fetch = vi.fn(() => Promise.resolve({
        ok: true,
        status: 200,
        headers: { get: () => 'text/event-stream' },
        body: slowStream,
      })) as any;

      const { start, abort, isStreaming } = useSSEStream(
        { url: '/api/v1/test', method: 'POST', body: {} },
        { onText: () => {} }
      );

      const promise = start();
      expect(isStreaming.value).toBe(true);

      // Abort after a short delay
      setTimeout(() => abort(), 10);

      await promise;
      expect(isStreaming.value).toBe(false);
    });

    it('should handle partial SSE data across chunks (buffering)', async () => {
      // Split a single SSE event across two chunks
      const sseChunks = [
        'data: {"type":"text","content":"He',
        'llo"}\n\ndata: {"type":"done","session_id":"s1"}\n\n',
      ];
      globalThis.fetch = vi.fn(() => Promise.resolve(mockSSEResponse(sseChunks))) as any;

      const receivedText: string[] = [];
      const { start } = useSSEStream(
        { url: '/api/v1/test', method: 'POST', body: {} },
        {
          onText: (content) => receivedText.push(content),
        }
      );

      await start();

      expect(receivedText).toEqual(['Hello']);
    });

    it('should send POST method with body and auth header', async () => {
      const sseChunks = ['data: {"type":"done","session_id":"s1"}\n\n'];
      let fetchCallArgs: any = null;
      globalThis.fetch = vi.fn((url, opts) => {
        fetchCallArgs = { url, opts };
        return Promise.resolve(mockSSEResponse(sseChunks));
      }) as any;

      const { start } = useSSEStream(
        {
          url: '/api/v1/game/test/choice',
          method: 'POST',
          body: { choice_id: 'choice-1' },
          headers: { 'Authorization': 'Bearer test-token' },
        },
        { onText: () => {} }
      );

      await start();

      expect(fetchCallArgs.url).toBe('/api/v1/game/test/choice');
      expect(fetchCallArgs.opts.method).toBe('POST');
      expect(fetchCallArgs.opts.headers['Content-Type']).toBe('application/json');
      expect(fetchCallArgs.opts.headers['Authorization']).toBe('Bearer test-token');
      expect(JSON.parse(fetchCallArgs.opts.body)).toEqual({ choice_id: 'choice-1' });
    });

    it('should use cookie token when no explicit auth header provided', async () => {
      // Mock document.cookie
      Object.defineProperty(document, 'cookie', {
        writable: true,
        value: 'isekai_access_token=cookie-token-abc',
      });

      const sseChunks = ['data: {"type":"done","session_id":"s1"}\n\n'];
      let fetchHeaders: any = null;
      globalThis.fetch = vi.fn((url, opts) => {
        fetchHeaders = opts.headers;
        return Promise.resolve(mockSSEResponse(sseChunks));
      }) as any;

      const { start } = useSSEStream(
        { url: '/api/v1/test', method: 'POST', body: {} },
        { onText: () => {} }
      );

      await start();

      expect(fetchHeaders['Authorization']).toBe('Bearer cookie-token-abc');
    });

    it('should handle empty/unknown event types gracefully', async () => {
      const sseChunks = [
        'data: {"type":"unknown_type","some_field":"value"}\n\n',
        'data: {"type":"text","content":"actual text"}\n\n',
        'data: {"type":"done"}\n\n',
      ];
      globalThis.fetch = vi.fn(() => Promise.resolve(mockSSEResponse(sseChunks))) as any;

      const receivedText: string[] = [];
      const { start } = useSSEStream(
        { url: '/api/v1/test', method: 'POST', body: {} },
        {
          onText: (content) => receivedText.push(content),
        }
      );

      // Should not throw, just ignore unknown events
      await start();

      expect(receivedText).toEqual(['actual text']);
    });

    it('should handle malformed JSON in SSE data gracefully', async () => {
      const sseChunks = [
        'data: {invalid json\n\n',
        'data: {"type":"text","content":"valid"}\n\n',
        'data: {"type":"done"}\n\n',
      ];
      globalThis.fetch = vi.fn(() => Promise.resolve(mockSSEResponse(sseChunks))) as any;

      // Suppress console.error for this test
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      const receivedText: string[] = [];
      const { start } = useSSEStream(
        { url: '/api/v1/test', method: 'POST', body: {} },
        {
          onText: (content) => receivedText.push(content),
        }
      );

      await start();

      // Malformed JSON should be skipped, valid events should still be processed
      expect(receivedText).toEqual(['valid']);
      expect(consoleErrorSpy).toHaveBeenCalled();
    });

    it('should ignore non-data lines in SSE stream', async () => {
      const sseChunks = [
        ': this is a comment\n\n',
        'event: custom\n',
        'data: {"type":"text","content":"real data"}\n\n',
        'data: {"type":"done"}\n\n',
      ];
      globalThis.fetch = vi.fn(() => Promise.resolve(mockSSEResponse(sseChunks))) as any;

      const receivedText: string[] = [];
      const { start } = useSSEStream(
        { url: '/api/v1/test', method: 'POST', body: {} },
        {
          onText: (content) => receivedText.push(content),
        }
      );

      await start();

      expect(receivedText).toEqual(['real data']);
    });
  });

  describe('callback chaining', () => {
    it('should call all callbacks in order: emotion → text → done', async () => {
      const sseChunks = [
        'data: {"type":"emotion","emotion":"happy","character_id":"c1"}\n\n',
        'data: {"type":"text","content":"Hello!"}\n\n',
        'data: {"type":"done","session_id":"s1","node_id":"n1"}\n\n',
      ];
      globalThis.fetch = vi.fn(() => Promise.resolve(mockSSEResponse(sseChunks))) as any;

      const callOrder: string[] = [];
      const { start } = useSSEStream(
        { url: '/api/v1/test', method: 'POST', body: {} },
        {
          onEmotion: () => callOrder.push('emotion'),
          onText: () => callOrder.push('text'),
          onDone: () => callOrder.push('done'),
        }
      );

      await start();

      expect(callOrder).toEqual(['emotion', 'text', 'done']);
    });

    it('should work with only onText callback (others optional)', async () => {
      const sseChunks = [
        'data: {"type":"emotion","emotion":"happy"}\n\n',
        'data: {"type":"text","content":"text"}\n\n',
        'data: {"type":"affection_update","value":50}\n\n',
        'data: {"type":"gm_update","player_options":[]}\n\n',
        'data: {"type":"done"}\n\n',
        'data: {"type":"error","message":"err"}\n\n',
      ];
      globalThis.fetch = vi.fn(() => Promise.resolve(mockSSEResponse(sseChunks))) as any;

      const receivedText: string[] = [];
      const { start } = useSSEStream(
        { url: '/api/v1/test', method: 'POST', body: {} },
        {
          onText: (content) => receivedText.push(content),
        }
      );

      // Should not throw even though only onText is provided
      await start();

      expect(receivedText).toEqual(['text']);
    });
  });
});
