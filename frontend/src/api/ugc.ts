/**
 * UGC (User Generated Content) API
 */
import { api } from './http';

export interface Post {
  id: string;
  user_id: string;
  username: string;
  title: string;
  content: string;
  image_urls?: string[];
  like_count: number;
  comment_count: number;
  created_at: string;
  updated_at: string;
}

export interface PostListResponse {
  posts: Post[];
  total: number;
  page: number;
  page_size: number;
}

export interface PostListParams {
  page?: number;
  page_size?: number;
}

/**
 * 获取帖子列表
 */
export function getPosts(params: PostListParams = {}): Promise<PostListResponse> {
  const query = new URLSearchParams();
  if (params.page) query.append('page', params.page.toString());
  if (params.page_size) query.append('page_size', params.page_size.toString());
  
  const qs = query.toString();
  return api.get(`/ugc/posts${qs ? `?${qs}` : ''}`);
}
