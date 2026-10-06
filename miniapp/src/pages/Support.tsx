import PageTitle from '../components/common/PageTitle'


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

export default SupportScreen
