import {
  useEffect,
  useState,
} from 'react'

import type {
  Subscription,
} from '../api/subscription'

import {
  deleteSubscriptionDevice,
  getSubscriptionLink,
  setSubscriptionDeviceLimit,
} from '../api/subscription'

import type {
  WalletResponse,
} from '../api/balance'

import happIcon from '../assets/happ.png'

import PageTitle from '../components/common/PageTitle'


const DAILY_PRICES: Record<number, number> = {
  1: 3,
  2: 5,
  3: 8,
  4: 10,
  5: 13,
  6: 14,
  7: 16,
  8: 18,
  9: 19,
  10: 21,
}


function SubscriptionScreen({

  subscription,

  renewOpen,

  setRenewOpen,

  subscriptionDevices,

  wallet,


  onDeviceLimitChanged,

  onDeviceDeleted,

}: {

  subscription: Subscription | null

  renewOpen: boolean

  setRenewOpen: React.Dispatch<
    React.SetStateAction<boolean>
  >

  subscriptionDevices: {
    count: number
    limit: number
    devices: {
      id: string
      model: string | null
      os: string | null
      os_version: string | null
      client_app: string | null
      client_version: string | null
      is_active: boolean
      last_seen_at: string | null
    }[]
  }

  wallet: WalletResponse | null


  onDeviceLimitChanged: (
    deviceLimit: number,
  ) => void

  onDeviceDeleted: (
    hwid: string,
  ) => void

}) {

  /*
   * Временно оставляем эти props,
   * чтобы не ломать состояние App.tsx.
   * Позже удалим старый renewOpen целиком.
   */
  void renewOpen
  void setRenewOpen


  const [
    deletingDeviceId,
    setDeletingDeviceId,
  ] = useState<string | null>(null)


  const [
    reduceTargetLimit,
    setReduceTargetLimit,
  ] = useState<number | null>(null)


  const [
    subscriptionLink,
    setSubscriptionLink,
  ] = useState<string | null>(null)

  const [
    linkLoading,
    setLinkLoading,
  ] = useState(false)

  const [
    linkError,
    setLinkError,
  ] = useState<string | null>(null)

  const [
    ,
    setSelectedDeviceLimit,
  ] = useState(
    wallet?.device_limit
      ?? subscriptionDevices.limit
      ?? 2,
  )

  const [
    savedDeviceLimit,
    setSavedDeviceLimit,
  ] = useState(
    wallet?.device_limit
      ?? subscriptionDevices.limit
      ?? 2,
  )

  const [
    ,
    setSavedDailyPrice,
  ] = useState(
    wallet?.daily_price_rubles
      ?? 5,
  )

  const [
    ,
    setDeviceLimitError,
  ] = useState<string | null>(null)

  const [
    ,
    setDeviceLimitSuccess,
  ] = useState<string | null>(null)

  const [
    copied,
    setCopied,
  ] = useState(false)


  useEffect(() => {

    const deviceLimit =
      wallet?.device_limit
      ?? subscriptionDevices.limit
      ?? 2

    setSelectedDeviceLimit(
      deviceLimit,
    )

    setSavedDeviceLimit(
      deviceLimit,
    )

    setSavedDailyPrice(
      wallet?.daily_price_rubles
        ?? DAILY_PRICES[deviceLimit]
        ?? 5,
    )

  }, [
    wallet?.device_limit,
    wallet?.daily_price_rubles,
    subscriptionDevices.limit,
  ])


  useEffect(() => {

    async function loadLink() {

      if (!subscription) {

        setSubscriptionLink(null)
        setLinkError(null)

        return
      }

      try {

        setLinkLoading(true)
        setLinkError(null)

        const response =
          await getSubscriptionLink(
            subscription.id,
          )

        setSubscriptionLink(
          response.config,
        )

      } catch (error) {

        setSubscriptionLink(null)

        setLinkError(
          error instanceof Error
            ? error.message
            : 'Не удалось получить ссылку',
        )

      } finally {

        setLinkLoading(false)

      }
    }

    loadLink()

  }, [subscription])


  const subscriptionLinkDisplay =
    subscriptionLink
      ? `sub/${subscriptionLink.slice(-6)}`
      : null


  async function handleReduceAndDeleteDevice(
    hwid: string,
  ) {

    if (
      !subscription
      || reduceTargetLimit === null
    ) {
      return
    }

    const targetLimit =
      reduceTargetLimit

    /*
     * subscriptionDevices.count — количество
     * устройств ДО текущего удаления.
     */
    const remainingCount =
      Math.max(
        0,
        subscriptionDevices.count - 1,
      )

    try {

      setDeletingDeviceId(
        hwid,
      )

      setDeviceLimitError(null)
      setDeviceLimitSuccess(null)

      await deleteSubscriptionDevice(
        subscription.id,
        hwid,
      )

      /*
       * Сразу убираем устройство из состояния App.
       */
      onDeviceDeleted(
        hwid,
      )


      /*
       * Если устройств всё ещё больше,
       * чем позволяет выбранный новый тариф,
       * popup оставляем открытым.
       */
      if (
        remainingCount
        > targetLimit
      ) {

        return
      }


      /*
       * Нужное количество устройств удалено.
       * Теперь безопасно уменьшаем тариф.
       */
      const response =
        await setSubscriptionDeviceLimit(
          subscription.id,
          targetLimit,
        )

      setSavedDeviceLimit(
        response.device_limit,
      )

      setSelectedDeviceLimit(
        response.device_limit,
      )

      setSavedDailyPrice(
        response.daily_price_rubles,
      )

      onDeviceLimitChanged(
        response.device_limit,
      )

      setReduceTargetLimit(null)

      setDeviceLimitSuccess(
        'Количество устройств изменено',
      )

    } catch (error) {

      setDeviceLimitError(
        error instanceof Error
          ? error.message
          : 'Не удалось изменить количество устройств',
      )

    } finally {

      setDeletingDeviceId(null)

    }
  }


  async function handleDeleteDevice(
    hwid: string,
  ) {

    if (!subscription) {
      return
    }

    try {

      setDeletingDeviceId(
        hwid,
      )

      setDeviceLimitError(null)
      setDeviceLimitSuccess(null)

      await deleteSubscriptionDevice(
        subscription.id,
        hwid,
      )

      onDeviceDeleted(
        hwid,
      )

    } catch (error) {

      setDeviceLimitError(
        error instanceof Error
          ? error.message
          : 'Не удалось удалить устройство',
      )

    } finally {

      setDeletingDeviceId(null)

    }
  }


  async function copySubscriptionLink() {

    if (!subscriptionLink) {
      return
    }

    try {

      if (
        navigator.clipboard
        && window.isSecureContext
      ) {

        await navigator.clipboard.writeText(
          subscriptionLink,
        )

      } else {

        const textarea =
          document.createElement(
            'textarea',
          )

        textarea.value =
          subscriptionLink

        textarea.style.position =
          'fixed'

        textarea.style.opacity =
          '0'

        document.body.appendChild(
          textarea,
        )

        textarea.focus()
        textarea.select()

        document.execCommand(
          'copy',
        )

        document.body.removeChild(
          textarea,
        )
      }

      setCopied(true)

      window.setTimeout(
        () => setCopied(false),
        1500,
      )

    } catch (error) {

      console.error(
        'Failed to copy subscription link:',
        error,
      )
    }
  }




  if (!subscription) {

    return (
      <>
        <PageTitle
          title="Подписка"
          subtitle="Управление VPN"
        />

        <div className="subscription-timer-card">

          <div className="subscription-timer-header">

            <div>

              <small>
                Подписка не активна
              </small>

              <strong>
                VPN пока не подключён
              </strong>

            </div>

            <div className="subscription-timer-icon">
              🔐
            </div>

          </div>

          <div className="empty-card">

            <strong>
              Нет активной подписки
            </strong>

            <span>
              Активируйте пробный период
              или пополните баланс.
            </span>

          </div>

        </div>

        <section className="section">

          <div className="section-title">
            Как работает оплата
          </div>

          <div className="apps-card">

            <div className="app-item">

              <div className="app-icon">
                💳
              </div>

              <div className="app-info">

                <strong>
                  Посуточная оплата
                </strong>

                <span>
                  Деньги списываются
                  один раз каждые 24 часа
                </span>

              </div>

            </div>

            <div className="divider" />

            <div className="app-item">

              <div className="app-icon">
                📱
              </div>

              <div className="app-info">

                <strong>
                  От 1 до 10 устройств
                </strong>

                <span>
                  Платите только за нужное
                  количество устройств
                </span>

              </div>

            </div>

          </div>

        </section>
      </>
    )
  }


  return (
    <>

      <section className="section">

        <div className="section-title">
          Как подключиться
        </div>

        <div
          className="apps-card"
          style={{
            padding: 0,
            overflow: 'hidden',
          }}
        >

          {/* STEP 1 */}

          <div
            style={{
              padding: 16,
            }}
          >

            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
              }}
            >

              <div
                style={{
                  width: 46,
                  height: 46,
                  borderRadius: 14,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  background:
                    'rgba(127, 127, 127, 0.08)',
                }}
              >
                <img
                  src={happIcon}
                  alt="Happ"
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: 9,
                  }}
                />
              </div>

              <div
                style={{
                  flex: 1,
                  minWidth: 0,
                }}
              >

                <div
                  style={{
                    fontSize: 16,
                    fontWeight: 750,
                  }}
                >
                  1. Установите Happ
                </div>

                <div
                  style={{
                    marginTop: 3,
                    fontSize: 12,
                    opacity: 0.6,
                  }}
                >
                  Приложение для подключения к VPN
                </div>

              </div>

            </div>

            <a
              href="https://happ.info/ru/"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '100%',
                marginTop: 14,
                padding: '11px 14px',
                boxSizing: 'border-box',
                borderRadius: 14,
                background:
                  'rgba(127, 127, 127, 0.10)',
                border:
                  '1px solid rgba(127, 127, 127, 0.12)',
                color: 'inherit',
                fontSize: 14,
                fontWeight: 700,
                textDecoration: 'none',
              }}
            >
              Скачать Happ
            </a>

          </div>


          <div
            style={{
              height: 1,
              marginLeft: 16,
              marginRight: 16,
              background:
                'rgba(127, 127, 127, 0.12)',
            }}
          />


          {/* STEP 2 */}

          <div
            style={{
              padding: 16,
            }}
          >

            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
              }}
            >

              <div
                style={{
                  width: 46,
                  height: 46,
                  borderRadius: 14,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  background:
                    'rgba(127, 127, 127, 0.08)',
                }}
              >
                <img
                  src={happIcon}
                  alt="Happ"
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: 9,
                  }}
                />
              </div>

              <div
                style={{
                  flex: 1,
                  minWidth: 0,
                }}
              >

                <div
                  style={{
                    fontSize: 16,
                    fontWeight: 750,
                  }}
                >
                  2. Добавьте подписку
                </div>

                <div
                  style={{
                    marginTop: 3,
                    fontSize: 12,
                    opacity: 0.6,
                  }}
                >
                  Она добавится в Happ автоматически
                </div>

              </div>

            </div>

            <a
              href={
                subscriptionLink
                  ? `/open/happ/#${
                      encodeURIComponent(
                        subscriptionLink,
                      )
                    }`
                  : 'https://happ.info/ru/'
              }
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '100%',
                marginTop: 14,
                padding: '11px 14px',
                boxSizing: 'border-box',
                borderRadius: 14,
                background:
                  'rgba(127, 127, 127, 0.10)',
                border:
                  '1px solid rgba(127, 127, 127, 0.12)',
                color: 'inherit',
                fontSize: 14,
                fontWeight: 700,
                textDecoration: 'none',
                opacity:
                  subscriptionLink
                    ? 1
                    : 0.6,
              }}
            >
              Открыть в Happ
            </a>

          </div>


          <div
            style={{
              height: 1,
              marginLeft: 16,
              marginRight: 16,
              background:
                'rgba(127, 127, 127, 0.12)',
            }}
          />


          {/* STEP 3 */}

          <div
            style={{
              padding: 16,
            }}
          >

            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
              }}
            >

              <div
                style={{
                  width: 46,
                  height: 46,
                  borderRadius: 14,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  background:
                    'rgba(127, 127, 127, 0.08)',
                  fontSize: 22,
                }}
              >
                ✓
              </div>

              <div
                style={{
                  flex: 1,
                  minWidth: 0,
                }}
              >

                <div
                  style={{
                    fontSize: 16,
                    fontWeight: 750,
                  }}
                >
                  3. Включите VPN
                </div>

                <div
                  style={{
                    marginTop: 3,
                    fontSize: 12,
                    opacity: 0.6,
                    lineHeight: 1.4,
                  }}
                >
                  Нажмите кнопку подключения
                  в приложении Happ
                </div>

              </div>

            </div>

          </div>

        </div>

      </section>


      <section className="section">

        <div className="section-title">
          Ручное подключение
        </div>

        <div className="subscription-link-card">

          <div className="subscription-link-icon">
            🔗
          </div>

          <div className="subscription-link-content">

            <strong>
              Ссылка подписки
            </strong>

            <span>
              Используйте её, если автоматическое
              добавление в Happ не сработало
            </span>

          </div>

        </div>


        <div className="subscription-link">

          {subscriptionLink ? (

            <button
              type="button"
              onClick={async () => {
                if (!subscriptionLink) {
                  return
                }

                await navigator.clipboard.writeText(
                  subscriptionLink,
                )

                setCopied(true)

                window.setTimeout(
                  () => setCopied(false),
                  1500,
                )
              }}
              style={{
                flex: 1,
                minWidth: 0,
                padding: 0,
                border: 0,
                background: 'transparent',
                color: 'inherit',
                textAlign: 'left',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                cursor: 'pointer',
              }}
            >
              {subscriptionLinkDisplay}
            </button>

          ) : (

            <span>
              {
                linkLoading
                  ? 'Загрузка...'
                  : linkError
                    ? 'Не удалось получить ссылку'
                    : 'Ссылка недоступна'
              }
            </span>

          )}

          <div
            style={{
              display: 'flex',
              gap: 8,
              flexShrink: 0,
            }}
          >

            <button
              type="button"
              disabled={!subscriptionLink}
              onClick={copySubscriptionLink}
            >
              {copied
                ? 'Скопировано'
                : 'Копировать'
              }
            </button>

          </div>

        </div>

      </section>


      <section
        id="subscription-devices"
        className="section"
      >

        <div className="devices-header">

          <div className="section-title">
            Мои устройства
          </div>

          <div className="devices-count">
            {subscriptionDevices.count}
            {' / '}
            {savedDeviceLimit}
          </div>

        </div>


        {subscriptionDevices.devices.length > 0 ? (

          <div className="devices-list">

            {subscriptionDevices.devices.map(
              (device) => {

                const deviceName =
                  device.model
                    ?.replace(
                      /^(\S+)\s+\1\s+/i,
                      '$1 ',
                    )
                  ?? 'Устройство'

                const os =
                  device.os?.trim()
                  ?? ''

                const osLower =
                  os.toLowerCase()

                const modelLower =
                  deviceName.toLowerCase()

                const deviceIcon =
                  osLower.includes('windows')
                    ? '💻'
                    : (
                        osLower.includes('tv')
                        || modelLower.includes('tv')
                      )
                      ? '📺'
                      : (
                          osLower.includes('android')
                          || osLower.includes('ios')
                          || modelLower.includes('iphone')
                        )
                        ? '📱'
                        : '🖥️'

                const clientParts =
                  device.client_app
                    ?.split('/')
                    .filter(Boolean)
                  ?? []

                const clientName =
                  clientParts.length >= 2
                    ? `${clientParts[0]} ${clientParts[1]}`
                    : (
                        device.client_app
                        ?? ''
                      )

                const osLabel = [
                  os,
                  device.os_version,
                ]
                  .filter(Boolean)
                  .join(' ')

                const secondaryInfo = [
                  osLabel,
                  clientName,
                ]
                  .filter(Boolean)
                  .join(' • ')

                const lastSeen =
                  device.last_seen_at
                    ? new Date(
                        device.last_seen_at,
                      ).toLocaleString(
                        'ru-RU',
                        {
                          day: '2-digit',
                          month: '2-digit',
                          hour: '2-digit',
                          minute: '2-digit',
                        },
                      )
                    : null

                return (

                  <div
                    key={device.id}
                    className="device-card"
                  >

                    <div className="device-card-icon">
                      {deviceIcon}
                    </div>

                    <div
                      style={{
                        flex: 1,
                        minWidth: 0,
                      }}
                    >

                      <div className="device-card-name">
                        {deviceName}
                      </div>

                      {secondaryInfo && (
                        <div
                          style={{
                            marginTop: 3,
                            fontSize: 12,
                            opacity: 0.62,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {secondaryInfo}
                        </div>
                      )}

                      {lastSeen && (
                        <div
                          style={{
                            marginTop: 3,
                            fontSize: 11,
                            opacity: 0.42,
                          }}
                        >
                          Активность: {lastSeen}
                        </div>
                      )}

                    </div>

                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() =>
                        handleDeleteDevice(
                          device.id,
                        )
                      }
                      disabled={
                        deletingDeviceId
                        === device.id
                      }
                      style={{
                        marginLeft: 'auto',
                        width: 'auto',
                        padding: '8px 12px',
                        borderRadius: 12,
                        border:
                          '1px solid rgba(255, 80, 80, 0.18)',
                        background:
                          'rgba(255, 80, 80, 0.08)',
                        color: '#ff5c5c',
                        fontSize: 12,
                        fontWeight: 700,
                      }}
                    >
                      {deletingDeviceId
                        === device.id
                          ? 'Удаляем...'
                          : 'Удалить'
                      }
                    </button>

                  </div>

                )
              },
            )}

          </div>

        ) : (

          <div className="device-empty">
            Нет подключённых устройств
          </div>

        )}

      </section>


      {reduceTargetLimit !== null && (

        <div
          onClick={() => {
            if (!deletingDeviceId) {
              setReduceTargetLimit(null)
            }
          }}
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 1000,
            background:
              'rgba(0, 0, 0, 0.45)',
            display: 'flex',
            alignItems: 'flex-end',
          }}
        >

          <div
            onClick={(event) =>
              event.stopPropagation()
            }
            style={{
              width: '100%',
              maxHeight: '78vh',
              overflowY: 'auto',
              padding:
                '22px 18px calc(22px + env(safe-area-inset-bottom))',
              borderRadius:
                '24px 24px 0 0',
              background:
                'var(--background, #111)',
              boxSizing: 'border-box',
            }}
          >

            <div
              style={{
                width: 42,
                height: 4,
                margin: '0 auto 20px',
                borderRadius: 99,
                background:
                  'rgba(127, 127, 127, 0.35)',
              }}
            />


            <div
              style={{
                fontSize: 20,
                fontWeight: 800,
                textAlign: 'center',
              }}
            >
              Уменьшить до {reduceTargetLimit}
              {' '}
              {reduceTargetLimit === 1
                ? 'устройства'
                : 'устройств'
              }?
            </div>


            <div
              style={{
                marginTop: 8,
                marginBottom: 18,
                textAlign: 'center',
                fontSize: 13,
                opacity: 0.65,
                lineHeight: 1.45,
              }}
            >
              {subscriptionDevices.count
                - reduceTargetLimit
                === 1
                  ? 'Нужно удалить 1 устройство'
                  : `Нужно удалить ещё ${
                      subscriptionDevices.count
                      - reduceTargetLimit
                    } устройства`
              }
            </div>


            <div
              style={{
                display: 'grid',
                gap: 10,
              }}
            >

              {subscriptionDevices.devices.map(
                (device) => {

                  const deviceName =
                    device.model
                      ?.replace(
                        /^(\S+)\s+\1\s+/i,
                        '$1 ',
                      )
                    ?? 'Устройство'

                  const os =
                    device.os?.trim()
                    ?? ''

                  const osLower =
                    os.toLowerCase()

                  const modelLower =
                    deviceName.toLowerCase()

                  const deviceIcon =
                    osLower.includes('windows')
                      ? '💻'
                      : (
                          osLower.includes('tv')
                          || modelLower.includes('tv')
                        )
                        ? '📺'
                        : (
                            osLower.includes('android')
                            || osLower.includes('ios')
                            || modelLower.includes('iphone')
                          )
                          ? '📱'
                          : '🖥️'

                  const clientParts =
                    device.client_app
                      ?.split('/')
                      .filter(Boolean)
                    ?? []

                  const clientName =
                    clientParts.length >= 2
                      ? `${clientParts[0]} ${clientParts[1]}`
                      : (
                          device.client_app
                          ?? ''
                        )

                  const osLabel = [
                    os,
                    device.os_version,
                  ]
                    .filter(Boolean)
                    .join(' ')

                  const secondaryInfo = [
                    osLabel,
                    clientName,
                  ]
                    .filter(Boolean)
                    .join(' • ')

                  return (

                    <button
                      key={device.id}
                      type="button"
                      disabled={
                        deletingDeviceId !== null
                      }
                      onClick={() =>
                        handleReduceAndDeleteDevice(
                          device.id,
                        )
                      }
                      style={{
                        width: '100%',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 12,
                        padding: 14,
                        borderRadius: 16,
                        border:
                          '1px solid rgba(127, 127, 127, 0.14)',
                        background:
                          'rgba(127, 127, 127, 0.07)',
                        color: 'inherit',
                        textAlign: 'left',
                      }}
                    >

                      <div
                        style={{
                          width: 42,
                          height: 42,
                          borderRadius: 14,
                          display: 'grid',
                          placeItems: 'center',
                          background:
                            'rgba(127, 127, 127, 0.10)',
                          fontSize: 20,
                          flexShrink: 0,
                        }}
                      >
                        {deviceIcon}
                      </div>


                      <div
                        style={{
                          flex: 1,
                          minWidth: 0,
                        }}
                      >

                        <div
                          style={{
                            fontSize: 14,
                            fontWeight: 700,
                          }}
                        >
                          {deviceName}
                        </div>

                        <div
                          style={{
                            marginTop: 3,
                            fontSize: 12,
                            opacity: 0.55,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {secondaryInfo
                            || 'Нажмите, чтобы удалить'
                          }
                        </div>

                      </div>


                      <div
                        style={{
                          color: '#ff5c5c',
                          fontSize: 13,
                          fontWeight: 700,
                        }}
                      >
                        {deletingDeviceId
                          === device.id
                            ? 'Удаляем...'
                            : 'Удалить'
                        }
                      </div>

                    </button>

                  )
                },
              )}

            </div>


            <button
              type="button"
              disabled={
                deletingDeviceId !== null
              }
              onClick={() =>
                setReduceTargetLimit(null)
              }
              style={{
                marginTop: 14,
                width: '100%',
                minHeight: 52,
                border: 0,
                borderRadius: 16,
                background:
                  'rgba(127, 127, 127, 0.10)',
                color: 'inherit',
                fontSize: 15,
                fontWeight: 700,
                cursor: 'pointer',
                opacity:
                  deletingDeviceId !== null
                    ? 0.45
                    : 1,
              }}
            >
              Отмена
            </button>

          </div>

        </div>

      )}

    </>
  )
}


export default SubscriptionScreen
