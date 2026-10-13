import { useEffect, useState } from 'react'

import './App.css'



import Settings from './pages/Settings'


import HomeScreen from './pages/Home'

import SubscriptionScreen from './pages/Subscription'

import BalanceScreen from './pages/Balance'

import NotificationsScreen from './pages/Notifications'

import {
  getUnreadNotificationCount,
} from './api/notifications'

import SupportScreen from './pages/Support'

import EmailAuthScreen from './components/auth/EmailAuthScreen'
import AuthChoiceScreen from './components/auth/AuthChoiceScreen'

import BottomNavigation from './components/layout/BottomNavigation'










import {

  initTelegramWebApp,

  getTelegramStartParam,

} from './api/telegram'



import { useAuth } from './context/AuthContext'



import {

  getSubscriptions,

  getSubscriptionUsage,

  type Subscription,

  getSubscriptionDevices,

} from './api/subscription'

import {
  getTrialStatus,
  startTrial,
  type TrialStatus,
} from './api/trial'

import {
  getWallet,
  type WalletResponse,
} from './api/balance'
import { useTheme } from './theme/ThemeContext'



type Tab =

  | 'home'

  | 'subscription'

  | 'balance'

  | 'support'

  | 'account'





function App() {

  const { mode, setMode } = useTheme()




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

    mode: authMode,

    continueWithTelegram,

    useEmailLogin,

    requestEmailCode,

    verifyEmailCode,

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
    trial,
    setTrial,
  ] = useState<TrialStatus | null>(
    null,
  )

  const [
    wallet,
    setWallet,
  ] = useState<WalletResponse | null>(
    null,
  )

  const [
    accountDataLoading,
    setAccountDataLoading,
  ] = useState(false)

  const [
    accountDataError,
    setAccountDataError,
  ] = useState<string | null>(
    null,
  )


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

      tab === 'support' ||

      tab === 'account' ||

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


  function handleTabChange(
    tab: Tab,
  ) {

    setNotificationsOpen(false)
    setSettingsOpen(false)
    setActiveTab(tab)
  }


  const [

    unreadNotificationCount,

    setUnreadNotificationCount,

  ] = useState(0)


  const [

    supportTicketToOpen,

    setSupportTicketToOpen,

  ] = useState<number | null>(null)


  useEffect(() => {

    let cancelled = false


    async function loadUnreadCount() {

      try {

        const result =
          await getUnreadNotificationCount()

        if (!cancelled) {
          setUnreadNotificationCount(
            result.count,
          )
        }

      } catch (error) {

        console.error(
          'Failed to load unread notifications',
          error,
        )

      }

    }


    void loadUnreadCount()


    const timer =
      window.setInterval(
        () => {
          void loadUnreadCount()
        },
        5000,
      )


    return () => {

      cancelled = true

      window.clearInterval(timer)

    }

  }, [])
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



  const [

    subscriptionDevices,

    setSubscriptionDevices,

  ] = useState({

    count: 0,

    limit: 2,

    devices: [],

  })



  useEffect(() => {

    let cancelled = false


    async function loadDevices() {

      if (!activeSubscription) {

        if (!cancelled) {

          setSubscriptionDevices({
            count: 0,
            limit: 2,
            devices: [],
          })

        }

        return
      }


      if (
        activeTab !== 'home'
        && activeTab !== 'subscription'
      ) {
        return
      }


      if (document.hidden) {
        return
      }


      try {

        const devices =
          await getSubscriptionDevices(
            activeSubscription.id,
          )


        if (cancelled) {
          return
        }


        console.log(
          'Subscription devices:',
          devices,
        )


        setSubscriptionDevices(
          devices
        )

      } catch (error) {

        if (cancelled) {
          return
        }

        console.error(
          'Failed to load subscription devices:',
          error,
        )

      }
    }


    function handleVisibilityChange() {

      if (
        !document.hidden
        && (
          activeTab === 'home'
          || activeTab === 'subscription'
        )
      ) {

        loadDevices()

      }
    }


    function handleFocus() {

      if (
        activeTab === 'home'
        || activeTab === 'subscription'
      ) {

        loadDevices()

      }
    }


    loadDevices()


    const timer =
      window.setInterval(
        loadDevices,
        30000,
      )


    document.addEventListener(
      'visibilitychange',
      handleVisibilityChange,
    )

    window.addEventListener(
      'focus',
      handleFocus,
    )


    return () => {

      cancelled = true

      window.clearInterval(
        timer,
      )

      document.removeEventListener(
        'visibilitychange',
        handleVisibilityChange,
      )

      window.removeEventListener(
        'focus',
        handleFocus,
      )

    }

  }, [
    activeSubscription,
    activeTab,
  ])


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



  async function refreshAccountData() {

    if (!user) {
      return
    }

    try {

      setAccountDataLoading(true)
      setAccountDataError(null)

      const [
        trialData,
        walletData,
        subscriptionsData,
      ] = await Promise.all([
        getTrialStatus(),
        getWallet(),
        getSubscriptions(),
      ])

      setTrial(trialData)
      setWallet(walletData)
      setSubscriptions(
        subscriptionsData,
      )

    } catch (error) {

      console.error(
        'Failed to refresh account data:',
        error,
      )

      setAccountDataError(
        error instanceof Error
          ? error.message
          : 'Не удалось загрузить данные аккаунта',
      )

    } finally {

      setAccountDataLoading(false)

    }

  }


  useEffect(() => {

    if (!user) {
      return
    }

    setSubscriptionsLoading(true)
    setSubscriptionsError(null)

    refreshAccountData()
      .catch((error) => {

        console.error(
          'Initial account load failed:',
          error,
        )

      })
      .finally(() => {

        setSubscriptionsLoading(false)

      })

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



  async function handleStartTrial() {

    try {

      setAccountDataLoading(true)
      setAccountDataError(null)

      await startTrial()

      await refreshAccountData()

    } catch (error) {

      console.error(
        'Failed to start trial:',
        error,
      )

      setAccountDataError(
        error instanceof Error
          ? error.message
          : 'Не удалось запустить пробный период',
      )

    } finally {

      setAccountDataLoading(false)

    }

  }


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





  if (
    authMode === 'choice' &&
    !user
  ) {

    return (
      <AuthChoiceScreen
        error={error}
        onTelegram={
          continueWithTelegram
        }
        onEmail={
          useEmailLogin
        }
      />
    )
  }


  if (
    authMode === 'email' &&
    !user
  ) {

    return (
      <EmailAuthScreen
        error={error}
        onRequestCode={
          requestEmailCode
        }
        onVerifyCode={
          verifyEmailCode
        }
      />
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

          {error && (
            <>
              <br />
              <br />
              {error}
            </>
          )}
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

        <div className="header-brand-row">

          <div className="text-brand">
            <span>Just</span>
            <strong>VPN</strong>
          </div>

          <button
            type="button"
            className="header-balance"
            onClick={() =>
              handleTabChange('balance')
            }
            aria-label="Открыть баланс"
          >
            {(
              wallet?.balance_rubles ?? 0
            ).toFixed(2)} ₽
          </button>

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



            {unreadNotificationCount > 0 && (
              <span className="notification-dot" />
            )}



          </button>

          <button
            type="button"
            className="theme-button"
            onClick={() =>
              setMode(
                mode === 'dark'
                  ? 'light'
                  : 'dark'
              )
            }
            aria-label="Переключить тему"
            title={
              mode === 'dark'
                ? 'Светлая тема'
                : 'Тёмная тема'
            }
          >
            {mode === 'dark' ? (
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
              >
                <circle
                  cx="12"
                  cy="12"
                  r="4"
                />
                <path d="M12 2v2" />
                <path d="M12 20v2" />
                <path d="M4.93 4.93l1.42 1.42" />
                <path d="M17.65 17.65l1.42 1.42" />
                <path d="M2 12h2" />
                <path d="M20 12h2" />
                <path d="M4.93 19.07l1.42-1.42" />
                <path d="M17.65 6.35l1.42-1.42" />
              </svg>
            ) : (
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path
                  d="M21 12.79A9 9 0 1 1 11.21 3
                     7 7 0 0 0 21 12.79z"
                />
              </svg>
            )}
          </button>

          <button
            type="button"
            className="account-button"
            onClick={() =>
              handleTabChange(
                'account'
              )
            }
            aria-label="Аккаунт"
          >

            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle
                cx="12"
                cy="8"
                r="4"
              />

              <path
                d="M4.5 21a7.5 7.5 0 0 1 15 0"
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

            onOpenSupportTicket={(
              ticketId,
            ) => {

              setSupportTicketToOpen(
                ticketId,
              )

              handleTabChange(
                'support'
              )

            }}

            onUnreadChanged={() => {

              getUnreadNotificationCount()
                .then((result) => {
                  setUnreadNotificationCount(
                    result.count,
                  )
                })
                .catch((error) => {
                  console.error(
                    'Failed to refresh unread notifications',
                    error,
                  )
                })

            }}

          />



        ) : (



          <>



            {activeTab === 'home' && (



              <HomeScreen

                daysLeft={daysLeft}

                subscription={activeSubscription}

                usageTotal={subscriptionUsage.total}

                subscriptionDevices={subscriptionDevices}
                trial={trial}
                wallet={wallet}

                accountDataLoading={
                  accountDataLoading
                }

                accountDataError={
                  accountDataError
                }

                onStartTrial={
                  handleStartTrial
                }



                onSubscriptionClick={() => {

                  setActiveTab('subscription')

                  setRenewOpen(false)

                }}

                onBalanceClick={() => {

                  setActiveTab('balance')

                }}

                onDeviceDeleted={(hwid) => {

                  setSubscriptionDevices(
                    (current) => ({
                      ...current,
                      count: Math.max(
                        0,
                        current.count - 1,
                      ),
                      devices:
                        current.devices.filter(
                          (device) =>
                            device.id !== hwid,
                        ),
                    }),
                  )

                }}

                onDeviceLimitChanged={(deviceLimit) => {

                  setSubscriptionDevices(
                    (current) => ({
                      ...current,
                      limit: deviceLimit,
                    }),
                  )

                  void refreshAccountData()

                }}

                onDevicesClick={() => {

                  setActiveTab('subscription')

                  setRenewOpen(false)

                  setTimeout(() => {

                    document
                      .getElementById(
                        'subscription-devices'
                      )
                      ?.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start',
                      })

                  }, 100)

                }}




              />

            )}



            {activeTab === 'subscription' && (



              <SubscriptionScreen

                subscription={activeSubscription}

                renewOpen={renewOpen}

                setRenewOpen={setRenewOpen}

                subscriptionDevices={subscriptionDevices}

                wallet={wallet}

                onDeviceDeleted={(hwid) => {

                  setSubscriptionDevices(
                    (current) => ({
                      ...current,
                      count: Math.max(
                        0,
                        current.count - 1,
                      ),
                      devices:
                        current.devices.filter(
                          (device) =>
                            device.id !== hwid,
                        ),
                    }),
                  )

                }}

                onDeviceLimitChanged={(deviceLimit) => {

                  setSubscriptionDevices(
                    (current) => ({
                      ...current,
                      limit: deviceLimit,
                    }),
                  )

                  refreshAccountData()
                    .catch((error) => {
                      console.error(
                        'Failed to refresh after device limit change:',
                        error,
                      )
                    })

                }}

              />



            )}





            {activeTab === 'balance' && (

              <BalanceScreen
                wallet={wallet}
              />

            )}









            {activeTab === 'account' && (

              <Settings
                onClose={() =>
                  handleTabChange(
                    'home'
                  )
                }
              />

            )}


            {activeTab === 'support' && (

              <SupportScreen
                openTicketId={
                  supportTicketToOpen
                }
              />

            )}



          </>



        )}



      </main>





      {!settingsOpen && (



        <BottomNavigation

          activeTab={activeTab}

          onChange={handleTabChange}

        />



      )}



    </div>

  )

}

export default App
