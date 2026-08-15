import { apiRequest } from './api'

export type UserResponse = {
    id: number
    telegram_id: number
    username: string | null
    first_name: string | null
    is_admin: boolean
}

export async function getCurrentUser(): Promise<UserResponse> {
    return apiRequest<UserResponse>(
        '/user/me',
    )
}