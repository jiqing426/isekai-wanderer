import { ref, onUnmounted } from 'vue';

export interface SSEMessage {
  type: 'text' | 'emotion' | 'scene' | 'choice' | 'affection_update' | 'memory_recall' | 'done';
  content?: string;
  character_id?: string;
  emotion?: string;
  scene_id?: string;
  bgm?: string;
  options?: ChoiceOption[];
  value?: number;
  level?: string;
  text?: string;
  session_id?: string;
  node_id?: string;
}

export interface ChoiceOption {
  id: string;
  text: string;
  affection_delta?: number;
}

export function useSSE(url: string) {
  const messages = ref<SSEMessage[]>([]);
  const isConnected = ref(false);
  const error = ref<string | null>(null);
  let eventSource: EventSource | null = null;

  function connect() {
    if (eventSource) {
      eventSource.close();
    }

    eventSource = new EventSource(url);
    isConnected.value = true;
    error.value = null;

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as SSEMessage;
        messages.value.push(data);
      } catch (err) {
        console.error('SSE parse error:', err);
      }
    };

    eventSource.onerror = () => {
      isConnected.value = false;
      error.value = 'SSE connection failed';
      eventSource?.close();
    };

    eventSource.addEventListener('done', (event) => {
      try {
        const data = JSON.parse((event as MessageEvent).data) as SSEMessage;
        messages.value.push(data);
      } catch (err) {
        console.error('SSE done event parse error:', err);
      }
      eventSource?.close();
      isConnected.value = false;
    });
  }

  function disconnect() {
    eventSource?.close();
    eventSource = null;
    isConnected.value = false;
  }

  function reset() {
    messages.value = [];
  }

  onUnmounted(() => {
    disconnect();
  });

  return {
    messages,
    isConnected,
    error,
    connect,
    disconnect,
    reset,
  };
}
