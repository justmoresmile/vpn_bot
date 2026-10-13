type AuthChoiceScreenProps = {
  error: string | null
  onTelegram: () => Promise<void>
  onEmail: () => void
}

function AuthChoiceScreen({
  error,
  onTelegram,
  onEmail,
}: AuthChoiceScreenProps) {

  return (
    <div
      className="app"
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 20,
        boxSizing: 'border-box',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: 420,
          padding: 24,
          borderRadius: 24,
          background:
            'var(--card-bg, rgba(255,255,255,0.08))',
          boxShadow:
            '0 18px 60px rgba(0,0,0,0.12)',
        }}
      >
        <div
          style={{
            fontSize: 26,
            fontWeight: 800,
            marginBottom: 8,
          }}
        >
          Добро пожаловать в JustVPN
        </div>

        <div
          style={{
            opacity: 0.7,
            lineHeight: 1.5,
            marginBottom: 24,
          }}
        >
          Выберите, как войти в аккаунт.
        </div>

        <button
          className="primary-button"
          style={{
            width: '100%',
          }}
          onClick={() => {
            void onTelegram()
          }}
        >
          Продолжить с Telegram
          <span>→</span>
        </button>

        <div
          style={{
            textAlign: 'center',
            opacity: 0.55,
            fontSize: 13,
            margin: '22px 0 12px',
          }}
        >
          Уже регистрировались по email?
        </div>

        <button
          type="button"
          onClick={onEmail}
          style={{
            width: '100%',
            padding: '14px 16px',
            borderRadius: 14,
            border:
              '1px solid rgba(128,128,128,0.25)',
            background: 'transparent',
            color: 'inherit',
            fontSize: 15,
            fontWeight: 700,
            cursor: 'pointer',
          }}
        >
          Войти по email
        </button>

        {error && (
          <div
            style={{
              marginTop: 16,
              color: '#e05252',
              fontSize: 13,
              lineHeight: 1.4,
            }}
          >
            {error}
          </div>
        )}
      </div>
    </div>
  )
}

export default AuthChoiceScreen
