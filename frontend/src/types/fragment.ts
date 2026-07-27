/**
 * 碎片中心相关类型
 */

export interface ShopGood {
  id: string;
  name: string;
  description: string;
  category: 'cg' | 'voice' | 'skin' | 'item';
  icon_url: string;
  price: number;
  stock: number;
  limit_per_user: number;
  owned: boolean;
  is_available: boolean;
}

export interface ShopGoodsList {
  goods: ShopGood[];
  total: number;
  user_balance: number;
}

export interface ExchangeRequest {
  goods_id: string;
  quantity?: number;
}

export interface ExchangeResponse {
  status: 'ok';
  goods_id: string;
  goods_name: string;
  price: number;
  quantity: number;
  new_balance: number;
  message: string;
}

export interface FragmentTransaction {
  id: string;
  amount: number;
  type: 'income' | 'expense';
  reason: string;
  reason_label?: string;
  description: string;
  created_at: string;
}

export interface TransactionList {
  transactions: FragmentTransaction[];
  total: number;
  page: number;
  page_size: number;
}
