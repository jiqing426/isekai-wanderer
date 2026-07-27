import { api } from './http';

export interface CreateSaveParams {
  session_id: string;
  script_id?: string;
  character_id?: string;
  current_node_id?: string;
  affection_value?: number;
  choice_history?: Array<{ choice_id: string; node_id: string }>;
}

export interface CreateSaveResponse {
  status: string;
  save_id?: string;
}

export const saveApi = {
  /**
   * 创建手动存档
   * POST /api/v1/saves
   */
  createSave(params: CreateSaveParams): Promise<CreateSaveResponse> {
    return api.post('/saves', params);
  },

  /**
   * 获取存档列表
   * GET /api/v1/saves
   */
  getSaves(): Promise<{ saves: Array<{ id: string; created_at: string }> }> {
    return api.get('/saves');
  },

  /**
   * 删除存档
   * DELETE /api/v1/saves/:id
   */
  deleteSave(saveId: string): Promise<{ status: string }> {
    return api.delete(`/saves/${saveId}`);
  },
};
