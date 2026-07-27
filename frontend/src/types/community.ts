/**
 * 帖子相关类型定义 (CR-011)
 */

export interface Post {
  id: string;
  title: string;
  content: string;
  images: string[];
  author: {
    id: string;
    name: string;
    avatar: string;
  };
  stats: {
    likes: number;
    comments: number;
    views: number;
  };
  views_count: number;
  comment_count: number;
  like_count: number;
  is_liked: boolean;
  created_at: string;
}

export interface PostsResponse {
  posts: Post[];
  total: number;
  has_more: boolean;
}

export interface SearchResponse {
  posts: Post[];
  total: number;
  suggestions: string[];
}

export interface LikeResponse {
  status: 'success';
  likes_count: number;
}

export interface DeletePostResponse {
  status: 'success';
  message: string;
}

export type PostTab = 'recommend' | 'latest' | 'hot' | 'mine';
