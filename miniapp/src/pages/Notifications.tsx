import {
  useEffect,
  useState,
} from 'react'

import {
  getNotifications,
  markAllNotificationsRead,
  markNotificationRead,
  type NotificationItem,
} from '../api/notifications'


function formatNotificationDate(
  timestamp: number,
) {

  const date =
    new Date(timestamp * 1000)

  const now =
    new Date()

  const today =
    date.toDateString()
      === now.toDateString()

  if (today) {
    return `Сегодня, ${date.toLocaleTimeString(
      'ru-RU',
      {
        hour: '2-digit',
        minute: '2-digit',
      },
    )}`
  }

  return date.toLocaleDateString(
    'ru-RU',
    {
      day: 'numeric',
      month: 'long',
    },
  )
}


function NotificationsScreen({

  onClose,
  onUnreadChanged,
  onOpenSupportTicket,

}: {

  onClose: () => void
  onUnreadChanged?: () => void
  onOpenSupportTicket?: (
    ticketId: number,
  ) => void

}) {

  const [
    notifications,
    setNotifications,
  ] = useState<NotificationItem[]>([])

  const [
    loading,
    setLoading,
  ] = useState(true)

  const [
    error,
    setError,
  ] = useState<string | null>(null)


  const loadNotifications =
    async () => {

      try {

        setError(null)

        const data =
          await getNotifications()

        setNotifications(data)

      } catch (err) {

        setError(
          err instanceof Error
            ? err.message
            : 'Не удалось загрузить уведомления',
        )

      } finally {

        setLoading(false)

      }

    }


  useEffect(() => {

    void loadNotifications()

  }, [])


  const handleRead =
    async (
      notification: NotificationItem,
    ) => {

      if (notification.is_read) {
        return
      }

      try {

        await markNotificationRead(
          notification.id,
        )

        setNotifications(
          (items) =>
            items.map(
              (item) =>
                item.id === notification.id
                  ? {
                      ...item,
                      is_read: true,
                    }
                  : item,
            ),
        )

        onUnreadChanged?.()

      } catch (err) {

        console.error(
          'Failed to mark notification read',
          err,
        )

      }

    }


  const handleNotificationClick =
    async (
      notification: NotificationItem,
    ) => {

      await handleRead(notification)

      if (
        notification.type
          === 'support_reply'
        && notification.related_type
          === 'support_ticket'
        && notification.related_id
      ) {

        onOpenSupportTicket?.(
          notification.related_id,
        )

      }

    }


  const handleReadAll =
    async () => {

      try {

        await markAllNotificationsRead()

        setNotifications(
          (items) =>
            items.map(
              (item) => ({
                ...item,
                is_read: true,
              }),
            ),
        )

        onUnreadChanged?.()

      } catch (err) {

        console.error(
          'Failed to mark all notifications read',
          err,
        )

      }

    }


  const hasUnread =
    notifications.some(
      (item) => !item.is_read,
    )


  return (

    <div className="notifications-page">

      <div className="notifications-header">

        <button
          className="back-button"
          onClick={onClose}
          aria-label="Назад"
        >

          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="M15 18l-6-6 6-6" />
          </svg>

        </button>


        <div
          style={{
            flex: 1,
          }}
        >

          <div className="notifications-title">
            Уведомления
          </div>

          <div className="notifications-subtitle">
            Важные сообщения JustVPN
          </div>

        </div>


        {hasUnread && (

          <button
            type="button"
            onClick={() => {
              void handleReadAll()
            }}
            style={{
              border: 0,
              background: 'transparent',
              color: 'var(--accent)',
              fontSize: 12,
              fontWeight: 700,
              cursor: 'pointer',
              padding: '8px 0 8px 8px',
            }}
          >
            Прочитать всё
          </button>

        )}

      </div>


      <div className="notification-list">

        {loading && (

          <div
            style={{
              padding: '24px 4px',
              textAlign: 'center',
              color: 'var(--text-secondary)',
            }}
          >
            Загрузка...
          </div>

        )}


        {!loading && error && (

          <div
            style={{
              padding: 20,
              textAlign: 'center',
              color: 'var(--text-secondary)',
            }}
          >
            {error}
          </div>

        )}


        {!loading
          && !error
          && notifications.length === 0 && (

          <div
            style={{
              padding: '40px 20px',
              textAlign: 'center',
              color: 'var(--text-secondary)',
            }}
          >

            <div
              style={{
                fontSize: 34,
                marginBottom: 12,
              }}
            >
              🔔
            </div>

            <div
              style={{
                fontSize: 15,
                fontWeight: 750,
                color: 'var(--text)',
              }}
            >
              Пока уведомлений нет
            </div>

            <div
              style={{
                marginTop: 6,
                fontSize: 13,
              }}
            >
              Здесь появятся важные сообщения JustVPN
            </div>

          </div>

        )}


        {notifications.map(
          (notification) => (

            <div
              key={notification.id}
              className={
                notification.is_read
                  ? 'notification-card'
                  : 'notification-card unread'
              }
              onClick={() => {
                void handleNotificationClick(
                  notification,
                )
              }}
              style={{
                cursor: notification.is_read
                  ? 'default'
                  : 'pointer',
              }}
            >

              <div className="notification-icon">

                {notification.type
                  === 'support_reply'
                  ? (

                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.8"
                    >
                      <path
                        d="M21 11.5a8.4 8.4 0 0 1-9 8.3 9.3 9.3 0 0 1-4-.9L3 20l1.3-4A8 8 0 0 1 3 11.5 8.4 8.4 0 0 1 12 3a8.4 8.4 0 0 1 9 8.5Z"
                      />
                    </svg>

                  )
                  : (

                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.8"
                    >
                      <path
                        d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"
                      />
                      <path d="M10 21h4" />
                    </svg>

                  )}

              </div>


              <div className="notification-content">

                <div className="notification-top">

                  <strong>
                    {notification.title}
                  </strong>

                  <span>
                    {formatNotificationDate(
                      notification.created_at,
                    )}
                  </span>

                </div>

                <p>
                  {notification.message}
                </p>

              </div>


              {!notification.is_read && (
                <span className="notification-unread-dot" />
              )}

            </div>

          ),
        )}

      </div>

    </div>

  )

}

export default NotificationsScreen
