import { api } from './http';

export interface FreeChatParams {
  character_id: string;
  message: string;
  script_id?: string;
  session_id?: string;
}

export interface FreeChatResponse {
  reply: string;
  emotion?: string;
  character_id: string;
  session_id?: string;
}

export interface FreeChatSession {
  id: string;
  character_id: string;
  character_name: string;
  last_message: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export const chatApi = {
  /**
   * 发送自由对话消息
   * POST /api/v1/chat/free
   */
  sendFreeChat(params: FreeChatParams): Promise<FreeChatResponse> {
    return api.post('/chat/free', params);
  },

  /**
   * 获取自由对话历史会话列表
   * GET /api/v1/chat/free/sessions
   */
  getFreeChatSessions(): Promise<{ sessions: FreeChatSession[] }> {
    return api.get('/chat/free/sessions');
  },

  /**
   * 获取特定角色的对话历史
   * GET /api/v1/chat/free/history?character_id=xxx
   */
  getFreeChatHistory(characterId: string, limit = 50): Promise<{ messages: Array<{ role: 'user' | 'assistant'; content: string; timestamp: string }> }> {
    return api.get(`/chat/free/history?character_id=${characterId}&limit=${limit}`);
  },
};
