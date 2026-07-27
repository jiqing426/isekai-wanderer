import { useAuthStore } from '@/stores/auth';
import router from '@/router';

const API_BASE = '/api/v1';

// AC-API-004: Error code → Chinese message mapping
const ERROR_MESSAGES: Record<string, string> = {
  // Auth errors
  AUTH_INVALID_CREDENTIALS: '邮箱或密码不正确',
  AUTH_TOKEN_EXPIRED: '登录已过期，请重新登录',
  AUTH_TOKEN_INVALID: '登录凭证无效，请重新登录',
  AUTH_REFRESH_FAILED: '刷新令牌失败，请重新登录',
  AUTH_EMAIL_NOT_VERIFIED: '邮箱未验证，请查看邮箱完成验证',
  AUTH_EMAIL_EXISTS: '该邮箱已被注册',
  AUTH_USER_NOT_FOUND: '用户不存在',
  AUTH_OAUTH_FAILED: '第三方登录失败，请重试',
  AUTH_OAUTH_ALREADY_LINKED: '该第三方账号已绑定其他用户',
  AUTH_FORBIDDEN: '没有权限执行此操作',

  // Game errors
  GAME_NOT_FOUND: '游戏存档不存在或已过期',
  GAME_ALREADY_ENDED: '游戏已结束',
  GAME_INVALID_CHOICE: '无效的选择',
  GAME_SCRIPT_NOT_FOUND: '剧本不存在',
  GAME_SESSION_NOT_FOUND: '游戏会话不存在',
  GAME_CANNOT_RESTART: '无法重新开始游戏',

  // Payment errors
  PAYMENT_FAILED: '支付失败，请重试',
  PAYMENT_INSUFFICIENT_FUNDS: '余额不足',
  PAYMENT_ALREADY_PURCHASED: '已购买过此内容',
  PAYMENT_ITEM_NOT_FOUND: '商品不存在',

  // Script errors
  SCRIPT_NOT_FOUND: '剧本不存在',
  SCRIPT_LOCKED: '剧本需要解锁',
  SCRIPT_PREMIUM_ONLY: '该剧本仅限高级订阅用户',

  // Community errors
  POST_NOT_FOUND: '帖子不存在',
  POST_DELETED: '帖子已被删除',
  COMMENT_NOT_FOUND: '评论不存在',
  RATE_LIMITED: '操作过于频繁，请稍后再试',

  // Daily / Check-in
  DAILY_ALREADY_CHECKED_IN: '今日已签到',
  DAILY_NOT_FOUND: '签到记录不存在',

  // Gallery / Collection
  ITEM_ALREADY_OWNED: '已拥有此物品',
  ITEM_NOT_FOUND: '物品不存在',
  COLLECTION_FULL: '收藏已满',

  // Share
  SHARE_NOT_FOUND: '分享内容不存在或已过期',
  SHARE_EXPIRED: '分享链接已过期',

  // Generic
  VALIDATION_ERROR: '输入数据有误，请检查',
  INTERNAL_ERROR: '服务器内部错误，请稍后重试',
  NOT_FOUND: '请求的资源不存在',
  SERVICE_UNAVAILABLE: '服务暂时不可用，请稍后重试',
};

/**
 * AC-API-004: Translate error code or message to user-friendly Chinese.
 */
function translateError(errorCode?: string, detail?: string): string {
  // 1. Exact error_code match
  if (errorCode && ERROR_MESSAGES[errorCode]) {
    return ERROR_MESSAGES[errorCode];
  }
  // 2. Partial match on detail message
  if (detail) {
    // 2a. Insufficient fragments pattern (backend returns English)
    const fragMatch = detail.match(/Insufficient fragments\.\s*Need\s+(\d+),?\s*have\s+(\d+)/i);
    if (fragMatch) {
      return `碎片不足，需要 ${fragMatch[1]} 碎片，当前仅有 ${fragMatch[2]} 碎片`;
    }
    const upper = detail.toUpperCase();
    for (const [code, msg] of Object.entries(ERROR_MESSAGES)) {
      if (upper.includes(code.replace(/_/g, ' ')) || upper.includes(code)) {
        return msg;
      }
    }
    // 3. HTTP status text fallback
    if (/^\d{3}$/.test(detail)) {
      const status = parseInt(detail, 10);
      if (status === 404) return '请求的资源不存在';
      if (status === 403) return '没有权限执行此操作';
      if (status === 429) return '操作过于频繁，请稍后再试';
      if (status >= 500) return '服务器内部错误，请稍后重试';
    }
  }
  // 4. Fallback
  return detail || '操作失败，请稍后重试';
}

// Token refresh guard — prevents concurrent refresh calls
let refreshing: Promise<boolean> | null = null;

async function tryRefreshToken(): Promise<boolean> {
  if (refreshing) return refreshing;
  refreshing = (async () => {
    try {
      const auth = useAuthStore();
      if (!auth.refreshToken) return false;
      const res = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: auth.refreshToken }),
      });
      if (!res.ok) return false;
      const data = await res.json();
      auth.setTokens(data.access_token, data.refresh_token);
      return true;
    } catch (err) {
      console.warn('Token 刷新失败:', err instanceof Error ? err.message : err);
      return false;
    } finally {
      refreshing = null;
    }
  })();
  return refreshing;
}

async function request<T>(
  path: string,
  options: RequestInit & { skipAutoLogout?: boolean } = {},
  _isRetry = false,
): Promise<T> {
  const { skipAutoLogout, ...fetchOptions } = options;
  const auth = useAuthStore();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(fetchOptions.headers as Record<string, string> || {}),
  };

  if (auth.accessToken) {
    headers['Authorization'] = `Bearer ${auth.accessToken}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...fetchOptions,
    headers,
  });

  if (response.status === 401 && !_isRetry) {
    const errorBody = await response.json().catch(() => ({ error_code: 'AUTH_TOKEN_EXPIRED', message: '' }));

    if (errorBody.error_code === 'AUTH_TOKEN_EXPIRED' && auth.refreshToken) {
      const refreshed = await tryRefreshToken();
      if (refreshed) {
        return request<T>(path, options, true);
      }
    }

    // 如果调用方要求不自动 logout，则只抛出错误，不执行 logout 和跳转
    if (skipAutoLogout) {
      const err = new Error(translateError(errorBody.error_code, errorBody.message));
      (err as any).errorCode = errorBody.error_code;
      (err as any).status = response.status;
      throw err;
    }

    // 区分「token 过期」和「从未有效登录」——没有 refresh token 时不弹"登录已过期"
    const wasLoggedIn = !!auth.refreshToken;
    auth.logout();
    if (wasLoggedIn) {
      router.push({ name: 'Login', query: { expired: '1' } });
    } else {
      router.push({ name: 'Login' });
    }
    throw new Error(translateError(errorBody.error_code, errorBody.message));
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ error_code: '', message: `HTTP ${response.status}` }));
    // AC-API-004: Throw user-friendly Chinese message
    // Backend returns {error_code, message}; legacy returns {detail}
    const rawDetail = errorBody.message || errorBody.detail || `HTTP ${response.status}`;
    const friendlyMsg = translateError(errorBody.error_code, rawDetail);
    const err = new Error(friendlyMsg);
    (err as any).errorCode = errorBody.error_code;
    throw err;
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string, options?: { skipAutoLogout?: boolean }) => request<T>(path, { method: 'GET', ...options }),
  post: <T>(path: string, body?: unknown, options?: { skipAutoLogout?: boolean }) =>
    request<T>(path, { method: 'POST', body: body ? JSON.stringify(body) : undefined, ...options }),
  put: <T>(path: string, body?: unknown, options?: { skipAutoLogout?: boolean }) =>
    request<T>(path, { method: 'PUT', body: body ? JSON.stringify(body) : undefined, ...options }),
  patch: <T>(path: string, body?: unknown, options?: { skipAutoLogout?: boolean }) =>
    request<T>(path, { method: 'PATCH', body: body ? JSON.stringify(body) : undefined, ...options }),
  delete: <T>(path: string, options?: { skipAutoLogout?: boolean }) => request<T>(path, { method: 'DELETE', ...options }),
};
