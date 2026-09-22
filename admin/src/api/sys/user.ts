import { defHttp } from '@/utils/http/axios';
import { LoginParams, LoginResultModel, GetUserInfoModel } from './model/userModel';

import { ErrorMessageMode } from '#/axios';

// Note: The isekai backend returns raw JSON (not wrapped in {code, result, message}),
// so we use isTransformResponse: false to bypass Vben's response transformer.

enum Api {
  Login = '/auth/login',
  GetUserInfo = '/user/profile',
  GetPermCode = '/getPermCode',
}

/**
 * @description: user login api
 * Backend returns: { access_token: string, refresh_token: string }
 * We map it to Vben's LoginResultModel { token, roles, userId }
 */
export async function loginApi(
  params: LoginParams,
  mode: ErrorMessageMode = 'modal',
): Promise<LoginResultModel> {
  const raw = await defHttp.post<{ access_token: string; refresh_token: string }>(
    {
      url: Api.Login,
      params: { email: params.username, password: params.password },
    },
    {
      errorMessageMode: mode,
      isTransformResponse: false,
    },
  );
  return {
    token: raw.access_token,
    roles: [{ roleName: 'super', value: 'super' }],
    userId: 'admin',
  };
}

/**
 * @description: getUserInfo
 * Backend returns: { id, email, display_name, is_admin }
 * We map it to Vben's GetUserInfoModel
 */
export async function getUserInfo(): Promise<GetUserInfoModel> {
  const raw = await defHttp.get<{
    id: string;
    email: string;
    display_name?: string;
    is_admin?: boolean;
  }>({ url: Api.GetUserInfo }, { errorMessageMode: 'none', isTransformResponse: false });

  return {
    userId: raw.id,
    username: raw.email,
    realName: raw.display_name || raw.email,
    avatar: '',
    roles: [{ roleName: 'super', value: 'super' }],
  };
}

export function getPermCode() {
  return defHttp.get<string[]>({ url: Api.GetPermCode });
}

/**
 * @description: logout — just clear token locally, no backend endpoint needed
 */
export function doLogout() {
  return Promise.resolve();
}
