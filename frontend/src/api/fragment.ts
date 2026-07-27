/**
 * 碎片中心 API
 */
import { api } from './http';
import type { ShopGoodsList, ExchangeRequest, ExchangeResponse, TransactionList } from '@/types/fragment';
import type { UserAsset } from '@/types/personal-center';

/**
 * 获取碎片余额
 */
export function getMyAsset() {
  return api.get<UserAsset>('/users/me/asset');
}

/**
 * 获取商城商品列表
 */
export function getShopGoods(params?: { category?: string; page?: number; page_size?: number }) {
  const query = new URLSearchParams();
  if (params?.category) query.set('category', params.category);
  if (params?.page) query.set('page', String(params.page));
  if (params?.page_size) query.set('page_size', String(params.page_size));
  const qs = query.toString();
  return api.get<ShopGoodsList>(`/fragment/shop/goods${qs ? `?${qs}` : ''}`);
}

/**
 * 兑换道具
 */
export function exchangeGoods(data: ExchangeRequest) {
  return api.post<ExchangeResponse>('/fragment/exchange', data);
}

/**
 * 获取碎片收支流水
 */
export function getFragmentTransactions(params?: { type?: string; page?: number; page_size?: number }) {
  const query = new URLSearchParams();
  if (params?.type) query.set('type', params.type);
  if (params?.page) query.set('page', String(params.page));
  if (params?.page_size) query.set('page_size', String(params.page_size));
  const qs = query.toString();
  return api.get<TransactionList>(`/fragment/transactions${qs ? `?${qs}` : ''}`);
}
