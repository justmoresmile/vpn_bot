export interface TelegramWebApp {
    initData: string

    initDataUnsafe: {
        user?: {
            id: number
            username?: string
            first_name?: string
            last_name?: string
            language_code?: string
            is_premium?: boolean
        }
    }

    ready(): void
    expand(): void
}

declare global {
    interface Window {
        Telegram?: {
            WebApp: TelegramWebApp
        }
    }
}