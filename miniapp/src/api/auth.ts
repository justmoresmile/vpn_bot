import { apiRequest } from './api'
import {
    getTelegramInitData,
} from './telegram'


export type AuthResponse = {
    access_token: string
    token_type: string
}


export type EmailCodeRequestResponse = {
    success: boolean
    expires_in: number
}


/**
 * Вход через Telegram Mini App.
 */
export async function loginWithTelegram(): Promise<AuthResponse> {

    const initData =
        getTelegramInitData()

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


/**
 * Запрос кода входа на email.
 */
export async function requestEmailCode(
    email: string,
): Promise<EmailCodeRequestResponse> {

    return apiRequest<EmailCodeRequestResponse>(
        '/auth/email/request-code',
        {
            method: 'POST',
            body: JSON.stringify({
                email,
            }),
        },
    )
}


/**
 * Проверка email-кода и получение JWT.
 */
export async function verifyEmailCode(
    email: string,
    code: string,
): Promise<AuthResponse> {

    const response =
        await apiRequest<AuthResponse>(
            '/auth/email/verify-code',
            {
                method: 'POST',
                body: JSON.stringify({
                    email,
                    code,
                }),
            },
        )

    localStorage.setItem(
        'access_token',
        response.access_token,
    )

    return response
}


/**
 * Есть ли уже сохранённый JWT.
 */
export function hasAccessToken(): boolean {

    return Boolean(
        localStorage.getItem(
            'access_token',
        ),
    )
}


/**
 * Выход из аккаунта.
 */
export function logout(): void {

    localStorage.removeItem(
        'access_token',
    )
}