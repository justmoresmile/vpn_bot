import { apiRequest } from './api'
import {
    getTelegramInitData,
} from './telegram'

export type AuthResponse = {
    access_token: string
    token_type: string
}

export async function loginWithTelegram(): Promise<AuthResponse> {
    const initData = getTelegramInitData()

    if (!initData) {
        throw new Error(
            'Telegram initData отсутствует',
        )
    }

    const response =
        await apiRequest<AuthResponse>(
            '/auth/telegram',
            {
                method: 'POST',
                body: JSON.stringify({
                    init_data: initData,
                }),
            },
        )

    localStorage.setItem(
        'access_token',
        response.access_token,
    )

    return response
}