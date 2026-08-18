import WebApp from '@twa-dev/sdk'


export function initTelegramWebApp() {
    WebApp.ready()
    WebApp.expand()
}


export function getTelegramInitData(): string {
    return WebApp.initData
}


export function getTelegramUser() {
    return WebApp.initDataUnsafe?.user ?? null
}

export function getTelegramStartParam(): string | null {
    return (
        WebApp.initDataUnsafe?.start_param ??
        new URLSearchParams(
            window.location.search,
        ).get('tgWebAppStartParam')
    )
}