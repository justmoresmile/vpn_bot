import {
    apiBlobRequest,
    apiRequest,
} from './api'


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

    return apiBlobRequest(
        `/subscription/${subscriptionId}/qr`,
    )
}


export async function downloadSubscriptionFile(
    subscriptionId: number,
): Promise<Blob> {

    return apiBlobRequest(
        `/subscription/${subscriptionId}/file`,
    )
}
