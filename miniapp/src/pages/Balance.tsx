import {
  useEffect,
  useState,
} from 'react'

import {
  createBalanceTopup,
  getWalletHistory,
  type WalletResponse,
  type WalletTransaction,
} from '../api/balance'

import PageTitle from '../components/common/PageTitle'


function BalanceScreen({
  wallet,
}: {
  wallet: WalletResponse | null
}) {

  const [
    topupOpen,
    setTopupOpen,
  ] = useState(false)

  const [
    selectedAmount,
    setSelectedAmount,
  ] = useState(300)

  const [
    customAmount,
    setCustomAmount,
  ] = useState('')

  const [
    topupLoading,
    setTopupLoading,
  ] = useState(false)

  const [
    topupError,
    setTopupError,
  ] = useState<string | null>(null)


  const [
    transactions,
    setTransactions,
  ] = useState<WalletTransaction[]>([])

  const [
    historyLoading,
    setHistoryLoading,
  ] = useState(true)

  const [
    historyError,
    setHistoryError,
  ] = useState<string | null>(null)


  const balance =
    wallet?.balance_rubles ?? 0

  const dailyPrice =
    wallet?.daily_price_rubles ?? 0

  const daysAvailable =
    wallet?.days_available ?? 0


  const shortage =
    wallet
      ? Math.max(
          0,
          wallet.daily_price_kopecks
          - wallet.balance_kopecks,
        ) / 100
      : 0


  useEffect(() => {

    let cancelled = false

    async function loadHistory() {

      try {

        setHistoryLoading(true)
        setHistoryError(null)

        const response =
          await getWalletHistory()

        if (!cancelled) {
          setTransactions(
            response.items,
          )
        }

      } catch (error) {

        if (!cancelled) {

          setHistoryError(
            error instanceof Error
              ? error.message
              : 'Не удалось загрузить историю',
          )

        }

      } finally {

        if (!cancelled) {
          setHistoryLoading(false)
        }

      }

    }

    loadHistory()

    return () => {
      cancelled = true
    }

  }, [])


  function getTransactionTitle(
    transaction: WalletTransaction,
  ): string {

    switch (transaction.type) {

      case 'topup':
      case 'test_credit':
        return 'Пополнение баланса'

      case 'daily_charge':
        return 'Оплата доступа'

      case 'trial_finish_charge':
        return 'Оплата доступа'

      case 'trial_finish_refund':
      case 'billing_refund':
      case 'refund':
        return 'Возврат средств'

      default:
        return transaction.amount_kopecks >= 0
          ? 'Пополнение баланса'
          : 'Оплата VPN'
    }
  }


  function formatTransactionDate(
    timestamp: number,
  ): string {

    const date =
      new Date(
        timestamp * 1000,
      )

    const now =
      new Date()

    const today =
      date.toDateString()
      === now.toDateString()

    const yesterdayDate =
      new Date(now)

    yesterdayDate.setDate(
      now.getDate() - 1,
    )

    const yesterday =
      date.toDateString()
      === yesterdayDate.toDateString()

    const time =
      date.toLocaleTimeString(
        'ru-RU',
        {
          hour: '2-digit',
          minute: '2-digit',
        },
      )

    if (today) {
      return `Сегодня, ${time}`
    }

    if (yesterday) {
      return `Вчера, ${time}`
    }

    return date.toLocaleString(
      'ru-RU',
      {
        day: 'numeric',
        month: 'long',
        hour: '2-digit',
        minute: '2-digit',
      },
    )
  }


  function formatTransactionAmount(
    amountKopecks: number,
  ): string {

    const amount =
      Math.abs(
        amountKopecks,
      ) / 100

    const sign =
      amountKopecks >= 0
        ? '+'
        : '−'

    return `${sign}${amount.toLocaleString(
      'ru-RU',
      {
        minimumFractionDigits:
          Number.isInteger(amount)
            ? 0
            : 2,
        maximumFractionDigits: 2,
      },
    )} ₽`
  }


  async function handleTopup() {

    const amount =
      customAmount.trim()
        ? Number(customAmount)
        : selectedAmount

    if (
      !Number.isFinite(amount)
      || amount < 10
      || amount > 10000
    ) {

      setTopupError(
        'Введите сумму от 10 до 10 000 ₽',
      )

      return
    }

    try {

      setTopupLoading(true)
      setTopupError(null)

      const payment =
        await createBalanceTopup(
          amount,
        )

      if (!payment.confirmation_url) {

        throw new Error(
          'Ссылка на оплату не получена',
        )
      }

      window.location.href =
        payment.confirmation_url

    } catch (error) {

      setTopupError(
        error instanceof Error
          ? error.message
          : 'Не удалось создать платёж',
      )

    } finally {

      setTopupLoading(false)

    }
  }


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
          {balance.toFixed(2)} ₽
        </strong>

        <button
          className="primary-button"
          onClick={() => {
            setTopupOpen(
              (value) => !value,
            )
            setTopupError(null)
          }}
        >

          {topupOpen
            ? 'Скрыть пополнение'
            : 'Пополнить баланс'
          }

          <span>
            {topupOpen ? '↑' : '→'}
          </span>

        </button>

      </div>


      {topupOpen && (

        <section className="section">

          <div className="section-title">
            Сумма пополнения
          </div>

          <div className="apps-card">

            <div
              style={{
                display: 'grid',
                gridTemplateColumns:
                  'repeat(2, 1fr)',
                gap: 10,
              }}
            >

              {[100, 300, 500, 1000].map(
                (amount) => (

                  <button
                    key={amount}
                    type="button"
                    className={
                      !customAmount
                      && selectedAmount === amount
                        ? 'tariff-card active'
                        : 'tariff-card'
                    }
                    onClick={() => {
                      setSelectedAmount(
                        amount,
                      )
                      setCustomAmount('')
                      setTopupError(null)
                    }}
                    style={{
                      minHeight: 64,
                    }}
                  >
                    <strong>
                      {amount} ₽
                    </strong>
                  </button>

                ),
              )}

            </div>


            <div
              style={{
                marginTop: 12,
              }}
            >

              <input
                type="number"
                inputMode="numeric"
                min="10"
                max="10000"
                placeholder="Другая сумма"
                value={customAmount}
                onChange={(event) => {
                  setCustomAmount(
                    event.target.value,
                  )
                  setTopupError(null)
                }}
                style={{
                  width: '100%',
                  boxSizing: 'border-box',
                  minHeight: 56,
                  padding: '0 16px',
                  borderRadius: 16,
                  border: '1px solid rgba(127, 127, 127, 0.18)',
                  background: 'rgba(127, 127, 127, 0.06)',
                  color: 'inherit',
                  fontSize: 16,
                  fontWeight: 600,
                  outline: 'none',
                }}
              />

            </div>


            {topupError && (

              <div
                style={{
                  marginTop: 12,
                  textAlign: 'center',
                  fontSize: 13,
                }}
              >
                {topupError}
              </div>

            )}


            <button
              type="button"
              className="primary-button"
              onClick={handleTopup}
              disabled={topupLoading}
              style={{
                marginTop: 14,
                width: '100%',
              }}
            >
              {topupLoading
                ? 'Создаём оплату...'
                : `Пополнить на ${
                    customAmount.trim()
                      ? customAmount
                      : selectedAmount
                  } ₽`
              }
            </button>

          </div>

        </section>

      )}


      <section className="section">

        <div className="section-title">
          Текущий тариф
        </div>

        <div className="apps-card">

          <div className="app-item">

            <div className="app-icon">
              ⚡
            </div>

            <div className="app-info">

              <strong>
                {dailyPrice} ₽ / 24 часа
              </strong>

              <span>
                Стоимость при текущем количестве устройств
              </span>

            </div>

          </div>

          <div className="divider" />

          <div className="app-item">

            <div className="app-icon">
              ⏳
            </div>

            <div className="app-info">

              <strong>
                {daysAvailable > 0
                  ? `Хватит на ${daysAvailable} ${
                      daysAvailable === 1
                        ? 'день'
                        : daysAvailable < 5
                          ? 'дня'
                          : 'дней'
                    }`
                  : shortage > 0
                    ? `Не хватает ${shortage.toFixed(2)} ₽`
                    : 'Недостаточно средств'
                }
              </strong>

              <span>
                {daysAvailable > 0
                  ? 'Без учёта уже оплаченного текущего периода'
                  : 'Для следующего списания'
                }
              </span>

            </div>

          </div>

        </div>

      </section>


      <section className="section">

        <div className="section-title">
          История операций
        </div>


        {historyLoading ? (

          <div className="empty-card">

            <strong>
              Загружаем операции...
            </strong>

          </div>

        ) : historyError ? (

          <div className="empty-card">

            <strong>
              Не удалось загрузить историю
            </strong>

            <span>
              Попробуйте открыть экран ещё раз
            </span>

          </div>

        ) : transactions.length === 0 ? (

          <div className="empty-card">

            <div className="empty-icon">
              💳
            </div>

            <strong>
              Пока нет операций
            </strong>

            <span>
              Здесь появятся пополнения и списания
            </span>

          </div>

        ) : (

          <div className="apps-card">

            {transactions.map(
              (
                transaction,
                index,
              ) => (

                <div
                  key={transaction.id}
                >

                  {index > 0 && (
                    <div className="divider" />
                  )}

                  <div className="app-item">

                    <div className="app-icon">
                      {transaction.amount_kopecks >= 0
                        ? '↓'
                        : '↑'
                      }
                    </div>

                    <div className="app-info">

                      <strong>
                        {getTransactionTitle(
                          transaction,
                        )}
                      </strong>

                      <span>
                        {formatTransactionDate(
                          transaction.created_at,
                        )}
                      </span>

                    </div>

                    <strong
                      style={{
                        marginLeft: 'auto',
                        whiteSpace: 'nowrap',
                        fontSize: 15,
                      }}
                    >
                      {formatTransactionAmount(
                        transaction.amount_kopecks,
                      )}
                    </strong>

                  </div>

                </div>

              ),
            )}

          </div>

        )}

      </section>

    </>
  )
}


export default BalanceScreen
