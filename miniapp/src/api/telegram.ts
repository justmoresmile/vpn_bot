import WebApp from '@twa-dev/sdk'

export function initTelegramWebApp() {
    WebApp.ready()
    WebApp.expand()
}

export function getTelegramInitData(): string {
    console.log('========== TELEGRAM DEBUG ==========')

    console.log(
        'WebApp.initData:',
        WebApp.initData,
    )

    console.log(
        'WebApp.initDataUnsafe:',
        WebApp.initDataUnsafe,
    )

    console.log(
        'WebApp.version:',
        WebApp.version,
    )

    console.log(
        'WebApp.platform:',
        WebApp.platform,
    )

    console.log(
        'WebApp.colorScheme:',
        WebApp.colorScheme,
    )

    console.log(
        'Browser URL:',
        window.location.href,
    )

    console.log(
        'Browser hash:',
        window.location.hash,
    )

    console.log(
        'Browser search:',
        window.location.search,
    )

    console.log(
        '====================================',
    )

    return WebApp.initData
}

export function getTelegramUser() {
    return WebApp.initDataUnsafe?.user ?? null
}