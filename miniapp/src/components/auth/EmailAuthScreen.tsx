import {
  useEffect,
  useState,
} from 'react'

import logoDark from '../../assets/justfastvpn-logo-dark.png'
import logoLight from '../../assets/justfastvpn-logo-white.png'


function EmailAuthScreen({
  error,
  onRequestCode,
  onVerifyCode,
}: {
  error: string | null

  onRequestCode: (
    email: string,
  ) => Promise<number>

  onVerifyCode: (
    email: string,
    code: string,
  ) => Promise<void>
}) {

  const [
    email,
    setEmail,
  ] = useState('')

  const [
    code,
    setCode,
  ] = useState('')

  const [
    step,
    setStep,
  ] = useState<
    'email' | 'code'
  >('email')

  const [
    submitting,
    setSubmitting,
  ] = useState(false)

  const [
    localError,
    setLocalError,
  ] = useState<string | null>(
    null,
  )

  const [
    retryAfter,
    setRetryAfter,
  ] = useState(0)


  useEffect(() => {

    if (retryAfter <= 0) {
      return
    }

    const timer =
      window.setInterval(
        () => {
          setRetryAfter(
            (current) =>
              Math.max(
                0,
                current - 1,
              ),
          )
        },
        1000,
      )

    return () => {
      window.clearInterval(
        timer,
      )
    }

  }, [retryAfter])


  async function handleRequestCode() {

    const normalizedEmail =
      email
        .trim()
        .toLowerCase()

    if (
      !normalizedEmail ||
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
        normalizedEmail,
      )
    ) {

      setLocalError(
        'Введите корректный email',
      )

      return
    }

    try {

      setSubmitting(true)
      setLocalError(null)

      await onRequestCode(
        normalizedEmail,
      )

      setEmail(
        normalizedEmail,
      )

      setStep(
        'code',
      )

      setRetryAfter(
        60,
      )

    } catch (requestError) {

      console.error(
        'Failed to request email code:',
        requestError,
      )

      setLocalError(
        requestError instanceof Error
          ? requestError.message
          : 'Не удалось отправить код',
      )

    } finally {

      setSubmitting(false)
    }
  }


  async function handleVerifyCode(
    codeValue?: string,
  ) {

    const normalizedCode =
      (
        codeValue ??
        code
      ).replace(
        /\D/g,
        '',
      )

    if (
      normalizedCode.length !== 6
    ) {

      setLocalError(
        'Введите 6 цифр из письма',
      )

      return
    }

    try {

      setSubmitting(true)
      setLocalError(null)

      await onVerifyCode(
        email,
        normalizedCode,
      )

    } catch (verifyError) {

      console.error(
        'Failed to verify email code:',
        verifyError,
      )

      setLocalError(
        'Неверный или просроченный код',
      )

    } finally {

      setSubmitting(false)
    }
  }


  async function handleResendCode() {

    if (
      retryAfter > 0 ||
      submitting
    ) {
      return
    }

    try {

      setSubmitting(true)
      setLocalError(null)

      await onRequestCode(
        email,
      )

      setRetryAfter(
        60,
      )

    } catch (requestError) {

      console.error(
        'Failed to resend email code:',
        requestError,
      )

      setLocalError(
        requestError instanceof Error
          ? requestError.message
          : 'Не удалось отправить код повторно',
      )

    } finally {

      setSubmitting(false)
    }
  }


  function handleBackToEmail() {

    setStep(
      'email',
    )

    setCode(
      '',
    )

    setLocalError(
      null,
    )
  }


  const visibleError =
    localError ?? error


  return (
    <div
      className="app"
      style={{
        minHeight: '100dvh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px 18px',
        boxSizing: 'border-box',
      }}
    >

      <div
        style={{
          width: '100%',
          maxWidth: 430,
        }}
      >

        <div
          style={{
            textAlign: 'center',
            marginBottom: 28,
          }}
        >

          <picture>

            <img
              src={logoLight}
              alt="JustVPN"
              className="brand-logo brand-logo-light"
              style={{
                maxWidth: 220,
                margin: '0 auto',
              }}
            />

            <img
              src={logoDark}
              alt="JustVPN"
              className="brand-logo brand-logo-dark"
              style={{
                maxWidth: 220,
                margin: '0 auto',
              }}
            />

          </picture>

          <div
            style={{
              marginTop: 10,
              opacity: 0.7,
              fontSize: 14,
            }}
          >
            Защита вашего подключения
          </div>

        </div>


        <div
          style={{
            padding: 24,
            borderRadius: 24,
            background:
              'var(--card-bg, rgba(255,255,255,0.08))',
            boxShadow:
              '0 18px 60px rgba(0,0,0,0.12)',
          }}
        >

          {step === 'email' ? (
            <>

              <div
                style={{
                  fontSize: 24,
                  fontWeight: 800,
                  marginBottom: 8,
                }}
              >
                Вход в JustVPN
              </div>

              <div
                style={{
                  opacity: 0.7,
                  lineHeight: 1.5,
                  marginBottom: 22,
                }}
              >
                Введите email. Мы отправим
                одноразовый код для входа.
              </div>


              <label
                style={{
                  display: 'block',
                  fontSize: 13,
                  fontWeight: 600,
                  marginBottom: 8,
                }}
              >
                Email
              </label>

              <input
                type="email"
                inputMode="email"
                autoComplete="email"
                value={email}
                disabled={submitting}
                placeholder="name@example.com"
                onChange={(event) => {
                  setEmail(
                    event.target.value,
                  )
                  setLocalError(null)
                }}
                onKeyDown={(event) => {
                  if (
                    event.key === 'Enter' &&
                    !submitting
                  ) {
                    void handleRequestCode()
                  }
                }}
                style={{
                  width: '100%',
                  boxSizing: 'border-box',
                  border: '1px solid rgba(128,128,128,0.25)',
                  borderRadius: 14,
                  padding: '14px 16px',
                  fontSize: 16,
                  outline: 'none',
                  background: 'transparent',
                  color: 'inherit',
                }}
              />


              {visibleError && (
                <div
                  style={{
                    marginTop: 12,
                    fontSize: 13,
                    lineHeight: 1.4,
                    color: '#e05252',
                  }}
                >
                  {visibleError}
                </div>
              )}


              <button
                className="primary-button"
                disabled={submitting}
                onClick={() => {
                  void handleRequestCode()
                }}
                style={{
                  width: '100%',
                  marginTop: 18,
                }}
              >
                {submitting
                  ? 'Отправляем...'
                  : 'Получить код'
                }

                <span>
                  →
                </span>
              </button>

            </>
          ) : (
            <>

              <button
                type="button"
                onClick={
                  handleBackToEmail
                }
                disabled={submitting}
                style={{
                  border: 0,
                  padding: 0,
                  marginBottom: 18,
                  background: 'transparent',
                  color: 'inherit',
                  cursor: 'pointer',
                  opacity: 0.75,
                  fontSize: 14,
                }}
              >
                ← Изменить email
              </button>


              <div
                style={{
                  fontSize: 24,
                  fontWeight: 800,
                  marginBottom: 8,
                }}
              >
                Введите код
              </div>

              <div
                style={{
                  opacity: 0.7,
                  lineHeight: 1.5,
                  marginBottom: 22,
                }}
              >
                Мы отправили 6-значный код на
                {' '}
                <strong>
                  {email}
                </strong>
              </div>


              <input
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                maxLength={6}
                value={code}
                disabled={submitting}
                placeholder="000000"
                onChange={(event) => {

                  const value =
                    event.target.value
                      .replace(
                        /\D/g,
                        '',
                      )
                      .slice(
                        0,
                        6,
                      )

                  setCode(
                    value,
                  )

                  setLocalError(
                    null,
                  )

                  if (
                    value.length === 6 &&
                    !submitting
                  ) {

                    window.setTimeout(
                      () => {
                        void handleVerifyCode(
                          value,
                        )
                      },
                      100,
                    )
                  }
                }}
                onKeyDown={(event) => {
                  if (
                    event.key === 'Enter' &&
                    code.length === 6 &&
                    !submitting
                  ) {
                    void handleVerifyCode()
                  }
                }}
                style={{
                  width: '100%',
                  boxSizing: 'border-box',
                  border: '1px solid rgba(128,128,128,0.25)',
                  borderRadius: 14,
                  padding: '15px 16px',
                  fontSize: 26,
                  fontWeight: 800,
                  letterSpacing: 8,
                  textAlign: 'center',
                  outline: 'none',
                  background: 'transparent',
                  color: 'inherit',
                }}
              />


              {visibleError && (
                <div
                  style={{
                    marginTop: 12,
                    fontSize: 13,
                    lineHeight: 1.4,
                    color: '#e05252',
                  }}
                >
                  {visibleError}
                </div>
              )}


              <button
                className="primary-button"
                disabled={
                  submitting ||
                  code.length !== 6
                }
                onClick={() => {
                  void handleVerifyCode()
                }}
                style={{
                  width: '100%',
                  marginTop: 18,
                }}
              >
                {submitting
                  ? 'Проверяем...'
                  : 'Войти'
                }

                <span>
                  →
                </span>
              </button>


              <button
                type="button"
                disabled={
                  submitting ||
                  retryAfter > 0
                }
                onClick={() => {
                  void handleResendCode()
                }}
                style={{
                  width: '100%',
                  border: 0,
                  padding: '14px 8px 0',
                  background: 'transparent',
                  color: 'inherit',
                  cursor:
                    retryAfter > 0
                      ? 'default'
                      : 'pointer',
                  opacity:
                    retryAfter > 0
                      ? 0.55
                      : 0.8,
                  fontSize: 14,
                }}
              >
                {retryAfter > 0
                  ? `Отправить повторно через ${retryAfter} сек.`
                  : 'Отправить код повторно'
                }
              </button>

            </>
          )}

        </div>


        <div
          style={{
            textAlign: 'center',
            marginTop: 18,
            fontSize: 12,
            opacity: 0.55,
            lineHeight: 1.5,
          }}
        >
          Продолжая, вы подтверждаете вход
          в свой аккаунт JustVPN.
        </div>

      </div>

    </div>
  )
}

export default EmailAuthScreen
