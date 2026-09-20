import { api } from './http';

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
    const params = new URLSearchParams({ page: String(page), pageSize: String(pageSize) });
    if (tag) params.append('tag', tag);
    return api.get(`/lorebook?${params.toString()}`);
  },

  get(id: string): Promise<LorebookEntry> {
    return api.get(`/lorebook/${id}`);
  },

  create(data: LorebookCreateData): Promise<LorebookEntry> {
    return api.post('/lorebook', data);
  },

  update(id: string, data: LorebookUpdateData): Promise<LorebookEntry> {
    return api.put(`/lorebook/${id}`, data);
  },

  delete(id: string): Promise<void> {
    return api.delete(`/lorebook/${id}`);
  },
};
