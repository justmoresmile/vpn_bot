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

export default NotificationsScreen
