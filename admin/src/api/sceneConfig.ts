import { api } from './http';

export interface SceneConfig {
  id: string;
  node_id: string;
  scene_name: string;
  tags: string[];
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface SceneConfigUpsertData {
  scene_name: string;
  tags: string[];
  description?: string;
}

export const sceneConfigApi = {
  list(scriptId?: string, routeId?: string): Promise<SceneConfig[]> {
    const params = new URLSearchParams();
    if (scriptId) params.append('script_id', scriptId);
    if (routeId) params.append('route_id', routeId);
    const query = params.toString();
    return api.get(`/scene-configs${query ? `?${query}` : ''}`);
  },

  upsert(nodeId: string, data: SceneConfigUpsertData): Promise<SceneConfig> {
    return api.put(`/scene-configs/node/${nodeId}`, data);
  },

  delete(nodeId: string): Promise<void> {
    return api.delete(`/scene-configs/node/${nodeId}`);
  },
};
