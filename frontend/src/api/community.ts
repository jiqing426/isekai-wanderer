/**
 * 社区帖子相关 API (CR-011)
 */
import { api } from './http';
import type {
  PostsResponse,
  SearchResponse,
  LikeResponse,
  DeletePostResponse,
  PostTab
} from '@/types/community';

/**
 * 获取帖子列表
 */
export function getPosts(params?: {
  tab?: PostTab;
  page?: number;
  page_size?: number;
  search?: string;
}): Promise<PostsResponse> {
  const query = new URLSearchParams();
  if (params?.tab) query.set('tab', params.tab);
  if (params?.page) query.set('page', String(params.page));
  if (params?.page_size) query.set('page_size', String(params.page_size));
  if (params?.search) query.set('search', params.search);
  
  const qs = query.toString();
  return api.get(`/community/posts${qs ? `?${qs}` : ''}`);
}

/**
 * 搜索帖子
 */
export function searchPosts(params: {
  keyword: string;
  page?: number;
  page_size?: number;
}): Promise<SearchResponse> {
  const query = new URLSearchParams();
  query.set('keyword', params.keyword);
  if (params.page) query.set('page', String(params.page));
  if (params.page_size) query.set('page_size', String(params.page_size));
  
  const qs = query.toString();
  return api.get(`/community/posts/search?${qs}`);
}

/**
 * 点赞帖子
 */
export function likePost(postId: string): Promise<LikeResponse> {
  return api.post(`/community/posts/${postId}/like`);
}

/**
 * 取消点赞
 */
export function unlikePost(postId: string): Promise<LikeResponse> {
  return api.delete(`/community/posts/${postId}/like`);
}

/**
 * 删除帖子
 */
export function deletePost(postId: string): Promise<DeletePostResponse> {
  return api.delete(`/community/posts/${postId}`);
}

/**
 * 获取帖子评论
 */
export function getComments(postId: string, params?: { page?: number; page_size?: number }): Promise<{ comments: any[]; total: number }> {
  const query = new URLSearchParams();
  if (params?.page) query.set('page', String(params.page));
  if (params?.page_size) query.set('page_size', String(params.page_size));
  
  const qs = query.toString();
  return api.get(`/community/posts/${postId}/comments${qs ? `?${qs}` : ''}`);
}

/**
 * 创建评论
 */
export function createComment(postId: string, content: string): Promise<{ comment_id: string }> {
  return api.post(`/community/posts/${postId}/comments`, { content });
}

/**
 * 删除评论
 */
export function deleteComment(commentId: string): Promise<void> {
  return api.delete(`/community/posts/comments/${commentId}`);
}

/**
 * 获取帖子详情（增加浏览量）
 */
export function getPostDetail(postId: string): Promise<any> {
  return api.get(`/community/posts/${postId}`);
}
