import {
  useEffect,
  useRef,
  useState,
} from 'react'

import PageTitle from '../components/common/PageTitle'

import {
  closeSupportTicket,
  createSupportTicket,
  deleteSupportTicket,
  getSupportTicket,
  getSupportTickets,
  sendSupportMessage,
} from '../api/support'

import type {
  SupportTicket,
  SupportTicketDetails,
} from '../api/support'


function SupportScreen({

  openTicketId,

}: {

  openTicketId?: number | null

}) {

  const [
    tickets,
    setTickets,
  ] = useState<SupportTicket[]>([])

  const [
    ticketsLoading,
    setTicketsLoading,
  ] = useState(true)

  const [
    supportError,
    setSupportError,
  ] = useState<string | null>(null)

  const [
    createOpen,
    setCreateOpen,
  ] = useState(false)

  const [
    faqOpen,
    setFaqOpen,
  ] = useState(false)

  const [
    faqExpanded,
    setFaqExpanded,
  ] = useState<number | null>(null)

  const [
    subject,
    setSubject,
  ] = useState('')

  const [
    message,
    setMessage,
  ] = useState('')

  const [
    creating,
    setCreating,
  ] = useState(false)

  const [
    selectedTicket,
    setSelectedTicket,
  ] = useState<SupportTicketDetails | null>(
    null,
  )


  useEffect(() => {

    if (!openTicketId) {
      return
    }

    let cancelled = false

    const openTicket =
      async () => {

        try {

          setSupportError(null)

          const ticket =
            await getSupportTicket(
              openTicketId,
            )

          if (!cancelled) {

            setSelectedTicket(ticket)

            setFaqOpen(false)
            setCreateOpen(false)

          }

        } catch (error) {

          if (!cancelled) {

            setSupportError(
              error instanceof Error
                ? error.message
                : 'Не удалось открыть обращение',
            )

          }

        }

      }

    void openTicket()

    return () => {
      cancelled = true
    }

  }, [openTicketId])


  const [
    replyMessage,
    setReplyMessage,
  ] = useState('')

  const [
    sendingReply,
    setSendingReply,
  ] = useState(false)

  const [
    closingTicket,
    setClosingTicket,
  ] = useState(false)

  const chatBottomRef =
    useRef<HTMLDivElement | null>(null)

  const chatScrollRef =
    useRef<HTMLDivElement | null>(null)

  const previousMessageCountRef =
    useRef(0)

  const [
    chatAtBottom,
    setChatAtBottom,
  ] = useState(true)

  const [
    showNewMessageButton,
    setShowNewMessageButton,
  ] = useState(false)


  useEffect(() => {

    const loadTickets = async () => {

      try {

        setTicketsLoading(true)
        setSupportError(null)

        const result =
          await getSupportTickets()

        setTickets(result)

      } catch (error) {

        setSupportError(
          error instanceof Error
            ? error.message
            : 'Не удалось загрузить обращения',
        )

      } finally {

        setTicketsLoading(false)

      }

    }

    void loadTickets()

  }, [])


  useEffect(() => {

    if (!selectedTicket) {
      return
    }

    const ticketId =
      selectedTicket.id

    const refreshTicket =
      async () => {

        try {

          const updated =
            await getSupportTicket(
              ticketId,
            )

          setSelectedTicket(
            (current) => {

              if (
                !current
                || current.id !== ticketId
              ) {
                return current
              }

              return updated
            },
          )

          setTickets(
            (current) =>
              current.map(
                (ticket) =>
                  ticket.id === updated.id
                    ? {
                        ...ticket,
                        status:
                          updated.status,
                        updated_at:
                          updated.updated_at,
                        closed_at:
                          updated.closed_at,
                      }
                    : ticket,
              ),
          )

        } catch {

          // Не закрываем чат из-за временной
          // ошибки сети. Следующая попытка
          // будет через 2 секунды.

        }

      }

    const interval =
      window.setInterval(
        () => {
          void refreshTicket()
        },
        2000,
      )

    return () => {
      window.clearInterval(
        interval,
      )
    }

  }, [selectedTicket?.id])


  useEffect(() => {

    if (!selectedTicket) {

      previousMessageCountRef.current = 0
      setShowNewMessageButton(false)
      setChatAtBottom(true)

      return
    }

    const currentCount =
      selectedTicket.messages.length

    const previousCount =
      previousMessageCountRef.current

    const hasNewMessage =
      previousCount > 0
      && currentCount > previousCount

    previousMessageCountRef.current =
      currentCount

    if (
      chatAtBottom
      || previousCount === 0
    ) {

      const timer =
        window.setTimeout(
          () => {

            chatBottomRef.current?.scrollIntoView({
              behavior:
                previousCount === 0
                  ? 'auto'
                  : 'smooth',
              block: 'end',
            })

          },
          50,
        )

      setShowNewMessageButton(false)

      return () => {
        window.clearTimeout(timer)
      }

    }

    if (hasNewMessage) {
      setShowNewMessageButton(true)
    }

  }, [
    selectedTicket?.id,
    selectedTicket?.messages.length,
    chatAtBottom,
  ])


  const handleChatScroll = () => {

    const element =
      chatScrollRef.current

    if (!element) {
      return
    }

    const distanceFromBottom =
      element.scrollHeight
      - element.scrollTop
      - element.clientHeight

    const nearBottom =
      distanceFromBottom < 120

    setChatAtBottom(
      nearBottom,
    )

    if (nearBottom) {
      setShowNewMessageButton(false)
    }

  }


  const scrollChatToBottom = () => {

    chatBottomRef.current?.scrollIntoView({
      behavior: 'smooth',
      block: 'end',
    })

    setChatAtBottom(true)
    setShowNewMessageButton(false)
  }


  const handleCreateTicket =
    async () => {

      const cleanSubject =
        subject.trim()

      const cleanMessage =
        message.trim()

      if (!cleanSubject) {
        setSupportError(
          'Укажите тему обращения',
        )
        return
      }

      if (!cleanMessage) {
        setSupportError(
          'Напишите сообщение',
        )
        return
      }

      try {

        setCreating(true)
        setSupportError(null)

        const created =
          await createSupportTicket(
            cleanSubject,
            cleanMessage,
          )

        setTickets(
          (current) => [
            created,
            ...current.filter(
              (ticket) =>
                ticket.id !== created.id,
            ),
          ],
        )

        setSubject('')
        setMessage('')
        setCreateOpen(false)

        setSelectedTicket(
          created,
        )

      } catch (error) {

        setSupportError(
          error instanceof Error
            ? error.message
            : 'Не удалось создать обращение',
        )

      } finally {

        setCreating(false)

      }

    }


  const openTicket =
    async (
      ticketId: number,
    ) => {

      try {

        setSupportError(null)

        const result =
          await getSupportTicket(
            ticketId,
          )

        setSelectedTicket(
          result,
        )

        setReplyMessage('')

      } catch (error) {

        setSupportError(
          error instanceof Error
            ? error.message
            : 'Не удалось открыть обращение',
        )

      }

    }


  const handleSendReply =
    async () => {

      if (!selectedTicket) {
        return
      }

      const cleanMessage =
        replyMessage.trim()

      if (!cleanMessage) {
        return
      }

      try {

        setSendingReply(true)
        setSupportError(null)

        const created =
          await sendSupportMessage(
            selectedTicket.id,
            cleanMessage,
          )

        setSelectedTicket(
          (current) =>
            current
              ? {
                  ...current,
                  status: 'open',
                  messages: [
                    ...current.messages,
                    created,
                  ],
                }
              : current,
        )

        setTickets(
          (current) =>
            current.map(
              (ticket) =>
                ticket.id
                === selectedTicket.id
                  ? {
                      ...ticket,
                      status: 'open',
                      updated_at:
                        created.created_at,
                    }
                  : ticket,
            ),
        )

        setReplyMessage('')

      } catch (error) {

        setSupportError(
          error instanceof Error
            ? error.message
            : 'Не удалось отправить сообщение',
        )

      } finally {

        setSendingReply(false)

      }

    }


  const handleCloseTicket =
    async () => {

      if (!selectedTicket) {
        return
      }

      try {

        setClosingTicket(true)
        setSupportError(null)

        const closed =
          await closeSupportTicket(
            selectedTicket.id,
          )

        setSelectedTicket(
          (current) =>
            current
              ? {
                  ...current,
                  status: closed.status,
                  closed_at:
                    closed.closed_at,
                  updated_at:
                    closed.updated_at,
                }
              : current,
        )

        setTickets(
          (current) =>
            current.map(
              (ticket) =>
                ticket.id
                === closed.id
                  ? closed
                  : ticket,
            ),
        )

      } catch (error) {

        setSupportError(
          error instanceof Error
            ? error.message
            : 'Не удалось закрыть обращение',
        )

      } finally {

        setClosingTicket(false)

      }

    }


  const handleDeleteTicket =
    async (
      ticketId: number,
    ) => {

      const confirmed =
        window.confirm(
          'Удалить обращение?\n\n'
          + 'История переписки будет удалена безвозвратно.',
        )

      if (!confirmed) {
        return
      }

      try {

        setSupportError(null)

        await deleteSupportTicket(
          ticketId,
        )

        setTickets(
          (current) =>
            current.filter(
              (ticket) =>
                ticket.id !== ticketId,
            ),
        )

        if (
          selectedTicket?.id
          === ticketId
        ) {
          setSelectedTicket(null)
        }

      } catch (error) {

        setSupportError(
          error instanceof Error
            ? error.message
            : 'Не удалось удалить обращение',
        )

      }

    }


  const formatTicketDate = (
    value: string,
  ) => {

    const normalized =
      value.endsWith('Z')
      || /[+-]\d{2}:\d{2}$/.test(value)
        ? value
        : `${value}Z`

    return new Date(
      normalized,
    ).toLocaleString(
      'ru-RU',
      {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      },
    )
  }


  const ticketStatusText = (
    status: string,
  ) => {

    if (status === 'closed') {
      return 'Закрыто'
    }

    if (status === 'waiting_user') {
      return 'Ждёт вашего ответа'
    }

    return 'Открыто'
  }



  const faqItems = [
    {
      question: 'VPN не подключается',
      answer: (
        <>
          Проверьте, работает ли интернет без VPN.
          Затем попробуйте переподключиться или выбрать
          другой сервер. Если проблема осталась —
          перезапустите приложение и проверьте,
          активна ли подписка.
        </>
      ),
    },
    {
      question: 'VPN подключён, но интернета нет',
      answer: (
        <>
          Отключите VPN и убедитесь, что обычный
          интернет работает. После этого подключитесь
          заново или выберите другой сервер.
          Также попробуйте перезапустить VPN-приложение.
        </>
      ),
    },
    {
      question: 'Почему VPN работает медленно?',
      answer: (
        <>
          Скорость зависит от сервера, провайдера
          и качества соединения. Попробуйте выбрать
          другой сервер, а также сравните скорость
          через Wi-Fi и мобильный интернет.
        </>
      ),
    },
    {
      question: 'Как подключить новое устройство?',
      answer: (
        <>
          Откройте раздел «Подписка», скопируйте
          ссылку подписки и добавьте её в поддерживаемое
          VPN-приложение. Если достигнут лимит устройств,
          его можно изменить на главной странице.
        </>
      ),
    },
    {
      question: 'Сколько устройств можно подключить?',
      answer: (
        <>
          Количество доступных устройств зависит
          от выбранного вами лимита. Текущий лимит
          отображается в Mini App и может быть изменён
          в настройках подписки.
        </>
      ),
    },
    {
      question: 'Где взять ссылку на подписку?',
      answer: (
        <>
          Перейдите в раздел «Подписка» и откройте
          активную подписку. Там находится ваша
          персональная ссылка для подключения.
        </>
      ),
    },
    {
      question: 'Оплата прошла, но баланс не изменился',
      answer: (
        <>
          Обновите Mini App и подождите немного —
          обработка платежа может занять некоторое время.
          Если деньги списались, а баланс так и не
          изменился, создайте обращение в поддержку.
        </>
      ),
    },
    {
      question: 'Оплата не проходит',
      answer: (
        <>
          Проверьте данные оплаты и наличие средств.
          Если платёж продолжает отклоняться,
          попробуйте повторить его позже. Если деньги
          были списаны — создайте обращение.
        </>
      ),
    },
    {
      question: 'Как удалить старое устройство?',
      answer: (
        <>
          Откройте раздел «Подписка» и список
          «Мои устройства». Найдите ненужное устройство
          и нажмите кнопку удаления.
        </>
      ),
    },
    {
      question: 'Как связаться с поддержкой?',
      answer: (
        <>
          На этой странице нажмите «Создать обращение»,
          укажите тему и опишите проблему. Ответ
          поддержки появится прямо в чате обращения.
        </>
      ),
    },
  ]


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





        <button
          className="primary-button"
          onClick={() => {
            setSupportError(null)
            setCreateOpen(true)
          }}
        >



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





        {ticketsLoading ? (

          <div className="support-empty-card">
            <strong>
              Загружаем обращения...
            </strong>
          </div>

        ) : tickets.length === 0 ? (

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

        ) : (

          <div
            style={{
              display: 'grid',
              gap: 10,
            }}
          >

            {tickets.map(
              (ticket) => (

                <div
                  key={ticket.id}
                  style={{
                    display: 'flex',
                    alignItems: 'stretch',
                    justifyContent: 'space-between',
                    gap: 12,
                    width: '100%',
                    boxSizing: 'border-box',
                    padding: 16,
                    borderRadius: 18,
                    background:
                      'rgba(127, 127, 127, 0.07)',
                    border:
                      '1px solid rgba(127, 127, 127, 0.10)',
                  }}
                >

                  <button
                    type="button"
                    onClick={() => {
                      void openTicket(
                        ticket.id,
                      )
                    }}
                    style={{
                      flex: 1,
                      minWidth: 0,
                      padding: 0,
                      border: 0,
                      background: 'transparent',
                      color: 'inherit',
                      font: 'inherit',
                      textAlign: 'left',
                      cursor: 'pointer',
                    }}
                  >

                    <div
                      style={{
                        fontSize: 12,
                        color:
                          'var(--text-secondary)',
                      }}
                    >
                      Обращение #{ticket.id}
                    </div>

                    <div
                      style={{
                        marginTop: 4,
                        fontSize: 15,
                        fontWeight: 750,
                        overflow: 'hidden',
                        textOverflow:
                          'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {ticket.subject}
                    </div>

                    <div
                      style={{
                        marginTop: 10,
                        fontSize: 12,
                        color:
                          'var(--text-secondary)',
                      }}
                    >
                      Обновлено{' '}
                      {formatTicketDate(
                        ticket.updated_at,
                      )}
                    </div>

                  </button>


                  <div
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'flex-end',
                      justifyContent:
                        'space-between',
                      flexShrink: 0,
                      gap: 12,
                    }}
                  >

                    <div
                      style={{
                        fontSize: 11,
                        fontWeight: 700,
                        padding:
                          '5px 10px',
                        borderRadius: 999,
                        background:
                          'var(--accent-soft)',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {ticketStatusText(
                        ticket.status,
                      )}
                    </div>


                    <button
                      type="button"
                      aria-label="Удалить обращение"
                      title="Удалить обращение"
                      onClick={(event) => {
                        event.stopPropagation()

                        void handleDeleteTicket(
                          ticket.id,
                        )
                      }}
                      style={{
                        width: 34,
                        height: 34,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent:
                          'center',
                        padding: 0,
                        borderRadius: 11,
                        border:
                          '1px solid rgba(239,68,68,0.18)',
                        background:
                          'rgba(239,68,68,0.08)',
                        color: '#ef4444',
                        cursor: 'pointer',
                      }}
                    >

                      <svg
                        width="17"
                        height="17"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M3 6h18" />
                        <path d="M8 6V4h8v2" />
                        <path d="M19 6l-1 14H6L5 6" />
                        <path d="M10 11v5" />
                        <path d="M14 11v5" />
                      </svg>

                    </button>

                  </div>

                </div>

              ),
            )}

          </div>

        )}



      </section>





      <section className="section">



        <div className="section-title">

          Быстрая помощь

        </div>





        <div className="support-options">



          <button
            className="support-option"
            onClick={() => {
              setFaqExpanded(null)
              setFaqOpen(true)
            }}
          >



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





          



        </div>



      </section>



      {faqOpen && (

        <div
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 1050,
            display: 'flex',
            flexDirection: 'column',
            background:
              'var(--background)',
            color:
              'var(--text)',
          }}
        >

          <div
            style={{
              padding: '14px 16px',
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              borderBottom:
                '1px solid rgba(127,127,127,0.12)',
              background:
                'var(--card)',
            }}
          >

            <button
              type="button"
              onClick={() => {
                setFaqOpen(false)
                setFaqExpanded(null)
              }}
              style={{
                width: 40,
                height: 40,
                borderRadius: 14,
                border: 0,
                background:
                  'rgba(127,127,127,0.08)',
                color: 'inherit',
                fontSize: 20,
                cursor: 'pointer',
              }}
            >
              ←
            </button>

            <div>
              <div
                style={{
                  fontSize: 18,
                  fontWeight: 850,
                }}
              >
                Частые вопросы
              </div>

              <div
                style={{
                  marginTop: 2,
                  fontSize: 12,
                  color:
                    'var(--text-secondary)',
                }}
              >
                Быстрые ответы на основные вопросы
              </div>
            </div>

          </div>


          <div
            style={{
              flex: 1,
              overflowY: 'auto',
              padding: 16,
              paddingBottom: 110,
            }}
          >

            <div
              style={{
                display: 'grid',
                gap: 10,
              }}
            >

              {faqItems.map(
                (item, index) => {

                  const expanded =
                    faqExpanded === index

                  return (

                    <div
                      key={item.question}
                      style={{
                        borderRadius: 18,
                        overflow: 'hidden',
                        background:
                          'rgba(127,127,127,0.07)',
                        border:
                          '1px solid rgba(127,127,127,0.10)',
                      }}
                    >

                      <button
                        type="button"
                        onClick={() => {
                          setFaqExpanded(
                            expanded
                              ? null
                              : index,
                          )
                        }}
                        style={{
                          width: '100%',
                          padding: '16px',
                          display: 'flex',
                          justifyContent:
                            'space-between',
                          alignItems: 'center',
                          gap: 14,
                          border: 0,
                          background:
                            'transparent',
                          color: 'inherit',
                          textAlign: 'left',
                          font: 'inherit',
                          cursor: 'pointer',
                        }}
                      >

                        <span
                          style={{
                            fontSize: 14,
                            fontWeight: 750,
                          }}
                        >
                          {item.question}
                        </span>

                        <span
                          style={{
                            flexShrink: 0,
                            fontSize: 18,
                            color:
                              'var(--text-secondary)',
                            transform:
                              expanded
                                ? 'rotate(90deg)'
                                : 'rotate(0deg)',
                            transition:
                              'transform 0.18s ease',
                          }}
                        >
                          ›
                        </span>

                      </button>


                      {expanded && (

                        <div
                          style={{
                            padding:
                              '0 16px 16px',
                            fontSize: 13,
                            lineHeight: 1.55,
                            color:
                              'var(--text-secondary)',
                          }}
                        >
                          {item.answer}
                        </div>

                      )}

                    </div>

                  )

                },
              )}

            </div>


            <div
              style={{
                marginTop: 22,
                padding: 18,
                borderRadius: 20,
                textAlign: 'center',
                background:
                  'var(--accent-soft)',
              }}
            >

              <div
                style={{
                  fontSize: 15,
                  fontWeight: 800,
                }}
              >
                Не нашли ответ?
              </div>

              <div
                style={{
                  marginTop: 5,
                  fontSize: 12,
                  color:
                    'var(--text-secondary)',
                }}
              >
                Напишите нам — разберёмся с проблемой.
              </div>

              <button
                type="button"
                className="primary-button"
                onClick={() => {
                  setFaqOpen(false)
                  setFaqExpanded(null)
                  setSupportError(null)
                  setCreateOpen(true)
                }}
                style={{
                  width: '100%',
                  marginTop: 14,
                }}
              >
                Создать обращение
              </button>

            </div>

          </div>

        </div>

      )}


      {selectedTicket && (

        <div
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 1100,
            display: 'flex',
            flexDirection: 'column',
            background:
              'var(--background)',
            color:
              'var(--text)',
          }}
        >

          <div
            style={{
              padding:
                '14px 16px',
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              borderBottom:
                '1px solid rgba(127,127,127,0.12)',
              background:
                'var(--card)',
            }}
          >

            <button
              type="button"
              onClick={() => {
                setSelectedTicket(null)
                setSupportError(null)
              }}
              style={{
                width: 40,
                height: 40,
                borderRadius: 14,
                border: 0,
                background:
                  'rgba(127,127,127,0.08)',
                color: 'inherit',
                fontSize: 20,
                cursor: 'pointer',
              }}
            >
              ←
            </button>


            <div
              style={{
                minWidth: 0,
                flex: 1,
              }}
            >

              <div
                style={{
                  fontSize: 12,
                  color:
                    'var(--text-secondary)',
                }}
              >
                Обращение #{selectedTicket.id}
              </div>

              <div
                style={{
                  marginTop: 2,
                  fontSize: 16,
                  fontWeight: 800,
                  overflow: 'hidden',
                  textOverflow:
                    'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {selectedTicket.subject}
              </div>

            </div>


            <div
              style={{
                fontSize: 11,
                fontWeight: 700,
                padding:
                  '5px 8px',
                borderRadius: 999,
                background:
                  'var(--accent-soft)',
                whiteSpace: 'nowrap',
              }}
            >
              {ticketStatusText(
                selectedTicket.status,
              )}
            </div>

          </div>


          <div
            ref={chatScrollRef}
            onScroll={handleChatScroll}
            style={{
              flex: 1,
              overflowY: 'auto',
              padding: 16,
              display: 'flex',
              flexDirection: 'column',
              gap: 10,
            }}
          >

            {selectedTicket.messages.map(
              (item) => {

                const fromUser =
                  item.sender_type
                  === 'user'

                return (

                  <div
                    key={item.id}
                    style={{
                      display: 'flex',
                      justifyContent:
                        fromUser
                          ? 'flex-end'
                          : 'flex-start',
                    }}
                  >

                    <div
                      style={{
                        maxWidth: '82%',
                        padding:
                          '10px 12px',
                        borderRadius:
                          fromUser
                            ? '18px 18px 5px 18px'
                            : '18px 18px 18px 5px',
                        background:
                          fromUser
                            ? 'var(--accent-soft)'
                            : 'var(--card)',
                        border:
                          '1px solid rgba(127,127,127,0.10)',
                      }}
                    >

                      <div
                        style={{
                          fontSize: 11,
                          fontWeight: 700,
                          color:
                            'var(--text-secondary)',
                        }}
                      >
                        {fromUser
                          ? 'Вы'
                          : item.sender_type === 'admin'
                            ? 'Поддержка'
                            : 'Система'
                        }
                      </div>

                      <div
                        style={{
                          marginTop: 4,
                          fontSize: 14,
                          lineHeight: 1.45,
                          whiteSpace:
                            'pre-wrap',
                          wordBreak:
                            'break-word',
                        }}
                      >
                        {item.message}
                      </div>

                      <div
                        style={{
                          marginTop: 5,
                          fontSize: 10,
                          textAlign: 'right',
                          color:
                            'var(--text-secondary)',
                        }}
                      >
                        {formatTicketDate(
                          item.created_at,
                        )}
                      </div>

                    </div>

                  </div>

                )

              },
            )}


            <div
              ref={chatBottomRef}
              style={{
                height: 1,
              }}
            />


            {supportError && (

              <div
                style={{
                  padding: 10,
                  fontSize: 12,
                  textAlign: 'center',
                }}
              >
                {supportError}
              </div>

            )}

          </div>


          {showNewMessageButton && (

            <button
              type="button"
              onClick={scrollChatToBottom}
              style={{
                position: 'absolute',
                right: 16,
                bottom:
                  selectedTicket.status === 'closed'
                    ? 70
                    : 125,
                zIndex: 5,
                padding:
                  '9px 13px',
                border: 0,
                borderRadius: 999,
                background:
                  'var(--accent)',
                color: '#fff',
                fontSize: 12,
                fontWeight: 750,
                boxShadow:
                  '0 6px 20px rgba(0,0,0,0.20)',
                cursor: 'pointer',
              }}
            >
              ↓ Новое сообщение
            </button>

          )}


          {selectedTicket.status !== 'closed' ? (

            <div
              style={{
                padding:
                  '10px 12px 14px',
                background:
                  'var(--card)',
                borderTop:
                  '1px solid rgba(127,127,127,0.12)',
              }}
            >

              <div
                style={{
                  display: 'flex',
                  gap: 8,
                  alignItems:
                    'flex-end',
                }}
              >

                <textarea
                  value={replyMessage}
                  maxLength={4000}
                  rows={1}
                  placeholder="Сообщение..."
                  disabled={sendingReply}
                  onChange={(event) =>
                    setReplyMessage(
                      event.target.value,
                    )
                  }
                  style={{
                    flex: 1,
                    minHeight: 44,
                    maxHeight: 120,
                    resize: 'none',
                    boxSizing:
                      'border-box',
                    padding:
                      '11px 13px',
                    borderRadius: 16,
                    border:
                      '1px solid rgba(127,127,127,0.16)',
                    background:
                      'rgba(127,127,127,0.07)',
                    color: 'inherit',
                    font: 'inherit',
                    outline: 'none',
                  }}
                />

                <button
                  type="button"
                  disabled={
                    sendingReply
                    || !replyMessage.trim()
                  }
                  onClick={() => {
                    void handleSendReply()
                  }}
                  style={{
                    width: 44,
                    height: 44,
                    flexShrink: 0,
                    border: 0,
                    borderRadius: 15,
                    background:
                      'var(--accent)',
                    color: '#fff',
                    fontSize: 20,
                    cursor: 'pointer',
                  }}
                >
                  →
                </button>

              </div>


              <button
                type="button"
                disabled={
                  closingTicket
                  || sendingReply
                }
                onClick={() => {
                  void handleCloseTicket()
                }}
                style={{
                  width: '100%',
                  marginTop: 8,
                  padding:
                    '9px 12px',
                  border: 0,
                  background:
                    'transparent',
                  color:
                    'var(--text-secondary)',
                  fontSize: 12,
                  cursor: 'pointer',
                }}
              >
                {closingTicket
                  ? 'Закрываем...'
                  : 'Закрыть обращение'
                }
              </button>

            </div>

          ) : (

            <div
              style={{
                padding:
                  '14px 16px',
                textAlign: 'center',
                background:
                  'var(--card)',
                borderTop:
                  '1px solid rgba(127,127,127,0.12)',
                fontSize: 13,
                color:
                  'var(--text-secondary)',
              }}
            >
              Обращение закрыто
            </div>

          )}

        </div>

      )}


      {createOpen && (

        <div
          onClick={() => {
            if (!creating) {
              setCreateOpen(false)
            }
          }}
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 1000,
            padding: 20,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background:
              'rgba(0, 0, 0, 0.45)',
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
              }}
            >
              Новое обращение
            </div>


            <div
              style={{
                marginTop: 6,
                fontSize: 13,
                color:
                  'var(--text-secondary)',
              }}
            >
              Опишите проблему — поддержка
              ответит вам здесь.
            </div>


            <input
              type="text"
              value={subject}
              maxLength={120}
              placeholder="Тема обращения"
              onChange={(event) =>
                setSubject(
                  event.target.value,
                )
              }
              style={{
                width: '100%',
                boxSizing:
                  'border-box',
                marginTop: 18,
                padding:
                  '13px 14px',
                borderRadius: 14,
                border:
                  '1px solid rgba(127,127,127,0.16)',
                background:
                  'rgba(127,127,127,0.07)',
                color: 'inherit',
                font: 'inherit',
                outline: 'none',
              }}
            />


            <textarea
              value={message}
              maxLength={4000}
              placeholder="Опишите проблему"
              onChange={(event) =>
                setMessage(
                  event.target.value,
                )
              }
              style={{
                width: '100%',
                minHeight: 130,
                resize: 'vertical',
                boxSizing:
                  'border-box',
                marginTop: 10,
                padding:
                  '13px 14px',
                borderRadius: 14,
                border:
                  '1px solid rgba(127,127,127,0.16)',
                background:
                  'rgba(127,127,127,0.07)',
                color: 'inherit',
                font: 'inherit',
                outline: 'none',
              }}
            />


            {supportError && (

              <div
                style={{
                  marginTop: 10,
                  fontSize: 12,
                  textAlign: 'center',
                }}
              >
                {supportError}
              </div>

            )}


            <button
              type="button"
              className="primary-button"
              disabled={creating}
              onClick={() => {
                void handleCreateTicket()
              }}
              style={{
                width: '100%',
                marginTop: 16,
              }}
            >
              {creating
                ? 'Отправляем...'
                : 'Отправить обращение'
              }
            </button>


            <button
              type="button"
              disabled={creating}
              onClick={() =>
                setCreateOpen(false)
              }
              style={{
                width: '100%',
                marginTop: 8,
                padding:
                  '12px 14px',
                borderRadius: 14,
                border: 0,
                background:
                  'transparent',
                color: 'inherit',
                cursor: 'pointer',
              }}
            >
              Отмена
            </button>

          </div>

        </div>

      )}


      {!createOpen && supportError && (

        <div
          style={{
            marginTop: 14,
            fontSize: 12,
            textAlign: 'center',
          }}
        >
          {supportError}
        </div>

      )}


    </>

  )

}

export default SupportScreen
