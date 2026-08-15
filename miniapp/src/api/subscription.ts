import { apiRequest } from './api'

export type Subscription = {
    id: number
    protocol: string
    status: string
    expires_at: string
    client_email: string | null
}

export type SubscriptionDetails = {
    id: number
    user_id: number
    protocol: string
    status: string
    expires_at: string
    client_email: string
}

export type ConfigResponse = {
    config: string
}

export type RenewResponse = {
    id: number
    status: string
    expires_at: string
}

export async function getSubscriptions(): Promise<Subscription[]> {
    return apiRequest<Subscription[]>(
        '/user/me/subscriptions',
    )
}

export async function getSubscription(
    subscriptionId: number,
): Promise<SubscriptionDetails> {
    return apiRequest<SubscriptionDetails>(
        `/subscription/${subscriptionId}`,
    )
}

export async function getSubscriptionConfig(
    subscriptionId: number,
): Promise<ConfigResponse> {
    return apiRequest<ConfigResponse>(
        `/subscription/${subscriptionId}/config`,
    )
}

export async function getSubscriptionLink(
    subscriptionId: number,
): Promise<ConfigResponse> {
    return apiRequest<ConfigResponse>(
        `/subscription/${subscriptionId}/link`,
    )
}

export async function renewSubscription(
    subscriptionId: number,
    days = 30,
): Promise<RenewResponse> {
    return apiRequest<RenewResponse>(
        `/subscription/${subscriptionId}/renew?days=${days}`,
        {
            method: 'POST',
        },
    )
}

export async function getSubscriptionQr(
    subscriptionId: number,
): Promise<Blob> {
    const token = localStorage.getItem('access_token')

    const response = await fetch(
        `http://127.0.0.1:8000/api/v1/subscription/${subscriptionId}/qr`,
        {
            headers: token
                ? {
                    Authorization: `Bearer ${token}`,
                }
                : {},
        },
    )

    if (!response.ok) {
        throw new Error(
            `API error: ${response.status}`,
        )
    }

    return response.blob()
}

export async function downloadSubscriptionFile(
    subscriptionId: number,
): Promise<Blob> {
    const token = localStorage.getItem('access_token')

    const response = await fetch(
        `http://127.0.0.1:8000/api/v1/subscription/${subscriptionId}/file`,
        {
            headers: token
                ? {
                    Authorization: `Bearer ${token}`,
                }
                : {},
        },
    )

    if (!response.ok) {
        throw new Error(
            `API error: ${response.status}`,
        )
    }

    return response.blob()
}