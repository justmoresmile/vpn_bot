import { apiRequest } from './api'


export type WalletResponse = {
  balance_kopecks: number
  balance_rubles: number
  device_limit: number
  daily_price_kopecks: number
  daily_price_rubles: number
  days_available: number
  max_devices: number
}


export type BalanceTopupResponse = {
  id: number
  amount: number
  amount_kopecks: number
  status: string
  confirmation_url: string | null
}


export async function getWallet(): Promise<WalletResponse> {
  return apiRequest<WalletResponse>(
    '/payment/wallet',
  )
}


export type PaymentMethod =
  | 'sbp'
  | 'bank_card'


export async function createBalanceTopup(
  amount: number,
  paymentMethod: PaymentMethod = 'sbp',
): Promise<BalanceTopupResponse> {

  return apiRequest<BalanceTopupResponse>(
    '/payment/topup',
    {
      method: 'POST',
      body: JSON.stringify({
        amount,
        payment_method: paymentMethod,
      }),
    },
  )
}


export type WalletTransaction = {
  id: number
  user_id: number
  type: string
  amount_kopecks: number
  balance_after_kopecks: number
  payment_id: number | null
  description: string | null
  created_at: number
}


export type WalletHistoryResponse = {
  items: WalletTransaction[]
}


export async function getWalletHistory(): Promise<WalletHistoryResponse> {
  return apiRequest<WalletHistoryResponse>(
    '/payment/history',
  )
}
