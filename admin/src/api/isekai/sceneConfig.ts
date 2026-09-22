import { defHttp } from '@/utils/http/axios';

// Note: The isekai backend returns raw JSON (not wrapped in {code, result, message}),
// so we use isTransformResponse: false to bypass Vben's response transformer.

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
    const params: Record<string, any> = {};
    if (scriptId) params.script_id = scriptId;
    if (routeId) params.route_id = routeId;
    return defHttp.get<SceneConfig[]>(
      { url: '/scene-configs', params },
      { isTransformResponse: false },
    );
  },

  upsert(nodeId: string, data: SceneConfigUpsertData): Promise<SceneConfig> {
    return defHttp.put<SceneConfig>(
      { url: `/scene-configs/node/${nodeId}`, params: data },
      { isTransformResponse: false },
    );
  },

  delete(nodeId: string): Promise<void> {
    return defHttp.delete<void>(
      { url: `/scene-configs/node/${nodeId}` },
      { isTransformResponse: false },
    );
  },
};
