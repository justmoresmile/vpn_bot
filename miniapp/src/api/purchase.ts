import { apiRequest } from './api'


export type PurchaseRequest = {
    days: number
    subscription_id?: number | null
}


export type PurchaseResponse = {
    payment_id: number
    provider_payment_id: string | null
    confirmation_url: string | null
    amount: number
    currency: string
    status: string
}


export async function createPurchase(
    days: number,
    subscriptionId: number | null = null,
): Promise<PurchaseResponse> {

    return apiRequest<PurchaseResponse>(
        '/purchase/',
        {
            method: 'POST',
            body: JSON.stringify({
                days,
                subscription_id: subscriptionId,
            }),
        },
    )
}