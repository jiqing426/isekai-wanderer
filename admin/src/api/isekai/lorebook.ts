import { defHttp } from '@/utils/http/axios';

// Note: The isekai backend returns raw JSON (not wrapped in {code, result, message}),
// so we use isTransformResponse: false to bypass Vben's response transformer.

export interface LorebookEntry {
  id: string;
  title: string;
  content: string;
  tags: string[];
  priority: number;
  status: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface LorebookListItem {
  id: string;
  title: string;
  tags: string[];
  priority: number;
  status: string;
  updated_at: string;
}

export interface LorebookListResponse {
  items: LorebookListItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface LorebookCreateData {
  title: string;
  content: string;
  tags: string[];
  priority: number;
}

export interface LorebookUpdateData {
  title?: string;
  content?: string;
  tags?: string[];
  priority?: number;
}

export const lorebookApi = {
  list(page = 1, pageSize = 20, tag?: string): Promise<LorebookListResponse> {
    const params: Record<string, any> = { page, pageSize };
    if (tag) params.tag = tag;
    return defHttp.get<LorebookListResponse>(
      { url: '/lorebook', params },
      { isTransformResponse: false },
    );
  },

  get(id: string): Promise<LorebookEntry> {
    return defHttp.get<LorebookEntry>(
      { url: `/lorebook/${id}` },
      { isTransformResponse: false },
    );
  },

  create(data: LorebookCreateData): Promise<LorebookEntry> {
    return defHttp.post<LorebookEntry>(
      { url: '/lorebook', params: data },
      { isTransformResponse: false },
    );
  },

  update(id: string, data: LorebookUpdateData): Promise<LorebookEntry> {
    return defHttp.put<LorebookEntry>(
      { url: `/lorebook/${id}`, params: data },
      { isTransformResponse: false },
    );
  },

  delete(id: string): Promise<void> {
    return defHttp.delete<void>(
      { url: `/lorebook/${id}` },
      { isTransformResponse: false },
    );
  },
};
