import { useEffect, useState } from 'react'
import './App.css'

import Settings from './pages/Settings'

import logoDark from './assets/justfastvpn-logo-dark.png'
import logoLight from './assets/justfastvpn-logo-white.png'

import happIcon from './assets/happ.png'
import incyIcon from './assets/incy.png'

import { useTheme } from './theme/ThemeContext'

import {
  initTelegramWebApp,
  getTelegramStartParam,
} from './api/telegram'

import { useAuth } from './context/AuthContext'

import {
  getSubscriptions,
  getSubscriptionLink,
  getSubscriptionUsage,
  type Subscription,
} from './api/subscription'

import {
  createPurchase,
} from './api/purchase'


type Tab =
  | 'home'
  | 'subscription'
  | 'balance'
  | 'referrals'
  | 'support'


function App() {

  useEffect(() => {
    initTelegramWebApp()
  }, [])

  const [
    renewOpen,
    setRenewOpen,
  ] = useState(false)

  const {
    user,
    loading,
    error,
  } = useAuth()

  const [
    subscriptions,
    setSubscriptions,
  ] = useState<Subscription[]>([])

  const [
    subscriptionsLoading,
    setSubscriptionsLoading,
  ] = useState(true)

  const [
    subscriptionsError,
    setSubscriptionsError,
  ] = useState<string | null>(null)

  const [
    activeTab,
    setActiveTab,
  ] = useState<Tab>(() => {

    const params =
      new URLSearchParams(
        window.location.search,
      )

    const tab =
      params.get('tab')

    if (
      tab === 'subscription' ||
      tab === 'balance' ||
      tab === 'referrals' ||
      tab === 'support' ||
      tab === 'home'
    ) {
      return tab
    }

    return 'home'
  })

  const [
    settingsOpen,
    setSettingsOpen,
  ] = useState(false)

  const [
    notificationsOpen,
    setNotificationsOpen,
  ] = useState(false)

  const {
    mode,
    setMode,
  } = useTheme()



  const activeSubscription =
    subscriptions.find(
      (subscription) =>
        subscription.status === 'active',
    ) ?? null

  const [
    subscriptionUsage,
    setSubscriptionUsage,
  ] = useState({
    up: 0,
    down: 0,
    total: 0,
  })


  useEffect(() => {

    async function loadUsage() {

      if (!activeSubscription) {

        setSubscriptionUsage({
          up: 0,
          down: 0,
          total: 0,
        })

        return
      }

      try {

        const usage =
          await getSubscriptionUsage(
            activeSubscription.id,
          )

        console.log(
          'Subscription usage:',
          usage,
        )

        setSubscriptionUsage(
          usage
        )

      } catch (error) {

        console.error(
          'Failed to load subscription usage:',
          error,
        )

      }
    }

    loadUsage()

  }, [activeSubscription])

  useEffect(() => {

    async function loadSubscriptions() {

      try {

        setSubscriptionsLoading(true)
        setSubscriptionsError(null)

        const data =
          await getSubscriptions()

        console.log(
          'Subscriptions from API:',
          data,
        )

        setSubscriptions(data)

      } catch (error) {

        console.error(
          'Failed to load subscriptions:',
          error,
        )

        setSubscriptionsError(
          error instanceof Error
            ? error.message
            : 'Failed to load subscriptions',
        )

      } finally {

        setSubscriptionsLoading(false)

      }
    }


    if (user) {
      loadSubscriptions()
    }

  }, [user])


  useEffect(() => {

    const startParam =
      getTelegramStartParam()

    const params =
      new URLSearchParams(
        window.location.search,
      )

    const paymentSuccess =
      startParam === 'payment_success' ||
      params.get('payment') === 'success'

    if (!paymentSuccess) {
      return
    }

    setActiveTab('subscription')
    setRenewOpen(false)

  }, [])

  const daysLeft =
    activeSubscription
      ? Math.max(
        0,
        Math.ceil(
          (
            new Date(
              activeSubscription.expires_at,
            ).getTime() -
            Date.now()
          ) /
          (
            1000 *
            60 *
            60 *
            24
          ),
        ),
      )
      : 0


  if (loading) {

    return (
      <div className="app">

        <div
          style={{
            padding: 24,
          }}
        >
          Загрузка...
        </div>

      </div>
    )
  }


  if (error || !user) {

    return (
      <div className="app">

        <div
          style={{
            padding: 24,
          }}
        >
          Не удалось загрузить данные пользователя.
        </div>

      </div>
    )
  }


  if (subscriptionsLoading) {

    return (
      <div className="app">

        <div
          style={{
            padding: 24,
          }}
        >
          Загрузка подписки...
        </div>

      </div>
    )
  }


  if (subscriptionsError) {

    return (
      <div className="app">

        <div
          style={{
            padding: 24,
          }}
        >
          Не удалось загрузить подписку.

          <br />

          {subscriptionsError}
        </div>

      </div>
    )
  }


  return (

    <div className="app">

      <header className="top-header">

        <div className="brand-area">

          <picture className="brand-logo-picture">

            <img
              src={logoLight}
              alt="JustFastVPN"
              className="brand-logo brand-logo-light"
            />

            <img
              src={logoDark}
              alt="JustFastVPN"
              className="brand-logo brand-logo-dark"
            />

          </picture>

          <div className="brand-status">
            Защита вашего подключения
          </div>

        </div>


        <div className="header-actions">

          <button
            className="notification-button"
            onClick={() =>
              setNotificationsOpen(true)
            }
            aria-label="Уведомления"
          >

            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
            >

              <path
                d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"
              />

              <path
                d="M10 21h4"
              />

            </svg>

            <span className="notification-dot" />

          </button>


          <button
            className="theme-button"
            onClick={() =>
              setMode(
                mode === 'light'
                  ? 'dark'
                  : 'light',
              )
            }
            aria-label={
              mode === 'light'
                ? 'Включить тёмную тему'
                : 'Включить светлую тему'
            }
          >

            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
            >

              {mode === 'light' ? (
                <>
                  <path
                    d="M21 12.8A8.5 8.5 0 1 1 11.2 3a6.7 6.7 0 0 0 9.8 9.8Z"
                  />
                </>
              ) : (
                <>
                  <circle
                    cx="12"
                    cy="12"
                    r="4"
                  />

                  <path d="M12 2v2" />
                  <path d="M12 20v2" />

                  <path
                    d="M4.93 4.93l1.42 1.42"
                  />

                  <path
                    d="M17.65 17.65l1.42 1.42"
                  />

                  <path d="M2 12h2" />
                  <path d="M20 12h2" />

                  <path
                    d="M4.93 19.07l1.42-1.42"
                  />

                  <path
                    d="M17.65 6.35l1.42-1.42"
                  />
                </>
              )}

            </svg>

          </button>


          <button
            className="color-button"
            onClick={() =>
              setSettingsOpen(true)
            }
            aria-label="Цвет интерфейса"
          >

            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
            >

              <path
                d="M12 3a9 9 0 1 0 0 18h1.5a2 2 0 0 0 0-4H12a2 2 0 0 1 0-4h2a2 2 0 0 0 0-4h-2a2 2 0 0 1 0-6Z"
              />

              <circle
                cx="7.5"
                cy="10"
                r="0.8"
              />

              <circle
                cx="9"
                cy="6.8"
                r="0.8"
              />

              <circle
                cx="14"
                cy="6.5"
                r="0.8"
              />

              <circle
                cx="17"
                cy="10"
                r="0.8"
              />

            </svg>

          </button>

        </div>

      </header>


      <main className="main">

        {notificationsOpen ? (

          <NotificationsScreen
            onClose={() =>
              setNotificationsOpen(false)
            }
          />

        ) : settingsOpen ? (

          <Settings
            onClose={() =>
              setSettingsOpen(false)
            }
          />

        ) : (

          <>

            {activeTab === 'home' && (

              <HomeScreen
                daysLeft={daysLeft}
                subscription={activeSubscription}
                usageTotal={subscriptionUsage.total}
                onSubscriptionClick={() => {
                  setActiveTab('subscription')
                  setRenewOpen(true)
                }}
              />
            )}

            {activeTab === 'subscription' && (

              <SubscriptionScreen
                subscription={activeSubscription}
                renewOpen={renewOpen}
                setRenewOpen={setRenewOpen}
              />

            )}


            {activeTab === 'balance' && (
              <BalanceScreen />
            )}


            {activeTab === 'referrals' && (
              <ReferralsScreen />
            )}


            {activeTab === 'support' && (
              <SupportScreen />
            )}

          </>

        )}

      </main>


      {!settingsOpen && (

        <BottomNavigation
          activeTab={activeTab}
          onChange={setActiveTab}
        />

      )}

    </div>
  )
}



function HomeScreen({
  daysLeft,
  subscription,
  usageTotal,
  onSubscriptionClick,
}: {
  daysLeft: number
  subscription: Subscription | null
  usageTotal: number
  onSubscriptionClick: () => void
}) {

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

  return (

    <>

      <section className="welcome">

        <div className="welcome-small">
          Добро пожаловать 👋
        </div>

        <h1>
          Justmoresmile
        </h1>

      </section>


      <section className="vpn-card">

        <div className="vpn-card-top">

          <div className="vpn-card-status">

            <div className="active-status">

              <span />

              {subscription
                ? 'Подписка активна'
                : 'Нет активной подписки'
              }

            </div>

          </div>

        </div>


        <div className="days-counter">

          <strong>
            {daysLeft}
          </strong>

          <span>
            ДНЕЙ
          </span>

        </div>


        <div className="days-label">
          осталось до окончания
        </div>


        <div className="progress">

          <div
            className="progress-value"
            style={{
              width: subscription
                ? '72%'
                : '0%',
            }}
          />

        </div>


        <div className="expire-date">

          {subscription
            ? `до ${new Date(
              subscription.expires_at,
            ).toLocaleDateString(
              'ru-RU',
              {
                day: 'numeric',
                month: 'long',
                year: 'numeric',
              },
            )}`
            : 'Оформите подписку для подключения'
          }

        </div>

      </section>


      <section className="section">

        <div className="section-title">
          Ваша подписка
        </div>


        <div className="stats-grid">

          <InfoCard
            icon="∞"
            title={formatBytes(usageTotal)}
            label="Использовано"
          />

          <InfoCard
            icon="📱"
            title="0 / 2"
            label="Устройства"
          />

        </div>

      </section>


      <button
        className="primary-button"
        onClick={onSubscriptionClick}
      >
        {subscription
          ? 'Продлить подписку'
          : 'Купить VPN'
        }

        <span>→</span>
      </button>


      <section className="section">

        <div className="section-title">
          Использование
        </div>


        <div className="usage-card">

          <div className="usage-row">

            <span className="usage-icon">
              {subscription?.server_country === 'Finland'
                ? '🇫🇮'
                : '🌍'
              }
            </span>

            <div>
              <strong>
                {subscription?.server_name ?? 'Не выбран'}
              </strong>

              <small>
                {subscription?.server_country ?? 'Текущий сервер'}
              </small>
            </div>
          </div>


          <div className="divider" />


          <div className="usage-row">

            <div>

              <span className="usage-icon">
                🕐
              </span>

              <div>

                <strong>
                  Последняя активность
                </strong>

                <small>
                  Последнее подключение
                </small>

              </div>

            </div>

            <b>
              Сегодня, 14:32
            </b>

          </div>

        </div>

      </section>


      <section className="section">

        <div className="section-title">
          Баланс
        </div>


        <div className="balance-card">

          <div className="balance-icon">
            💳
          </div>


          <div className="balance-info">

            <strong>
              0.00 ₽
            </strong>

            <span>
              Доступный баланс
            </span>

          </div>


          <div className="arrow">
            →
          </div>

        </div>

      </section>

    </>
  )
}



function InfoCard({
  icon,
  title,
  label,
}: {
  icon: string
  title: string
  label: string
}) {

  return (

    <div className="info-card">

      <div className="info-icon">
        {icon}
      </div>

      <strong>
        {title}
      </strong>

      <span>
        {label}
      </span>

    </div>
  )
}



function SubscriptionScreen({
  subscription,
  renewOpen,
  setRenewOpen,
}: {
  subscription: Subscription | null
  renewOpen: boolean
  setRenewOpen: React.Dispatch<
    React.SetStateAction<boolean>
  >
}) {

  const [
    selectedDays,
    setSelectedDays,
  ] = useState(30)

  const [
    purchaseLoading,
    setPurchaseLoading,
  ] = useState(false)

  const [
    purchaseError,
    setPurchaseError,
  ] = useState<string | null>(null)

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


  const selectedPrice =
    selectedDays === 30
      ? 100
      : selectedDays === 90
        ? 300
        : selectedDays === 180
          ? 570
          : 1000


  const subscriptionLinkDisplay =
    subscriptionLink
      ? subscriptionLink.length > 38
        ? `${subscriptionLink.slice(0, 35)}...`
        : subscriptionLink
      : null


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


  async function handlePurchase() {

    try {

      setPurchaseLoading(true)
      setPurchaseError(null)


      const payment =
        await createPurchase(
          selectedDays,
          null,
        )


      if (!payment.confirmation_url) {

        throw new Error(
          'Ссылка на оплату не получена',
        )

      }


      window.location.href =
        payment.confirmation_url

    } catch (error) {

      setPurchaseError(
        error instanceof Error
          ? error.message
          : 'Не удалось создать оплату',
      )

    } finally {

      setPurchaseLoading(false)

    }
  }


  if (!subscription) {



    return (

      <>

        <PageTitle
          title="Подписка"
          subtitle="Управление вашей подпиской"
        />


        <div className="subscription-timer-card">

          <div className="subscription-timer-header">

            <div>

              <small>
                Подписка не активна
              </small>

              <strong>
                Подключите JustFastVPN
              </strong>

            </div>


            <div className="subscription-timer-icon">
              ⏱
            </div>

          </div>


          <div className="empty-card">

            <div className="empty-icon">
              🔐
            </div>

            <strong>
              У вас нет активной подписки
            </strong>

            <span>
              Оформите подписку, чтобы получить
              доступ к VPN и ссылку для подключения.
            </span>

          </div>

        </div>


        <section className="section">

          <div className="section-title">
            Выберите тариф
          </div>

          <div className="tariff-grid">

            <button
              className={
                selectedDays === 30
                  ? 'tariff-card active'
                  : 'tariff-card'
              }
              onClick={() => setSelectedDays(30)}
            >

              <div className="tariff-top">

                <div>
                  <div className="tariff-period">
                    1 месяц
                  </div>

                  <div className="tariff-device">
                    2 устройства
                  </div>
                </div>

              </div>

              <div className="tariff-price">
                100 ₽
              </div>

              <div className="tariff-monthly">
                100 ₽ / месяц
              </div>

              <div className="tariff-check">
                {selectedDays === 30 ? '✓' : ''}
              </div>

            </button>


            <button
              className={
                selectedDays === 90
                  ? 'tariff-card active'
                  : 'tariff-card'
              }
              onClick={() => setSelectedDays(90)}
            >

              <div className="tariff-top">

                <div>
                  <div className="tariff-period">
                    3 месяца
                  </div>

                  <div className="tariff-device">
                    2 устройства
                  </div>
                </div>

              </div>

              <div className="tariff-price">
                300 ₽
              </div>

              <div className="tariff-monthly">
                100 ₽ / месяц
              </div>

              <div className="tariff-check">
                {selectedDays === 90 ? '✓' : ''}
              </div>

            </button>


            <button
              className={
                selectedDays === 180
                  ? 'tariff-card active'
                  : 'tariff-card'
              }
              onClick={() => setSelectedDays(180)}
            >

              <div className="tariff-top">

                <div>
                  <div className="tariff-period">
                    6 месяцев
                  </div>

                  <div className="tariff-device">
                    2 устройства
                  </div>
                </div>

                <div className="tariff-badge">
                  −5%
                </div>

              </div>

              <div className="tariff-price">
                570 ₽
              </div>

              <div className="tariff-monthly">
                95 ₽ / месяц
              </div>

              <div className="tariff-check">
                {selectedDays === 180 ? '✓' : ''}
              </div>

            </button>


            <button
              className={
                selectedDays === 365
                  ? 'tariff-card active'
                  : 'tariff-card'
              }
              onClick={() => setSelectedDays(365)}
            >

              <div className="tariff-top">

                <div>
                  <div className="tariff-period">
                    12 месяцев
                  </div>

                  <div className="tariff-device">
                    2 устройства
                  </div>
                </div>

                <div className="tariff-badge tariff-badge-best">
                  Выгодно
                </div>

              </div>

              <div className="tariff-price">
                1000 ₽
              </div>

              <div className="tariff-monthly">
                ≈ 83 ₽ / месяц
              </div>

              <div className="tariff-check">
                {selectedDays === 365 ? '✓' : ''}
              </div>

            </button>

          </div>

        </section>


        <button
          className="primary-button tariff-buy-button"
          onClick={handlePurchase}
          disabled={purchaseLoading}
        >
          {purchaseLoading
            ? 'Создаём оплату...'
            : `Оплатить ${selectedPrice} ₽`
          }

          <span>→</span>
        </button>


        {purchaseError && (

          <div
            style={{
              marginTop: 12,
              textAlign: 'center',
            }}
          >
            {purchaseError}
          </div>

        )}


        <section className="section">

          <div className="section-title">
            Что входит в подписку
          </div>


          <div className="apps-card">

            <div className="app-item">

              <div className="app-icon">
                ⚡
              </div>


              <div className="app-info">

                <strong>
                  Быстрое подключение
                </strong>

                <span>
                  VLESS с автоматической настройкой
                </span>

              </div>

            </div>


            <div className="divider" />


            <div className="app-item">

              <div className="app-icon">
                🔗
              </div>


              <div className="app-info">

                <strong>
                  Персональная ссылка
                </strong>

                <span>
                  Для Happ, Incy и других клиентов
                </span>

              </div>

            </div>

          </div>

        </section>

      </>
    )
  }


  const remainingMs =
    Math.max(
      0,
      new Date(
        subscription.expires_at,
      ).getTime() -
      Date.now(),
    )


  const remainingDays =
    Math.floor(
      remainingMs /
      (
        1000 *
        60 *
        60 *
        24
      ),
    )


  const remainingHours =
    Math.floor(
      (
        remainingMs /
        (
          1000 *
          60 *
          60
        )
      ) % 24,
    )


  const remainingMinutes =
    Math.floor(
      (
        remainingMs /
        (
          1000 *
          60
        )
      ) % 60,
    )


  const expiresAt =
    new Date(
      subscription.expires_at,
    ).toLocaleDateString(
      'ru-RU',
      {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
      },
    )


  return (

    <>

      <PageTitle
        title="Подписка"
        subtitle="Управление вашей подпиской"
      />


      <div className="subscription-timer-card">

        <div className="subscription-timer-header">

          <div>

            <small>
              Подписка активна
            </small>

            <strong>
              До окончания
            </strong>

          </div>


          <div className="subscription-timer-icon">
            ⏱
          </div>

        </div>


        <div className="subscription-countdown">

          <div className="countdown-item">

            <strong>
              {remainingDays}
            </strong>

            <span>
              ДНЕЙ
            </span>

          </div>


          <div className="countdown-separator">
            :
          </div>


          <div className="countdown-item">

            <strong>
              {remainingHours}
            </strong>

            <span>
              ЧАСОВ
            </span>

          </div>


          <div className="countdown-separator">
            :
          </div>


          <div className="countdown-item">

            <strong>
              {remainingMinutes}
            </strong>

            <span>
              МИН
            </span>

          </div>

        </div>


        <div className="subscription-expire">

          <span>
            Действует до
          </span>

          <strong>
            {expiresAt}
          </strong>

        </div>

      </div>


      <section className="section">

        <div className="section-title">
          Подключение
        </div>





        <button
          className="primary-button connect-button"
          onClick={() =>
            setRenewOpen(
              (value) => !value,
            )
          }
        >
          {renewOpen
            ? 'Скрыть тарифы'
            : 'Продлить подписку'
          }

          <span>
            {renewOpen ? '↑' : '→'}
          </span>
        </button>

        {renewOpen && (

          <div className="renew-tariffs">

            <div className="tariff-grid">

              <button
                className={
                  selectedDays === 30
                    ? 'tariff-card active'
                    : 'tariff-card'
                }
                onClick={() =>
                  setSelectedDays(30)
                }
              >
                <div className="tariff-top">
                  <div>
                    <div className="tariff-period">
                      1 месяц
                    </div>

                    <div className="tariff-device">
                      2 устройства
                    </div>
                  </div>
                </div>

                <div className="tariff-price">
                  100 ₽
                </div>

                <div className="tariff-monthly">
                  100 ₽ / месяц
                </div>

                <div className="tariff-check">
                  {selectedDays === 30 ? '✓' : ''}
                </div>
              </button>


              <button
                className={
                  selectedDays === 90
                    ? 'tariff-card active'
                    : 'tariff-card'
                }
                onClick={() =>
                  setSelectedDays(90)
                }
              >
                <div className="tariff-top">
                  <div>
                    <div className="tariff-period">
                      3 месяца
                    </div>

                    <div className="tariff-device">
                      2 устройства
                    </div>
                  </div>
                </div>

                <div className="tariff-price">
                  300 ₽
                </div>

                <div className="tariff-monthly">
                  100 ₽ / месяц
                </div>

                <div className="tariff-check">
                  {selectedDays === 90 ? '✓' : ''}
                </div>
              </button>


              <button
                className={
                  selectedDays === 180
                    ? 'tariff-card active'
                    : 'tariff-card'
                }
                onClick={() =>
                  setSelectedDays(180)
                }
              >
                <div className="tariff-top">

                  <div>
                    <div className="tariff-period">
                      6 месяцев
                    </div>

                    <div className="tariff-device">
                      2 устройства
                    </div>
                  </div>

                  <div className="tariff-badge">
                    −5%
                  </div>

                </div>

                <div className="tariff-price">
                  570 ₽
                </div>

                <div className="tariff-monthly">
                  95 ₽ / месяц
                </div>

                <div className="tariff-check">
                  {selectedDays === 180 ? '✓' : ''}
                </div>
              </button>


              <button
                className={
                  selectedDays === 365
                    ? 'tariff-card active'
                    : 'tariff-card'
                }
                onClick={() =>
                  setSelectedDays(365)
                }
              >
                <div className="tariff-top">

                  <div>
                    <div className="tariff-period">
                      12 месяцев
                    </div>

                    <div className="tariff-device">
                      2 устройства
                    </div>
                  </div>

                  <div className="tariff-badge tariff-badge-best">
                    Выгодно
                  </div>

                </div>

                <div className="tariff-price">
                  1000 ₽
                </div>

                <div className="tariff-monthly">
                  ≈ 83 ₽ / месяц
                </div>

                <div className="tariff-check">
                  {selectedDays === 365 ? '✓' : ''}
                </div>
              </button>

            </div>


            <button
              className="primary-button tariff-buy-button"
              disabled={purchaseLoading}
              onClick={async () => {

                try {

                  setPurchaseLoading(true)
                  setPurchaseError(null)

                  const payment =
                    await createPurchase(
                      selectedDays,
                      subscription.id,
                    )

                  if (!payment.confirmation_url) {
                    throw new Error(
                      'Ссылка на оплату не получена',
                    )
                  }

                  window.location.href =
                    payment.confirmation_url

                } catch (error) {

                  setPurchaseError(
                    error instanceof Error
                      ? error.message
                      : 'Не удалось создать оплату',
                  )

                } finally {

                  setPurchaseLoading(false)

                }
              }}
            >

              {purchaseLoading
                ? 'Создаём оплату...'
                : `Продлить за ${selectedPrice} ₽`
              }

              <span>
                →
              </span>

            </button>


            {purchaseError && (
              <div
                style={{
                  marginTop: 12,
                  textAlign: 'center',
                }}
              >
                {purchaseError}
              </div>
            )}

          </div>

        )}




      </section>


      <section className="section">

        <div className="section-title">
          Ссылка для подключения
        </div>


        <div className="subscription-link-card">

          <div className="subscription-link-icon">
            🔗
          </div>


          <div className="subscription-link-content">

            <strong>
              Ваша ссылка
            </strong>

            <span>
              Скопируйте ссылку и добавьте её
              в поддерживаемое VPN-приложение
            </span>

          </div>

        </div>


        <div className="subscription-link">

          <span>

            {
              linkLoading
                ? 'Загрузка...'
                : linkError
                  ? 'Не удалось получить ссылку'
                  : subscriptionLinkDisplay ??
                  'Ссылка недоступна'
            }

          </span>


          <button
            disabled={!subscriptionLink}
            onClick={async () => {

              if (!subscriptionLink) {
                return
              }

              try {

                await navigator.clipboard.writeText(
                  subscriptionLink,
                )

              } catch (error) {

                console.error(
                  'Failed to copy subscription link:',
                  error,
                )

              }
            }}
          >
            Копировать
          </button>

        </div>

      </section>


      <section className="section">

        <div className="section-title">
          Приложения для подключения
        </div>


        <div className="vpn-apps">

          <a
            href="https://happ.info/"
            target="_blank"
            rel="noopener noreferrer"
            className="vpn-app-card"
          >

            <div className="vpn-app-icon">

              <img
                src={happIcon}
                alt="Happ"
              />

            </div>


            <div className="vpn-app-info">

              <strong>
                Happ
              </strong>

              <small>
                Скачать приложение и подключиться
              </small>

            </div>


            <span className="vpn-app-arrow">
              →
            </span>

          </a>


          <a
            href="https://incyyvpn.ru/download"
            target="_blank"
            rel="noopener noreferrer"
            className="vpn-app-card"
          >

            <div className="vpn-app-icon">

              <img
                src={incyIcon}
                alt="Incy"
              />

            </div>


            <div className="vpn-app-info">

              <strong>
                Incy
              </strong>

              <small>
                Скачать приложение и подключиться
              </small>

            </div>


            <span className="vpn-app-arrow">
              →
            </span>

          </a>

        </div>

      </section>


      <section className="section">

        <div className="section-title">
          Наши приложения
        </div>


        <div className="apps-card">

          <div className="app-item">

            <div className="app-icon">
              📱
            </div>


            <div className="app-info">

              <strong>
                JustFastVPN для Android
              </strong>

              <span>
                Подключение в одно нажатие
              </span>

            </div>


            <span className="app-badge">
              Скоро
            </span>

          </div>


          <div className="divider" />


          <div className="app-item">

            <div className="app-icon">
              
            </div>


            <div className="app-info">

              <strong>
                JustFastVPN для iOS
              </strong>

              <span>
                Подключение в одно нажатие
              </span>

            </div>


            <span className="app-badge">
              Скоро
            </span>

          </div>

        </div>

      </section>





      <section className="section">

        <div className="section-title">
          Мои устройства
        </div>


        <div className="empty-card">

          <div className="empty-icon">
            📱
          </div>

          <strong>
            Нет подключённых устройств
          </strong>

          <span>
            Подключённые устройства появятся здесь
          </span>

        </div>

      </section>

    </>
  )
}



function BalanceScreen() {

  return (

    <>

      <PageTitle
        title="Баланс"
        subtitle="Управление средствами"
      />


      <div className="large-balance-card">

        <span>
          Доступный баланс
        </span>

        <strong>
          0.00 ₽
        </strong>

        <button className="primary-button">

          Пополнить баланс

          <span>
            →
          </span>

        </button>

      </div>


      <section className="section">

        <div className="section-title">
          Промокод
        </div>


        <div className="promo-card">

          <div className="promo-icon">
            %
          </div>


          <div className="promo-content">

            <strong>
              Есть промокод?
            </strong>

            <span>
              Введите его, чтобы получить бонус
            </span>

          </div>


          <div className="promo-input-row">

            <input
              type="text"
              placeholder="Введите промокод"
            />

            <button>
              Применить
            </button>

          </div>

        </div>

      </section>


      <section className="section">

        <div className="section-title">
          История операций
        </div>


        <div className="empty-card">

          <div className="empty-icon">
            💳
          </div>

          <strong>
            Пока нет операций
          </strong>

          <span>
            История пополнений и платежей появится здесь
          </span>

        </div>

      </section>

    </>
  )
}



function ReferralsScreen() {

  const referralPercent = 25

  const referralBalance =
    '0.00 ₽'

  const invitedCount = 0

  const pendingReward =
    '0.00 ₽'


  return (

    <>

      <PageTitle
        title="Рефералы"
        subtitle="Приглашайте друзей и получайте бонусы"
      />


      <div className="referral-card">

        <div className="referral-icon">
          👥
        </div>

        <span>
          Ваш бонус
        </span>

        <strong>
          {referralBalance}
        </strong>

        <small>
          Приглашено друзей: {invitedCount}
        </small>

      </div>


      <section className="section">

        <div className="referral-percent-card">

          <div className="referral-percent-icon">
            %
          </div>


          <div className="referral-percent-info">

            <strong>
              {referralPercent}% вознаграждение
            </strong>

            <span>
              Получайте 25% с каждой оплаты
              приглашённых пользователей
            </span>

          </div>

        </div>

      </section>


      <section className="section">

        <div className="section-title">
          Ваша ссылка
        </div>


        <div className="referral-link">

          <span>
            t.me/justvpn_bot?start=ref
          </span>

          <button>
            Копировать
          </button>

        </div>

      </section>


      <section className="section">

        <div className="section-title">
          Как это работает
        </div>


        <div className="referral-steps">

          <div className="referral-step">

            <div className="referral-step-icon">
              1
            </div>


            <div>

              <strong>
                Пригласите друга
              </strong>

              <span>
                Отправьте ему вашу реферальную ссылку
              </span>

            </div>

          </div>


          <div className="divider" />


          <div className="referral-step">

            <div className="referral-step-icon">
              2
            </div>


            <div>

              <strong>
                Друг оформляет подписку
              </strong>

              <span>
                После оплаты вам начисляется 25%
              </span>

            </div>

          </div>


          <div className="divider" />


          <div className="referral-step">

            <div className="referral-step-icon">
              3
            </div>


            <div>

              <strong>
                Получаете вознаграждение
              </strong>

              <span>
                Начисление производится один раз в месяц
              </span>

            </div>

          </div>

        </div>

      </section>


      <section className="section">

        <div className="section-title">
          Начисления
        </div>


        <div className="referral-pending-card">

          <div className="referral-pending-icon">
            🕐
          </div>


          <div className="referral-pending-info">

            <strong>
              {pendingReward}
            </strong>

            <span>
              Ожидает ежемесячного начисления
            </span>

          </div>

        </div>


        <p className="referral-note">
          Средства переводятся на ваш счёт
          один раз в месяц.
        </p>

      </section>


      <section className="section">

        <div className="section-title">
          Куда направить вознаграждение
        </div>


        <div className="referral-destination">

          <button className="referral-destination-item active">

            <div className="referral-destination-icon">
              💳
            </div>


            <div>

              <strong>
                Пополнить баланс
              </strong>

              <span>
                Использовать средства для JustVPN
              </span>

            </div>


            <div className="referral-radio">
              ✓
            </div>

          </button>


          <div className="divider" />


          <button className="referral-destination-item">

            <div className="referral-destination-icon">
              💰
            </div>


            <div>

              <strong>
                Вывести средства
              </strong>

              <span>
                Получить вознаграждение на свой счёт
              </span>

            </div>


            <div className="referral-radio" />

          </button>

        </div>

      </section>


      <div className="referral-info-card">

        <span>
          💡
        </span>

        <p>
          Вознаграждение начисляется за каждого
          приглашённого пользователя после его оплаты.
          Выплата производится один раз в месяц.
        </p>

      </div>

    </>
  )
}



function NotificationsScreen({
  onClose,
}: {
  onClose: () => void
}) {

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

            <path
              d="M15 18l-6-6 6-6"
            />

          </svg>

        </button>


        <div>

          <div className="notifications-title">
            Уведомления
          </div>

          <div className="notifications-subtitle">
            Важные сообщения JustVPN
          </div>

        </div>

      </div>


      <div className="notification-list">

        <div className="notification-card unread">

          <div className="notification-icon">

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

          </div>


          <div className="notification-content">

            <div className="notification-top">

              <strong>
                Ответ поддержки
              </strong>

              <span>
                Сегодня, 14:42
              </span>

            </div>

            <p>
              Поддержка ответила на ваш тикет.
            </p>

          </div>


          <span className="notification-unread-dot" />

        </div>


        <div className="notification-card">

          <div className="notification-icon">

            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
            >

              <path
                d="M12 3v18"
              />

              <path
                d="M17 7H9.5a2.5 2.5 0 0 0 0 5H14a2.5 2.5 0 0 1 0 5H7"
              />

            </svg>

          </div>


          <div className="notification-content">

            <div className="notification-top">

              <strong>
                Реферальный бонус
              </strong>

              <span>
                10 августа
              </span>

            </div>

            <p>
              Вам начислен реферальный бонус.
            </p>

          </div>

        </div>

      </div>

    </div>
  )
}



function SupportScreen() {

  return (

    <>

      <PageTitle
        title="Поддержка"
        subtitle="Мы готовы помочь"
      />


      <section className="support-main-card">

        <div className="support-main-icon">

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

        </div>


        <h2>
          Нужна помощь?
        </h2>

        <p>
          Создайте обращение, и наша поддержка
          поможет решить ваш вопрос.
        </p>


        <button className="primary-button">

          Создать обращение

          <span>
            →
          </span>

        </button>

      </section>


      <section className="section">

        <div className="section-title">
          Мои обращения
        </div>


        <div className="support-empty-card">

          <div className="support-empty-icon">

            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
            >

              <path
                d="M4 5h16v12H8l-4 4V5Z"
              />

              <path
                d="M8 9h8"
              />

              <path
                d="M8 13h5"
              />

            </svg>

          </div>


          <strong>
            Нет обращений
          </strong>

          <span>
            Здесь будут отображаться ваши обращения
            в службу поддержки
          </span>

        </div>

      </section>


      <section className="section">

        <div className="section-title">
          Быстрая помощь
        </div>


        <div className="support-options">

          <button className="support-option">

            <div className="support-option-icon">

              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
              >

                <circle
                  cx="12"
                  cy="12"
                  r="9"
                />

                <path
                  d="M9.5 9a2.5 2.5 0 1 1 4.2 1.8c-.9.7-1.7 1.1-1.7 2.2"
                />

                <path
                  d="M12 16h.01"
                />

              </svg>

            </div>


            <div>

              <strong>
                Частые вопросы
              </strong>

              <small>
                Ответы на популярные вопросы
              </small>

            </div>


            <span>
              →
            </span>

          </button>


          <button className="support-option">

            <div className="support-option-icon">

              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
              >

                <path
                  d="M4 5h16v12H8l-4 4V5Z"
                />

                <path
                  d="M8 9h8"
                />

                <path
                  d="M8 13h5"
                />

              </svg>

            </div>


            <div>

              <strong>
                Связаться с поддержкой
              </strong>

              <small>
                Напишите нам напрямую
              </small>

            </div>


            <span>
              →
            </span>

          </button>

        </div>

      </section>

    </>
  )
}



function PageTitle({
  title,
  subtitle,
}: {
  title: string
  subtitle: string
}) {

  return (

    <section className="page-title">

      <h1>
        {title}
      </h1>

      <p>
        {subtitle}
      </p>

    </section>
  )
}



function BottomNavigation({
  activeTab,
  onChange,
}: {
  activeTab: Tab
  onChange: (tab: Tab) => void
}) {

  const items: {
    id: Tab
    icon: string
    label: string
  }[] = [

      {
        id: 'home',
        icon: '⌂',
        label: 'Главная',
      },

      {
        id: 'subscription',
        icon: '▣',
        label: 'Подписка',
      },

      {
        id: 'balance',
        icon: '▤',
        label: 'Баланс',
      },

      {
        id: 'referrals',
        icon: '♧',
        label: 'Рефералы',
      },

      {
        id: 'support',
        icon: '◯',
        label: 'Поддержка',
      },

    ]


  return (

    <nav className="bottom-navigation">

      {items.map((item) => (

        <button
          key={item.id}
          className={
            activeTab === item.id
              ? 'nav-item active'
              : 'nav-item'
          }
          onClick={() =>
            onChange(item.id)
          }
        >

          <span className="nav-icon">
            {item.icon}
          </span>

          <span>
            {item.label}
          </span>

        </button>

      ))}

    </nav>
  )
}


export default App