import { apiRequest } from './api'


export type AdminSubscription = {
  id: number
  protocol: string
  provider: string
  status: string

  server_id: number | null
  client_email: string | null

  device_limit: number

  billing_mode: string
  billing_enabled: boolean

  created_at: string | null
  expires_at: string | null
  paid_until: string | null
  bonus_until: string | null
  bonus_device_limit: number | null
}


export type AdminUserListItem = {
  id: number

  telegram_id: number | null
  email: string | null

  username: string | null
  first_name: string | null

  is_admin: boolean
  is_blocked: boolean

  balance_kopecks: number
  balance_rubles: number

  subscription: AdminSubscription | null
}


export type AdminUsersResponse = {
  items: AdminUserListItem[]

  total: number
  limit: number
  offset: number
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


export type AdminUserDetail = {
  id: number

  telegram_id: number | null
  email: string | null

  username: string | null
  first_name: string | null

  is_admin: boolean
  is_blocked: boolean

  balance_kopecks: number
  balance_rubles: number

  subscriptions: AdminSubscription[]

  wallet_transactions: WalletTransaction[]
}


export type AdminUserFilter =
  | 'all'
  | 'active'
  | 'expired'
  | 'disabled'
  | 'blocked'
  | 'admins'
  | 'no_subscription'


export async function getAdminUsers(
  options: {
    search?: string
    filter?: AdminUserFilter
    limit?: number
    offset?: number
  } = {},
): Promise<AdminUsersResponse> {

  const params =
    new URLSearchParams()

  if (options.search) {
    params.set(
      'search',
      options.search,
    )
  }

  params.set(
    'filter',
    options.filter ?? 'all',
  )

  params.set(
    'limit',
    String(
      options.limit ?? 50,
    ),
  )

  params.set(
    'offset',
    String(
      options.offset ?? 0,
    ),
  )

  return apiRequest<AdminUsersResponse>(
    `/admin/users?${params.toString()}`,
  )
}


export async function getAdminUser(
  userId: number,
): Promise<AdminUserDetail> {

  return apiRequest<AdminUserDetail>(
    `/admin/users/${userId}`,
  )
}


export async function adjustAdminUserBalance(
  userId: number,
  action: 'credit' | 'debit',
  amountRubles: number,
  description?: string,
): Promise<{
  user_id: number
  action: string
  amount_kopecks: number
  amount_rubles: number
  balance_kopecks: number
  balance_rubles: number
}> {

  return apiRequest(
    `/admin/users/${userId}/balance`,
    {
      method: 'POST',
      body: JSON.stringify({
        action,
        amount_rubles: amountRubles,
        description:
          description || null,
      }),
    },
  )
}


export async function blockAdminUser(
  userId: number,
): Promise<void> {

  await apiRequest(
    `/admin/users/${userId}/block`,
    {
      method: 'POST',
    },
  )
}


export async function unblockAdminUser(
  userId: number,
): Promise<void> {

  await apiRequest(
    `/admin/users/${userId}/unblock`,
    {
      method: 'POST',
    },
  )
}


export async function extendAdminSubscription(
  userId: number,
  subscriptionId: number,
  days: number,
): Promise<{
  subscription_id: number
  user_id: number
  days_added: number
  status: string
  expires_at: string
}> {

  return apiRequest(
    `/admin/users/${userId}` +
    `/subscriptions/${subscriptionId}` +
    `/extend`,
    {
      method: 'POST',
      body: JSON.stringify({
        days,
      }),
    },
  )
}


export async function setAdminSubscriptionUntil(
  userId: number,
  subscriptionId: number,
  until: string,
): Promise<{
  subscription_id: number
  user_id: number
  status: string
  paid_until: string | null
  expires_at: string | null
}> {

  return apiRequest(
    `/admin/users/${userId}` +
      `/subscriptions/${subscriptionId}` +
      `/set-until?until=${encodeURIComponent(until)}`,
    {
      method: 'POST',
    },
  )
}


export async function removeAdminSubscriptionBonus(
  userId: number,
  subscriptionId: number,
  days?: number,
): Promise<{
  subscription_id: number
  removed_days: number
  bonus_until: string | null
  paid_until: string | null
  expires_at: string | null
}> {

  const query =
    days === undefined
      ? '?remove_all=true'
      : `?days=${encodeURIComponent(days)}`

  return apiRequest(
    `/admin/users/${userId}` +
      `/subscriptions/${subscriptionId}` +
      `/bonus/remove${query}`,
    {
      method: 'POST',
    },
  )
}
