export const API_BASE_URL =
    'https://s.justfastvpn.ru/api/v1'


function getAuthHeaders(
    headers?: HeadersInit,
): Headers {

    const result =
        new Headers(headers)

    const token =
        localStorage.getItem(
            'access_token',
        )

    if (token) {
        result.set(
            'Authorization',
            `Bearer ${token}`,
        )
    }

    return result
}


export async function apiRequest<T>(
    path: string,
    options: RequestInit = {},
): Promise<T> {

    const headers =
        getAuthHeaders(
            options.headers,
        )

    headers.set(
        'Content-Type',
        'application/json',
    )

    const response =
        await fetch(
            `${API_BASE_URL}${path}`,
            {
                ...options,
                headers,
            },
        )

    if (!response.ok) {

        let detail =
            `API error: ${response.status}`

        try {

            const data =
                await response.json()

            if (data?.detail) {
                detail = data.detail
            }

        } catch {
            // Ответ не JSON
        }

        throw new Error(detail)
    }

    return response.json() as Promise<T>
}


export async function apiBlobRequest(
    path: string,
    options: RequestInit = {},
): Promise<Blob> {

    const headers =
        getAuthHeaders(
            options.headers,
        )

    const response =
        await fetch(
            `${API_BASE_URL}${path}`,
            {
                ...options,
                headers,
            },
        )

    if (!response.ok) {
        throw new Error(
            `API error: ${response.status}`,
        )
    }

    return response.blob()
}
