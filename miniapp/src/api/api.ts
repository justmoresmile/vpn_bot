const API_BASE_URL =
    'https://exactly-sector-tide-tobago.trycloudflare.com/api/v1/health'

export async function apiRequest<T>(
    path: string,
    options: RequestInit = {},
): Promise<T> {
    const token = localStorage.getItem('access_token')

    const headers = new Headers(options.headers)

    headers.set('Content-Type', 'application/json')

    if (token) {
        headers.set(
            'Authorization',
            `Bearer ${token}`,
        )
    }

    const response = await fetch(
        `${API_BASE_URL}${path}`,
        {
            ...options,
            headers,
        },
    )

    if (!response.ok) {
        let detail = `API error: ${response.status}`

        try {
            const data = await response.json()

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