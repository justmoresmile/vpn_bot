import { useEffect, useState } from 'react'

import './App.css'



import Settings from './pages/Settings'


import HomeScreen from './pages/Home'

import SubscriptionScreen from './pages/Subscription'

import BalanceScreen from './pages/Balance'

import NotificationsScreen from './pages/Notifications'

import SupportScreen from './pages/Support'

import EmailAuthScreen from './components/auth/EmailAuthScreen'

import BottomNavigation from './components/layout/BottomNavigation'







import { useTheme } from './theme/ThemeContext'



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



type Tab =

  | 'home'

  | 'subscription'

  | 'balance'

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

    mode: authMode,

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
            onClick={() => {
              setActiveTab('balance')
              setNotificationsOpen(false)
              setSettingsOpen(false)
            }}
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

export default App
