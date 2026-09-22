import { defHttp } from '@/utils/http/axios';

// The isekai backend returns raw JSON (not wrapped in {code, result, message}),
// so we use isTransformResponse: false to bypass Vben's response transformer.

export interface SystemConfigItem {
  key: string;
  value: string;
  description?: string;
  category?: string;
  is_secret?: boolean;
  updated_at?: string;
}

export const systemConfigApi = {
  getAll(): Promise<SystemConfigItem[]> {
    return defHttp.get<SystemConfigItem[]>(
      { url: '/admin/system-config' },
      { isTransformResponse: false },
    );
  },

  update(key: string, value: string): Promise<SystemConfigItem> {
    return defHttp.put<SystemConfigItem>(
      { url: '/admin/system-config', data: { key, value } },
      { isTransformResponse: false },
    );
  },
};
