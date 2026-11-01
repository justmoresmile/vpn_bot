import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  adjustAdminUserBalance,
  extendAdminSubscription,
  removeAdminSubscriptionBonus,
  setAdminSubscriptionUntil,
  blockAdminUser,
  getAdminUser,
  getAdminUsers,
  unblockAdminUser,
  type AdminUserDetail,
  type AdminUserFilter,
  type AdminUserListItem,
} from '../../api/admin'

import './Admin.css'


const FILTERS: {
  id: AdminUserFilter
  label: string
}[] = [
  {
    id: 'all',
    label: 'Все',
  },
  {
    id: 'active',
    label: 'Активные',
  },
  {
    id: 'expired',
    label: 'Истекли',
  },
  {
    id: 'no_subscription',
    label: 'Без VPN',
  },
  {
    id: 'blocked',
    label: 'Заблокированы',
  },
]


function normalizeAdminDate(
  value: string | null | undefined,
): string | null {

  if (!value) return null

  if (
    value.endsWith('Z')
    || /[+-]\d{2}:\d{2}$/.test(value)
  ) {
    return value
  }

  return `${value}Z`
}


function getAdminTransactionTitle(
  transaction: {
    type: string
    amount_kopecks: number
    description: string | null
  },
): string {

  const description =
    transaction.description || ''

  const devicesMatch =
    description.match(
      /devices=(\d+)/,
    )

  const devices =
    devicesMatch
      ? Number(devicesMatch[1])
      : null

  const devicesText =
    devices
      ? `${devices} ${
          devices === 1
            ? 'устройство'
            : devices >= 2
              && devices <= 4
              ? 'устройства'
              : 'устройств'
        }`
      : null

  switch (transaction.type) {

    case 'admin_credit':
      return 'Начисление администратором'

    case 'admin_debit':
      return 'Списание администратором'

    case 'daily_charge':
      return devicesText
        ? `Оплата VPN · ${devicesText} · 24 часа`
        : 'Оплата VPN · 24 часа'

    case 'trial_finish_charge':
      return devicesText
        ? `Оплата VPN после пробного периода · ${devicesText}`
        : 'Оплата VPN после пробного периода'

    case 'topup':
      return 'Пополнение баланса'

    case 'test_credit':
      return 'Пополнение баланса'

    case 'trial_finish_refund':
      return 'Возврат после пробного периода'

    case 'billing_refund':
    case 'refund':
      return 'Возврат средств'

    default:
      return transaction.amount_kopecks >= 0
        ? 'Начисление'
        : 'Списание'
  }
}


function getBonusDaysLeft(
  value: string | null | undefined,
): number {

  const normalized =
    normalizeAdminDate(value)

  if (!normalized) return 0

  const end =
    new Date(normalized).getTime()

  if (
    Number.isNaN(end)
    || end <= Date.now()
  ) {
    return 0
  }

  return Math.ceil(
    (
      end - Date.now()
    ) / 86400000,
  )
}


function formatDate(
  value: string | null,
): string {

  if (!value) {
    return '—'
  }

  const date =
    new Date(value)

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return '—'
  }

  return date.toLocaleDateString(
    'ru-RU',
    {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    },
  )
}


function getDisplayName(
  user: {
    username: string | null
    first_name: string | null
    email: string | null
    telegram_id: number | null
  },
): string {

  if (user.username) {
    return `@${user.username}`
  }

  if (user.first_name) {
    return user.first_name
  }

  if (user.email) {
    return user.email
  }

  if (user.telegram_id) {
    return `Telegram ${user.telegram_id}`
  }

  return 'Пользователь'
}


function Admin() {

  const [
    customRemoveBonusDays,
    setCustomRemoveBonusDays,
  ] = useState('')


  const [
    customAmount,
    setCustomAmount,
  ] = useState('')


  const [
    customDays,
    setCustomDays,
  ] = useState('')



  const [
    users,
    setUsers,
  ] = useState<AdminUserListItem[]>([])

  const [
    total,
    setTotal,
  ] = useState(0)

  const [
    search,
    setSearch,
  ] = useState('')

  const [
    filter,
    setFilter,
  ] = useState<AdminUserFilter>('all')

  const [
    loading,
    setLoading,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState<string | null>(null)

  const [
    selectedUser,
    setSelectedUser,
  ] = useState<AdminUserDetail | null>(null)

  const [
    detailLoading,
    setDetailLoading,
  ] = useState(false)

  const [
    actionLoading,
    setActionLoading,
  ] = useState(false)










  const [customUntil, setCustomUntil] =
    useState('')


  async function loadUsers() {

    try {

      setLoading(true)
      setError(null)

      const result =
        await getAdminUsers({
          search:
            search.trim() || undefined,
          filter,
          limit: 100,
          offset: 0,
        })

      setUsers(
        result.items,
      )

      setTotal(
        result.total,
      )

    } catch (error) {

      console.error(
        'Failed to load admin users:',
        error,
      )

      setError(
        error instanceof Error
          ? error.message
          : 'Не удалось загрузить пользователей',
      )

    } finally {

      setLoading(false)
    }
  }


  useEffect(() => {

    const timer =
      window.setTimeout(
        () => {
          void loadUsers()
        },
        250,
      )

    return () => {
      window.clearTimeout(
        timer,
      )
    }

  }, [
    search,
    filter,
  ])


  async function openUser(
    userId: number,
  ) {

    try {

      setDetailLoading(true)
      setError(null)

      const result =
        await getAdminUser(
          userId,
        )

      setSelectedUser(
        result,
      )

    } catch (error) {

      setError(
        error instanceof Error
          ? error.message
          : 'Не удалось открыть пользователя',
      )

    } finally {

      setDetailLoading(false)
    }
  }


  async function refreshSelectedUser() {

    if (!selectedUser) {
      return
    }

    const result =
      await getAdminUser(
        selectedUser.id,
      )

    setSelectedUser(
      result,
    )

    await loadUsers()
  }


  async function changeBalance(
    action: 'credit' | 'debit',
    amount: number,
  ) {

    if (!selectedUser) {
      return
    }

    if (
      !Number.isFinite(amount)
      || amount <= 0
    ) {
      return
    }

    try {

      setActionLoading(true)
      setError(null)

      await adjustAdminUserBalance(
        selectedUser.id,
        action,
        amount,
        'Изменено через Admin Mini App',
      )

      setCustomAmount('')

      await refreshSelectedUser()

    } catch (error) {

      setError(
        error instanceof Error
          ? error.message
          : 'Не удалось изменить баланс',
      )

    } finally {

      setActionLoading(false)
    }
  }


  async function extendSubscription(
    subscriptionId: number,
    days: number,
  ) {

    if (!selectedUser) {
      return
    }

    try {

      setActionLoading(true)
      setError(null)

      await extendAdminSubscription(
        selectedUser.id,
        subscriptionId,
        days,
      )

      await refreshSelectedUser()

    } catch (error) {

      setError(
        error instanceof Error
          ? error.message
          : 'Не удалось продлить подписку',
      )

    } finally {

      setActionLoading(false)
    }
  }


  async function setSubscriptionUntil(
    subscriptionId: number,
    until: string,
  ) {

    if (!selectedUser || !until) {
      return
    }

    try {

      setActionLoading(true)
      setError(null)

      await setAdminSubscriptionUntil(
        selectedUser.id,
        subscriptionId,
        until,
      )

      setCustomUntil('')

      await refreshSelectedUser()

    } catch (error) {

      setError(
        error instanceof Error
          ? error.message
          : 'Не удалось изменить дату',
      )

    } finally {

      setActionLoading(false)
    }
  }


  async function toggleBlock() {

    if (!selectedUser) {
      return
    }

    try {

      setActionLoading(true)
      setError(null)

      if (
        selectedUser.is_blocked
      ) {

        await unblockAdminUser(
          selectedUser.id,
        )

      } else {

        await blockAdminUser(
          selectedUser.id,
        )
      }

      await refreshSelectedUser()

    } catch (error) {

      setError(
        error instanceof Error
          ? error.message
          : 'Не удалось изменить статус пользователя',
      )

    } finally {

      setActionLoading(false)
    }
  }


  const stats =
    useMemo(
      () => {

        const active =
          users.filter(
            (user) =>
              user.subscription?.status
              === 'active',
          ).length

        const blocked =
          users.filter(
            (user) =>
              user.is_blocked,
          ).length

        return {
          active,
          blocked,
        }
      },
      [users],
    )


  if (selectedUser) {

    const subscription =
      selectedUser.subscriptions[0]
      ?? null

    return (
      <div className="admin-page">

        <button
          type="button"
          className="admin-back"
          onClick={() =>
            setSelectedUser(null)
          }
        >
          ← Пользователи
        </button>


        <section className="admin-user-header">

          <div className="admin-avatar">
            {(
              selectedUser.first_name
              || selectedUser.username
              || 'U'
            )
              .slice(0, 1)
              .toUpperCase()}
          </div>

          <div>

            <h2>
              {getDisplayName(
                selectedUser,
              )}
            </h2>

            <div className="admin-muted">

              ID: {selectedUser.id}

              {selectedUser.telegram_id && (
                <>
                  {' '}· Telegram:
                  {' '}
                  {selectedUser.telegram_id}
                </>
              )}

            </div>

          </div>

          <div
            className={
              selectedUser.is_blocked
                ? 'admin-status blocked'
                : 'admin-status active'
            }
          >
            {
              selectedUser.is_blocked
                ? 'Заблокирован'
                : 'Активен'
            }
          </div>

        </section>


        {error && (
          <div className="admin-error">
            {error}
          </div>
        )}


        <section className="admin-card">

          <div className="admin-card-title">
            Баланс
          </div>

          <div className="admin-balance">
            {
              selectedUser
                .balance_rubles
                .toFixed(2)
            } ₽
          </div>


          <div className="admin-quick-grid">

            <button
              type="button"
              disabled={actionLoading}
              onClick={() =>
                void changeBalance(
                  'credit',
                  100,
                )
              }
            >
              +100 ₽
            </button>

            <button
              type="button"
              disabled={actionLoading}
              onClick={() =>
                void changeBalance(
                  'credit',
                  500,
                )
              }
            >
              +500 ₽
            </button>

            <button
              type="button"
              disabled={actionLoading}
              onClick={() =>
                void changeBalance(
                  'credit',
                  1000,
                )
              }
            >
              +1000 ₽
            </button>

            <button
              type="button"
              disabled={actionLoading}
              onClick={() =>
                void changeBalance(
                  'debit',
                  100,
                )
              }
            >
              −100 ₽
            </button>

          </div>


          <div className="admin-custom-balance">

            <input
              type="number"
              min="1"
              step="1"
              placeholder="Введите сумму, ₽"
              value={customAmount}
              onChange={(event) =>
                setCustomAmount(
                  event.target.value,
                )
              }
            />

            <div className="admin-custom-balance-actions">

              <button
                type="button"
                disabled={
                  actionLoading
                  || !customAmount
                  || Number(customAmount) <= 0
                }
                onClick={() =>
                  void changeBalance(
                    'credit',
                    Number(customAmount),
                  )
                }
              >
                Начислить
              </button>

              <button
                type="button"
                className="danger"
                disabled={
                  actionLoading
                  || !customAmount
                  || Number(customAmount) <= 0
                }
                onClick={() =>
                  void changeBalance(
                    'debit',
                    Number(customAmount),
                  )
                }
              >
                Списать
              </button>

            </div>

          </div>

        </section>


        <section className="admin-card">

          <div className="admin-card-title">
            VPN-подписка
          </div>

          {subscription ? (
            <>

              <div className="admin-info-row">
                <span>Статус</span>
                <strong>
                  {subscription.status}
                </strong>
              </div>

              <div className="admin-info-row">
                <span>Протокол</span>
                <strong>
                  {
                    subscription
                      .protocol
                      .toUpperCase()
                  }
                </strong>
              </div>

              <div className="admin-info-row">
                <span>Биллинг</span>
                <strong>
                  {
                    subscription
                      .billing_mode
                  }
                </strong>
              </div>

              <div className="admin-info-row">
                <span>Устройств</span>
                <strong>
                  {
                    subscription
                      .device_limit
                  }
                </strong>
              </div>

              <div className="admin-info-row">
                <span>Действует до</span>
                <strong>
                  {
                    formatDate(
                      subscription
                        .expires_at,
                    )
                  }
                </strong>
              </div>


              <div className="admin-info-row">
                <span>Бонусное время</span>

                <strong>
                  {
                    getBonusDaysLeft(
                      subscription.bonus_until,
                    ) > 0
                      ? `${
                          getBonusDaysLeft(
                            subscription.bonus_until,
                          )
                        } дн. · до ${
                          formatDate(
                            subscription.bonus_until,
                          )
                        }`
                      : 'Нет'
                  }
                </strong>
              </div>

              {
                getBonusDaysLeft(
                  subscription.bonus_until,
                ) > 0 && (
                  <div className="admin-info-row">
                    <span>Бонус действует на</span>
                    <strong>
                      {
                        subscription.bonus_device_limit
                        ?? subscription.device_limit
                      } устр.
                    </strong>
                  </div>
                )
              }


              {
                getBonusDaysLeft(
                  subscription.bonus_until,
                ) > 0 && (
                  <>
                    <div
                      className="admin-subscription-manual-title"
                      style={{
                        marginTop: 16,
                      }}
                    >
                      Убрать бонусные дни
                    </div>

                    <div className="admin-subscription-actions">
                      {
                        [1, 7, 30].map(
                          (days) => (
                            <button
                              key={`remove-${days}`}
                              type="button"
                              disabled={actionLoading}
                              onClick={() => {
                                void (
                                  async () => {
                                    await removeAdminSubscriptionBonus(
                                      selectedUser.id,
                                      subscription.id,
                                      days,
                                    )

                                    window.location.reload()
                                  }
                                )()
                              }}
                            >
                              −{days} дн.
                            </button>
                          ),
                        )
                      }
                    </div>

                    <div
                      className="admin-subscription-manual"
                      style={{
                        marginTop: 12,
                      }}
                    >
                      <div className="admin-subscription-manual-title">
                        Снять вручную
                      </div>

                      <div className="admin-subscription-manual-row">

                        <input
                          type="number"
                          min="1"
                          step="1"
                          placeholder="Количество дней"
                          value={customRemoveBonusDays}
                          onChange={(event) =>
                            setCustomRemoveBonusDays(
                              event.target.value,
                            )
                          }
                        />

                        <button
                          type="button"
                          disabled={
                            actionLoading
                            || !customRemoveBonusDays
                            || Number(
                              customRemoveBonusDays,
                            ) <= 0
                          }
                          onClick={() => {
                            const days =
                              Number(
                                customRemoveBonusDays,
                              )

                            if (days <= 0) {
                              return
                            }

                            void (
                              async () => {
                                await removeAdminSubscriptionBonus(
                                  selectedUser.id,
                                  subscription.id,
                                  days,
                                )

                                setCustomRemoveBonusDays(
                                  '',
                                )

                                window.location.reload()
                              }
                            )()
                          }}
                        >
                          Убрать
                        </button>

                      </div>
                    </div>

                    <button
                      type="button"
                      className="admin-action-button danger"
                      disabled={actionLoading}
                      style={{
                        marginTop: 10,
                      }}
                      onClick={() => {
                        if (
                          !window.confirm(
                            'Удалить все бонусные дни?',
                          )
                        ) {
                          return
                        }

                        void (
                          async () => {
                            await removeAdminSubscriptionBonus(
                              selectedUser.id,
                              subscription.id,
                            )

                            window.location.reload()
                          }
                        )()
                      }}
                    >
                      Удалить все бонусные дни
                    </button>
                  </>
                )
              }


              <div className="admin-subscription-manual-title">
                Добавить бонусные дни
              </div>

              <div className="admin-subscription-actions">

                {[7, 30, 90, 365].map(
                  (days) => (

                    <button
                      key={days}
                      type="button"
                      disabled={actionLoading}
                      onClick={() =>
                        void extendSubscription(
                          subscription.id,
                          days,
                        )
                      }
                    >
                      +{days} дней
                    </button>

                  ),
                )}

              </div>


              <div className="admin-subscription-manual">

                <div className="admin-subscription-manual-title">
                  Ручное продление
                </div>

                <div className="admin-subscription-manual-row">

                  <input
                    type="number"
                    min="1"
                    step="1"
                    placeholder="Количество дней"
                    value={customDays}
                    onChange={(event) =>
                      setCustomDays(
                        event.target.value,
                      )
                    }
                  />

                  <button
                    type="button"
                    disabled={
                      actionLoading
                      || !customDays
                      || Number(customDays) <= 0
                    }
                    onClick={() => {
                      const days =
                        Number(customDays)

                      if (days > 0) {
                        void extendSubscription(
                          subscription.id,
                          days,
                        )
                        setCustomDays('')
                      }
                    }}
                  >
                    Добавить
                  </button>

                </div>


                <div className="admin-subscription-manual-title">
                  Установить дату
                </div>

                <div className="admin-subscription-manual-row">

                  <input
                    type="date"
                    value={customUntil}
                    onChange={(event) =>
                      setCustomUntil(
                        event.target.value,
                      )
                    }
                  />

                  <button
                    type="button"
                    disabled={
                      actionLoading
                      || !customUntil
                    }
                    onClick={() =>
                      void setSubscriptionUntil(
                        subscription.id,
                        customUntil,
                      )
                    }
                  >
                    Установить
                  </button>

                </div>

              </div>


              {subscription.billing_mode === 'balance' && (

                <div className="admin-balance-hint">
                  Добавленные дни являются
                  бесплатным периодом.
                  Баланс в это время не списывается.
                </div>

              )}

            </>
          ) : (
            <div className="admin-empty">
              У пользователя нет подписки
            </div>
          )}

        </section>


        <section className="admin-card">

          <div className="admin-card-title">
            Управление
          </div>

          <button
            type="button"
            className={
              selectedUser.is_blocked
                ? 'admin-action-button'
                : 'admin-action-button danger'
            }
            disabled={actionLoading}
            onClick={() =>
              void toggleBlock()
            }
          >
            {
              selectedUser.is_blocked
                ? 'Разблокировать пользователя'
                : 'Заблокировать пользователя'
            }
          </button>

        </section>


        <section className="admin-card">

          <div className="admin-card-title">
            Последние операции
          </div>

          {
            selectedUser
              .wallet_transactions
              .length === 0
          ? (
            <div className="admin-empty">
              Операций пока нет
            </div>
          ) : (
            selectedUser
              .wallet_transactions
              .slice(0, 10)
              .map((transaction) => (

                <div
                  key={transaction.id}
                  className="admin-transaction"
                >

                  <div>

                    <strong>
                      {
                        transaction
                          .amount_kopecks
                          > 0
                          ? '+'
                          : ''
                      }
                      {
                        (
                          transaction
                            .amount_kopecks
                          / 100
                        ).toFixed(2)
                      } ₽
                    </strong>

                    <div className="admin-muted">
                      {
                        getAdminTransactionTitle(
                          transaction,
                        )
                      }
                    </div>

                  </div>

                  <div className="admin-transaction-balance">
                    <span
                      style={{
                        opacity: 0.55,
                        fontSize: 11,
                        display: 'block',
                      }}
                    >
                      Баланс
                    </span>

                    <strong>
                      {
                        (
                          transaction
                            .balance_after_kopecks
                          / 100
                        ).toFixed(2)
                      } ₽
                    </strong>
                  </div>

                </div>

              )))
          }

        </section>

      </div>
    )
  }


  return (
    <div className="admin-page">

      <div className="admin-title-row">

        <div>
          <h1>Админ</h1>
          <div className="admin-muted">
            Управление JustVPN
          </div>
        </div>

        <div className="admin-total">
          {total}
        </div>

      </div>


      <div className="admin-stats">

        <div className="admin-stat">
          <strong>
            {total}
          </strong>
          <span>
            Пользователей
          </span>
        </div>

        <div className="admin-stat">
          <strong>
            {stats.active}
          </strong>
          <span>
            Активных
          </span>
        </div>

        <div className="admin-stat">
          <strong>
            {stats.blocked}
          </strong>
          <span>
            Заблокировано
          </span>
        </div>

      </div>


      <input
        className="admin-search"
        type="search"
        placeholder="Имя, username, Telegram ID, email"
        value={search}
        onChange={(event) =>
          setSearch(
            event.target.value,
          )
        }
      />


      <div className="admin-filters">

        {FILTERS.map((item) => (

          <button
            key={item.id}
            type="button"
            className={
              filter === item.id
                ? 'active'
                : ''
            }
            onClick={() =>
              setFilter(
                item.id,
              )
            }
          >
            {item.label}
          </button>

        ))}

      </div>


      {error && (
        <div className="admin-error">
          {error}
        </div>
      )}


      {loading ? (

        <div className="admin-loading">
          Загрузка пользователей...
        </div>

      ) : users.length === 0 ? (

        <div className="admin-empty">
          Пользователи не найдены
        </div>

      ) : (

        <div className="admin-users">

          {users.map((user) => (

            <button
              key={user.id}
              type="button"
              className="admin-user-card"
              onClick={() =>
                void openUser(
                  user.id,
                )
              }
            >

              <div className="admin-user-main">

                <div className="admin-user-avatar">
                  {(
                    user.first_name
                    || user.username
                    || 'U'
                  )
                    .slice(0, 1)
                    .toUpperCase()}
                </div>

                <div className="admin-user-text">

                  <strong>
                    {
                      getDisplayName(
                        user,
                      )
                    }
                  </strong>

                  <span>
                    ID {user.id}

                    {user.telegram_id && (
                      <>
                        {' '}· TG {user.telegram_id}
                      </>
                    )}
                  </span>

                </div>

              </div>


              <div className="admin-user-right">

                <strong>
                  {
                    user
                      .balance_rubles
                      .toFixed(0)
                  } ₽
                </strong>

                <span
                  className={
                    user.is_blocked
                      ? 'red'
                      : user.subscription
                        ?.status
                        === 'active'
                        ? 'green'
                        : ''
                  }
                >
                  {
                    user.is_blocked
                      ? 'Заблокирован'
                      : user.subscription
                        ?.status
                        === 'active'
                        ? `до ${
                            formatDate(
                              user
                                .subscription
                                .expires_at,
                            )
                          }`
                        : 'Нет активного VPN'
                  }
                </span>

              </div>

            </button>

          ))}

        </div>
      )}


      {detailLoading && (
        <div className="admin-overlay">
          Загрузка...
        </div>
      )}

    </div>
  )
}


export default Admin
