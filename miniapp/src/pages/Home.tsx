import {
  useEffect,
  useState,
} from 'react'

import type {
  Subscription,
} from '../api/subscription'

import {
  deleteSubscriptionDevice,
  setSubscriptionDeviceLimit,
} from '../api/subscription'

import type {
  TrialStatus,
} from '../api/trial'

import {
  finishTrial,
} from '../api/trial'

import type {
  WalletResponse,
} from '../api/balance'


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


type SubscriptionDevices = {
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


type Props = {
  daysLeft: number
  subscription: Subscription | null
  usageTotal: number

  subscriptionDevices: SubscriptionDevices

  trial: TrialStatus | null
  wallet: WalletResponse | null

  accountDataLoading: boolean
  accountDataError: string | null

  onStartTrial: () => Promise<void>

  onSubscriptionClick: () => void
  onDevicesClick: () => void
  onBalanceClick: () => void
  onDeviceLimitChanged: (
    deviceLimit: number,
  ) => void

  onDeviceDeleted: (
    hwid: string,
  ) => void
}


function HomeScreen({
  daysLeft,
  subscription,
  usageTotal,
  subscriptionDevices,
  trial,
  wallet,
  accountDataLoading,
  accountDataError,
  onStartTrial,
  onSubscriptionClick,
  onDevicesClick,
  onBalanceClick,
  onDeviceLimitChanged,
  onDeviceDeleted,
}: Props) {

  function formatBytes(
    bytes: number,
  ): string {

    if (bytes <= 0) {
      return '0 Б'
    }

    const units = [
      'Б',
      'КБ',
      'МБ',
      'ГБ',
      'ТБ',
    ]

    const index = Math.min(
      Math.floor(
        Math.log(bytes) /
        Math.log(1024),
      ),
      units.length - 1,
    )

    const value =
      bytes /
      Math.pow(
        1024,
        index,
      )

    return `${value.toFixed(
      index === 0 ? 0 : 2,
    )} ${units[index]}`
  }


  const currentDeviceLimit =
    wallet?.device_limit
    ?? subscriptionDevices.limit
    ?? 1

  const maxDeviceLimit =
    wallet?.max_devices ?? 10

  const [
    selectedDeviceLimit,
    setSelectedDeviceLimit,
  ] = useState(
    currentDeviceLimit,
  )

  const [
    deviceLimitLoading,
    setDeviceLimitLoading,
  ] = useState(false)

  const [
    deviceLimitError,
    setDeviceLimitError,
  ] = useState<string | null>(null)

  const [
    trialUpgradeOpen,
    setTrialUpgradeOpen,
  ] = useState(false)

  const [
    trialUpgradeError,
    setTrialUpgradeError,
  ] = useState<string | null>(null)


  const [
    reduceTargetLimit,
    setReduceTargetLimit,
  ] = useState<number | null>(null)

  const [
    deletingDeviceId,
    setDeletingDeviceId,
  ] = useState<string | null>(null)


  useEffect(() => {

    setSelectedDeviceLimit(
      currentDeviceLimit,
    )

  }, [currentDeviceLimit])


  const previewDailyPrice =
    DAILY_PRICES[
      selectedDeviceLimit
    ] ?? 0


  const decreaseDeviceLimit = () => {

    setSelectedDeviceLimit(
      (value) =>
        Math.max(
          1,
          value - 1,
        ),
    )

    setDeviceLimitError(null)
  }


  const increaseDeviceLimit = () => {

    setSelectedDeviceLimit(
      (value) =>
        Math.min(
          maxDeviceLimit,
          value + 1,
        ),
    )

    setDeviceLimitError(null)
  }


  const continueWithDeviceLimit =
    async () => {

      if (!subscription) {
        onSubscriptionClick()
        return
      }

      /*
       * Во время trial бесплатно доступно
       * 1 устройство.
       *
       * Выбор 2+ означает досрочный переход
       * на платный режим.
       */
      if (
        trial?.active
        && selectedDeviceLimit > 1
      ) {

        setTrialUpgradeError(null)
        setTrialUpgradeOpen(true)

        return
      }

      /*
       * Если уменьшаем лимит ниже количества
       * уже зарегистрированных устройств,
       * открываем тот же popup, что в Подписке.
       */
      if (
        selectedDeviceLimit
        < subscriptionDevices.count
      ) {

        setReduceTargetLimit(
          selectedDeviceLimit,
        )

        setDeviceLimitError(null)

        return
      }

      setDeviceLimitLoading(true)
      setDeviceLimitError(null)

      try {

        if (
          selectedDeviceLimit
          !== currentDeviceLimit
        ) {

          const response =
            await setSubscriptionDeviceLimit(
              subscription.id,
              selectedDeviceLimit,
            )

          setSelectedDeviceLimit(
            response.device_limit,
          )

          onDeviceLimitChanged(
            response.device_limit,
          )

        }

        onSubscriptionClick()

      } catch (error) {

        setDeviceLimitError(
          error instanceof Error
            ? error.message
            : 'Не удалось изменить количество устройств',
        )

      } finally {

        setDeviceLimitLoading(false)

      }

    }


  const confirmTrialUpgrade =
    async () => {

      if (
        !subscription
        || !trial?.active
        || selectedDeviceLimit <= 1
      ) {
        return
      }

      setDeviceLimitLoading(true)
      setTrialUpgradeError(null)

      try {

        const response =
          await finishTrial(
            selectedDeviceLimit,
          )

        if (
          response.status
          === 'insufficient_balance'
        ) {

          setTrialUpgradeError(
            `Для перехода нужно ${
              (
                response.required_kopecks
                / 100
              ).toFixed(2)
            } ₽ на балансе`,
          )

          return
        }

        setSelectedDeviceLimit(
          response.device_limit,
        )

        onDeviceLimitChanged(
          response.device_limit,
        )

        setTrialUpgradeOpen(false)

        onSubscriptionClick()

      } catch (error) {

        setTrialUpgradeError(
          error instanceof Error
            ? error.message
            : 'Не удалось перейти на платный режим',
        )

      } finally {

        setDeviceLimitLoading(false)

      }

    }


  const handleReduceAndDeleteDevice =
    async (
      hwid: string,
    ) => {

      if (
        !subscription
        || reduceTargetLimit === null
      ) {
        return
      }

      const targetLimit =
        reduceTargetLimit

      /*
       * count здесь ещё содержит устройство,
       * которое сейчас удаляем.
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

        await deleteSubscriptionDevice(
          subscription.id,
          hwid,
        )

        /*
         * Сразу обновляем список в App.
         */
        onDeviceDeleted(
          hwid,
        )

        /*
         * Если лишние устройства ещё остались,
         * popup остаётся открытым.
         */
        if (
          remainingCount
          > targetLimit
        ) {
          return
        }

        /*
         * Лишние устройства удалены.
         * Теперь безопасно уменьшаем лимит.
         */
        const response =
          await setSubscriptionDeviceLimit(
            subscription.id,
            targetLimit,
          )

        setSelectedDeviceLimit(
          response.device_limit,
        )

        onDeviceLimitChanged(
          response.device_limit,
        )

        setReduceTargetLimit(null)

        /*
         * После успешного выбора продолжаем
         * к подключению.
         */
        onSubscriptionClick()

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


  const vpnActive =
    subscription?.status === 'active'


  const [
    now,
    setNow,
  ] = useState(
    Date.now(),
  )


  useEffect(() => {

    const timer =
      window.setInterval(
        () => {
          setNow(
            Date.now(),
          )
        },
        1000,
      )

    return () => {
      window.clearInterval(
        timer,
      )
    }

  }, [])


  const trialEndsAtValue =
    trial?.active && trial.ends_at
      ? (
          trial.ends_at.endsWith('Z')
          || /[+-]\d{2}:\d{2}$/.test(
            trial.ends_at,
          )
        )
        ? trial.ends_at
        : `${trial.ends_at}Z`
      : null


  const trialEndsAtMs =
    trialEndsAtValue
      ? new Date(
          trialEndsAtValue,
        ).getTime()
      : 0


  const trialRemainingSeconds =
    trial?.active && trialEndsAtMs > 0
      ? Math.max(
          0,
          Math.floor(
            (
              trialEndsAtMs
              - now
            ) / 1000,
          ),
        )
      : 0


  const trialDays =
    Math.floor(
      trialRemainingSeconds /
      86400,
    )


  const trialHours =
    Math.floor(
      (
        trialRemainingSeconds %
        86400
      ) /
      3600,
    )


  const trialMinutes =
    Math.floor(
      (
        trialRemainingSeconds %
        3600
      ) /
      60,
    )


  const trialSeconds =
    trialRemainingSeconds % 60


  const trialTime =
    [
      trialHours,
      trialMinutes,
      trialSeconds,
    ]
      .map(
        (value) =>
          String(
            value,
          ).padStart(
            2,
            '0',
          ),
      )
      .join(':')


  const dailyPrice =
    wallet?.daily_price_rubles ?? 4


  const daysAvailable =
    wallet?.days_available ?? 0


  const paidUntilValue =
    subscription?.expires_at
      ? (
          subscription.expires_at.endsWith('Z')
          || /[+-]\d{2}:\d{2}$/.test(
            subscription.expires_at,
          )
        )
        ? subscription.expires_at
        : `${subscription.expires_at}Z`
      : null


  const paidUntilMs =
    paidUntilValue
      ? new Date(
          paidUntilValue,
        ).getTime()
      : 0


  const currentPeriodSeconds =
    paidUntilMs > 0
      ? Math.max(
          0,
          Math.floor(
            (
              paidUntilMs
              - now
            ) / 1000,
          ),
        )
      : Math.max(
          0,
          daysLeft * 86400,
        )


  const totalAccessSeconds =
    currentPeriodSeconds
    + (
      daysAvailable
      * 86400
    )


  const accessDays =
    Math.floor(
      totalAccessSeconds /
      86400,
    )


  const accessHours =
    Math.floor(
      (
        totalAccessSeconds %
        86400
      ) /
      3600,
    )


  const accessMinutes =
    Math.floor(
      (
        totalAccessSeconds %
        3600
      ) /
      60,
    )


  const accessSeconds =
    totalAccessSeconds % 60


  const accessTime =
    [
      accessHours,
      accessMinutes,
      accessSeconds,
    ]
      .map(
        (value) =>
          String(
            value,
          ).padStart(
            2,
            '0',
          ),
      )
      .join(':')


  return (
    <>

      <section
        className="vpn-card"
        style={{
          padding: '24px 20px',
          minHeight: 96,
          display: 'flex',
          alignItems: 'center',
        }}
      >

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'auto 1fr auto',
            alignItems: 'center',
            gap: 20,
            width: '100%',
          }}
        >

          <div
            style={{
              display: 'flex',
              alignItems: 'baseline',
              gap: 5,
              whiteSpace: 'nowrap',
            }}
          >

            <strong
              style={{
                fontSize: 28,
                lineHeight: 1,
                fontWeight: 850,
              }}
            >
              {trial?.active
                ? trialDays
                : vpnActive
                  ? accessDays
                  : '0'
              }
            </strong>

            <span
              style={{
                fontSize: 11,
                fontWeight: 700,
                opacity: 0.55,
              }}
            >
              ДН.
            </span>

          </div>


          <div
            style={{
              textAlign: 'center',
              minWidth: 0,
            }}
          >

            <div
              style={{
                fontSize: 14,
                fontWeight: 750,
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
            >
              {trial?.active
                ? 'Пробный период'
                : vpnActive
                  ? 'Подписка активна'
                  : 'Подписка не активна'
              }
            </div>

          </div>


          <div
            style={{
              textAlign: 'right',
              whiteSpace: 'nowrap',
              fontSize: 16,
              fontWeight: 800,
              fontVariantNumeric: 'tabular-nums',
            }}
          >
            {trial?.active
              ? trialTime
              : vpnActive
                ? accessTime
                : '00:00:00'
            }
          </div>

        </div>

      </section>


      {trial?.available && (

        <section className="section">

          <div className="section-title">
            Попробуйте бесплатно
          </div>


          <div className="balance-card">

            <div className="balance-icon">
              🎁
            </div>


            <div className="balance-info">

              <strong>
                3 дня бесплатно
              </strong>

              <span>
                Без списаний. Затем {dailyPrice} ₽ / 24 часа
              </span>

            </div>

          </div>


          <button
            className="primary-button"
            disabled={accountDataLoading}
            onClick={() => {
              void onStartTrial()
            }}
          >

            {accountDataLoading
              ? 'Подключаем...'
              : 'Попробовать бесплатно'
            }

            <span>
              →
            </span>

          </button>

        </section>

      )}


      {subscription && (

        <section className="section">

          <div className="section-title">
            Как начать?
          </div>

          <div
            className="usage-card"
            style={{
              padding: 18,
            }}
          >

            <div
              style={{
                fontSize: 15,
                fontWeight: 700,
                textAlign: 'center',
              }}
            >
              Для начала выберите количество
              необходимых устройств
            </div>

            <div
              style={{
                marginTop: 18,
                display: 'flex',
                justifyContent: 'center',
              }}
            >

              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  padding: 6,
                  borderRadius: 20,
                  background:
                    'rgba(127, 127, 127, 0.08)',
                  border:
                    '1px solid rgba(127, 127, 127, 0.12)',
                }}
              >

                <button
                  type="button"
                  onClick={decreaseDeviceLimit}
                  disabled={
                    selectedDeviceLimit <= 1
                    || deviceLimitLoading
                  }
                  style={{
                    width: 44,
                    height: 44,
                    border: 0,
                    borderRadius: 15,
                    background:
                      'rgba(127, 127, 127, 0.10)',
                    color: 'inherit',
                    fontSize: 25,
                    cursor: 'pointer',
                    opacity:
                      selectedDeviceLimit <= 1
                        ? 0.35
                        : 1,
                  }}
                >
                  −
                </button>

                <div
                  style={{
                    minWidth: 84,
                    textAlign: 'center',
                  }}
                >

                  <div
                    style={{
                      fontSize: 30,
                      fontWeight: 850,
                      lineHeight: 1,
                    }}
                  >
                    {selectedDeviceLimit}
                  </div>

                  <div
                    style={{
                      marginTop: 4,
                      fontSize: 11,
                      opacity: 0.55,
                    }}
                  >
                    {selectedDeviceLimit === 1
                      ? 'устройство'
                      : selectedDeviceLimit < 5
                        ? 'устройства'
                        : 'устройств'
                    }
                  </div>

                </div>

                <button
                  type="button"
                  onClick={increaseDeviceLimit}
                  disabled={
                    selectedDeviceLimit
                    >= maxDeviceLimit
                    || deviceLimitLoading
                  }
                  style={{
                    width: 44,
                    height: 44,
                    border: 0,
                    borderRadius: 15,
                    background:
                      'rgba(127, 127, 127, 0.10)',
                    color: 'inherit',
                    fontSize: 25,
                    cursor: 'pointer',
                    opacity:
                      selectedDeviceLimit
                      >= maxDeviceLimit
                        ? 0.35
                        : 1,
                  }}
                >
                  +
                </button>

              </div>

            </div>


            <div
              style={{
                marginTop: 15,
                textAlign: 'center',
              }}
            >

              <strong
                style={{
                  fontSize: 18,
                }}
              >
                {trial?.active
                  && selectedDeviceLimit === 1
                  ? 'Бесплатно'
                  : `${previewDailyPrice} ₽ / 24 часа`
                }
              </strong>

              {trial?.active && (

                <div
                  style={{
                    marginTop: 5,
                    fontSize: 11,
                    color:
                      'var(--text-secondary)',
                  }}
                >
                  {selectedDeviceLimit === 1
                    ? '1 устройство на весь пробный период'
                    : 'Переход на платный режим'
                  }
                </div>

              )}

            </div>


            {deviceLimitError && (

              <div
                style={{
                  marginTop: 12,
                  textAlign: 'center',
                  fontSize: 12,
                }}
              >
                {deviceLimitError}

                {selectedDeviceLimit
                  < subscriptionDevices.count && (

                  <button
                    type="button"
                    onClick={onDevicesClick}
                    style={{
                      display: 'block',
                      margin: '10px auto 0',
                      border: 0,
                      background: 'transparent',
                      color: 'inherit',
                      fontWeight: 700,
                      textDecoration: 'underline',
                      cursor: 'pointer',
                    }}
                  >
                    Управлять устройствами
                  </button>

                )}

              </div>

            )}


            <button
              type="button"
              className="primary-button"
              disabled={deviceLimitLoading}
              onClick={() => {
                void continueWithDeviceLimit()
              }}
              style={{
                width: '100%',
                marginTop: 18,
              }}
            >

              {deviceLimitLoading
                ? 'Сохраняем...'
                : 'Продолжить'
              }

              <span>
                →
              </span>

            </button>

          </div>

        </section>

      )}


      <section className="section">

        <div className="section-title">
          Использование
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: 10,
          }}
        >

          <div
            style={{
              padding: '16px 12px',
              borderRadius: 18,
              background:
                'rgba(127, 127, 127, 0.07)',
              border:
                '1px solid rgba(127, 127, 127, 0.10)',
              textAlign: 'center',
              minWidth: 0,
            }}
          >

            <div
              style={{
                height: 34,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 28,
                fontWeight: 800,
                lineHeight: 1,
                color:
                  'var(--text-secondary)',
              }}
            >
              ∞
            </div>

            <div
              style={{
                marginTop: 10,
                fontSize: 18,
                fontWeight: 800,
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
            >
              {formatBytes(
                usageTotal,
              )}
            </div>

            <div
              style={{
                marginTop: 5,
                fontSize: 12,
                fontWeight: 700,
                opacity: 0.58,
              }}
            >
              Трафик
            </div>

          </div>


          <div
            role="button"
            tabIndex={0}
            onClick={onDevicesClick}
            onKeyDown={(event) => {

              if (
                event.key === 'Enter'
                || event.key === ' '
              ) {

                event.preventDefault()
                onDevicesClick()

              }

            }}
            style={{
              padding: '16px 12px',
              borderRadius: 18,
              background:
                'rgba(127, 127, 127, 0.07)',
              border:
                '1px solid rgba(127, 127, 127, 0.10)',
              textAlign: 'center',
              cursor: 'pointer',
              minWidth: 0,
            }}
          >

            <div
              style={{
                height: 34,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 25,
                lineHeight: 1,
              }}
            >
              📱
            </div>

            <div
              style={{
                marginTop: 10,
                fontSize: 18,
                fontWeight: 800,
                whiteSpace: 'nowrap',
              }}
            >
              {subscriptionDevices.count}
              {' / '}
              {subscriptionDevices.limit}
            </div>

            <div
              style={{
                marginTop: 5,
                fontSize: 12,
                fontWeight: 700,
                opacity: 0.58,
              }}
            >
              Устройства
            </div>

          </div>

        </div>

      </section>


      {!subscription &&
        !trial?.available && (

          <button
            className="primary-button"
            onClick={
              onBalanceClick
            }
          >

            Пополнить баланс

            <span>
              →
            </span>

          </button>

        )}


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
                      onClick={() => {
                        void handleReduceAndDeleteDevice(
                          device.id,
                        )
                      }}
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
                        cursor: 'pointer',
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
                            fontWeight: 750,
                          }}
                        >
                          {deviceName}
                        </div>

                        {secondaryInfo && (

                          <div
                            style={{
                              marginTop: 3,
                              fontSize: 12,
                              opacity: 0.6,
                              overflow: 'hidden',
                              whiteSpace: 'nowrap',
                              textOverflow: 'ellipsis',
                            }}
                          >
                            {secondaryInfo}
                          </div>

                        )}

                      </div>


                      <div
                        style={{
                          fontSize: 12,
                          fontWeight: 700,
                          opacity:
                            deletingDeviceId === device.id
                              ? 0.45
                              : 0.8,
                        }}
                      >
                        {deletingDeviceId === device.id
                          ? 'Удаляем...'
                          : 'Удалить'
                        }
                      </div>

                    </button>

                  )

                },
              )}

            </div>


            {deviceLimitError && (

              <div
                style={{
                  marginTop: 14,
                  textAlign: 'center',
                  fontSize: 12,
                }}
              >
                {deviceLimitError}
              </div>

            )}


            <button
              type="button"
              disabled={
                deletingDeviceId !== null
              }
              onClick={() =>
                setReduceTargetLimit(null)
              }
              style={{
                width: '100%',
                marginTop: 16,
                padding: '12px 14px',
                borderRadius: 14,
                border:
                  '1px solid rgba(127, 127, 127, 0.14)',
                background:
                  'rgba(127, 127, 127, 0.07)',
                color: 'inherit',
                fontSize: 14,
                fontWeight: 700,
              }}
            >
              Отмена
            </button>

          </div>

        </div>

      )}


      {trialUpgradeOpen && (

        <div
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 1000,
            display: 'flex',
            alignItems: 'flex-end',
            justifyContent: 'center',
            padding: 16,
            background:
              'rgba(0, 0, 0, 0.46)',
          }}
          onClick={() => {

            if (!deviceLimitLoading) {
              setTrialUpgradeOpen(false)
            }

          }}
        >

          <div
            onClick={(event) =>
              event.stopPropagation()
            }
            style={{
              width: '100%',
              maxWidth: 480,
              padding: 20,
              borderRadius: 24,
              background:
                'var(--card)',
              color:
                'var(--text)',
              boxShadow:
                '0 18px 60px rgba(0,0,0,0.24)',
            }}
          >

            <div
              style={{
                fontSize: 19,
                fontWeight: 850,
                textAlign: 'center',
              }}
            >
              Перейти на {
                selectedDeviceLimit
              } устройств?
            </div>


            <div
              style={{
                marginTop: 10,
                fontSize: 14,
                lineHeight: 1.5,
                textAlign: 'center',
                opacity: 0.72,
              }}
            >
              Пробный период завершится,
              и начнётся платный режим.
            </div>


            <div
              style={{
                marginTop: 18,
                padding: 16,
                borderRadius: 18,
                background:
                  'var(--accent-soft)',
                textAlign: 'center',
              }}
            >

              <div
                style={{
                  fontSize: 12,
                  color:
                    'var(--text-secondary)',
                }}
              >
                Стоимость
              </div>

              <div
                style={{
                  marginTop: 4,
                  fontSize: 24,
                  fontWeight: 850,
                }}
              >
                {previewDailyPrice} ₽
              </div>

              <div
                style={{
                  marginTop: 2,
                  fontSize: 12,
                  color:
                    'var(--text-secondary)',
                }}
              >
                за 24 часа
              </div>

            </div>


            {(wallet?.balance_kopecks ?? 0)
              < previewDailyPrice * 100 && (

              <div
                style={{
                  marginTop: 14,
                  fontSize: 13,
                  textAlign: 'center',
                  lineHeight: 1.45,
                }}
              >
                На балансе недостаточно средств.
                Пополните баланс, чтобы перейти
                на {
                  selectedDeviceLimit
                } устройств.
              </div>

            )}


            {trialUpgradeError && (

              <div
                style={{
                  marginTop: 12,
                  fontSize: 12,
                  textAlign: 'center',
                }}
              >
                {trialUpgradeError}
              </div>

            )}


            {(wallet?.balance_kopecks ?? 0)
              >= previewDailyPrice * 100 ? (

              <button
                type="button"
                className="primary-button"
                disabled={deviceLimitLoading}
                onClick={() => {
                  void confirmTrialUpgrade()
                }}
                style={{
                  width: '100%',
                  marginTop: 18,
                }}
              >
                {deviceLimitLoading
                  ? 'Переходим...'
                  : 'Перейти на платный режим'
                }
              </button>

            ) : (

              <button
                type="button"
                className="primary-button"
                onClick={() => {

                  setTrialUpgradeOpen(false)
                  onBalanceClick()

                }}
                style={{
                  width: '100%',
                  marginTop: 18,
                }}
              >
                Пополнить баланс
              </button>

            )}


            <button
              type="button"
              disabled={deviceLimitLoading}
              onClick={() =>
                setTrialUpgradeOpen(false)
              }
              style={{
                width: '100%',
                marginTop: 10,
                padding: '13px 16px',
                borderRadius: 16,
                border:
                  '1px solid rgba(127,127,127,0.14)',
                background:
                  'rgba(127,127,127,0.07)',
                color: 'inherit',
                fontSize: 14,
                fontWeight: 700,
              }}
            >
              Остаться на пробном периоде
            </button>

          </div>

        </div>

      )}


      {accountDataError && (

        <div
          style={{
            marginTop: 16,
            padding: '12px 14px',
            borderRadius: 12,
            fontSize: 13,
            textAlign: 'center',
          }}
        >
          {accountDataError}
        </div>

      )}

    </>
  )
}



export default HomeScreen
