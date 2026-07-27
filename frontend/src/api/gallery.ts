/**
 * Gallery API - 收藏馆相关接口
 */
import { api } from './http';

export interface CollectionItem {
  id: string;
  item_type: 'cg' | 'achievement' | 'ending';
  item_id: string;
  item_name: string;
  image_url?: string;
  unlocked_at: string;
}

export interface CollectionListResponse {
  collections: CollectionItem[];
  total: number;
}

/**
 * 获取收藏品列表
 */
export function getCollections(): Promise<CollectionListResponse> {
  return api.get('/gallery/collections');
}
