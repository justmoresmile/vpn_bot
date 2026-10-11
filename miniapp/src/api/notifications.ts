import { apiRequest } from './api'


export type NotificationItem = {
  id: number
  type: string
  title: string
  message: string
  related_type: string | null
  related_id: number | null
  is_read: boolean
  created_at: number
}


export async function getNotifications() {
  return apiRequest<NotificationItem[]>(
    '/notifications',
  )
}


export async function getUnreadNotificationCount() {
  return apiRequest<{ count: number }>(
    '/notifications/unread-count',
  )
}


export async function markNotificationRead(
  notificationId: number,
) {
  return apiRequest<{ success: boolean }>(
    `/notifications/${notificationId}/read`,
    {
      method: 'POST',
    },
  )
}


export async function markAllNotificationsRead() {
  return apiRequest<{ success: boolean }>(
    '/notifications/read-all',
    {
      method: 'POST',
    },
  )
}
