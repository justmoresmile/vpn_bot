import {
    createContext,
    useContext,
    useEffect,
    useState,
    type ReactNode,
} from 'react'

import {
    attachEmail,
    hasAccessToken,
    loginWithTelegram,
    linkEmailWithTelegram,
    logout as logoutApi,
    requestEmailCode,
    verifyEmailCode,
} from '../api/auth'

import { getCurrentUser } from '../api/user'
import { getTelegramInitData } from '../api/telegram'

import type { UserResponse } from '../api/user'


type AuthMode =
    | 'loading'
    | 'authenticated'
    | 'choice'
    | 'email'


type AuthContextValue = {
    user: UserResponse | null
    loading: boolean
    error: string | null
    mode: AuthMode

    continueWithTelegram: () => Promise<void>
    useEmailLogin: () => void

    requestEmailCode: (
        email: string,
    ) => Promise<number>

    verifyEmailCode: (
        email: string,
        code: string,
    ) => Promise<void>

    attachEmail: (
        email: string,
        code: string,
    ) => Promise<void>

    logout: () => void
}


const AuthContext =
    createContext<AuthContextValue | undefined>(
        undefined,
    )


type AuthProviderProps = {
    children: ReactNode
}


export function AuthProvider({
    children,
}: AuthProviderProps) {

    const [user, setUser] =
        useState<UserResponse | null>(null)

    const [loading, setLoading] =
        useState(true)

    const [error, setError] =
        useState<string | null>(null)

    const [mode, setMode] =
        useState<AuthMode>('loading')


    async function loadCurrentUser() {

        const currentUser =
            await getCurrentUser()

        setUser(
            currentUser
        )

        setMode(
            'authenticated'
        )
    }


    useEffect(() => {

        async function initializeAuth() {

            try {

                setLoading(true)
                setError(null)

                // ==========================================
                // 1. Уже есть JWT
                // ==========================================

                if (
                    hasAccessToken()
                ) {

                    try {

                        await loadCurrentUser()

                        return

                    } catch (error) {

                        console.warn(
                            'Stored token is invalid:',
                            error,
                        )

                        logoutApi()
                    }
                }


                // ==========================================
                // 2. Telegram Mini App
                // ==========================================

                const initData =
                    getTelegramInitData()

                if (
                    initData
                ) {

                    setMode(
                        'choice'
                    )

                    return
                }


                // ==========================================
                // 3. Обычный браузер
                // ==========================================

                setMode(
                    'email'
                )

            } catch (error) {

                console.error(
                    'Authentication failed:',
                    error,
                )

                setError(
                    error instanceof Error
                        ? error.message
                        : 'Authentication failed',
                )

                setMode(
                    'email'
                )

            } finally {

                setLoading(false)
            }
        }


        initializeAuth()

    }, [])


    async function handleContinueWithTelegram() {

        try {

            setLoading(true)
            setError(null)

            await loginWithTelegram()

            await loadCurrentUser()

        } catch (error) {

            console.error(
                'Telegram authentication failed:',
                error,
            )

            const message =
                error instanceof Error
                    ? error.message
                    : 'Не удалось войти через Telegram'

            setError(
                message
            )

            throw error

        } finally {

            setLoading(false)
        }
    }


    function handleUseEmailLogin() {

        setError(
            null
        )

        setMode(
            'email'
        )
    }


    async function handleRequestEmailCode(
        email: string,
    ): Promise<number> {

        setError(null)

        const response =
            await requestEmailCode(
                email,
            )

        return response.expires_in
    }


    async function handleVerifyEmailCode(
        email: string,
        code: string,
    ): Promise<void> {

        try {

            setLoading(true)
            setError(null)

            const initData =
                getTelegramInitData()

            if (initData) {

                await linkEmailWithTelegram(
                    email,
                    code,
                )

            } else {

                await verifyEmailCode(
                    email,
                    code,
                )
            }

            await loadCurrentUser()

        } catch (error) {

            console.error(
                'Email authentication failed:',
                error,
            )

            const message =
                error instanceof Error
                    ? error.message
                    : 'Не удалось войти'

            setError(
                message
            )

            throw error

        } finally {

            setLoading(false)
        }
    }


    async function handleAttachEmail(
        email: string,
        code: string,
    ): Promise<void> {

        try {

            setLoading(true)
            setError(null)

            await attachEmail(
                email,
                code,
            )

            await loadCurrentUser()

        } catch (error) {

            console.error(
                'Email attach failed:',
                error,
            )

            const message =
                error instanceof Error
                    ? error.message
                    : 'Не удалось привязать email'

            setError(
                message
            )

            throw error

        } finally {

            setLoading(false)
        }
    }


    function handleLogout() {

        logoutApi()

        setUser(
            null
        )

        setError(
            null
        )

        setMode(
            getTelegramInitData()
                ? 'choice'
                : 'email'
        )
    }


    return (
        <AuthContext.Provider
            value={{
                user,
                loading,
                error,
                mode,
                continueWithTelegram:
                    handleContinueWithTelegram,
                useEmailLogin:
                    handleUseEmailLogin,
                requestEmailCode:
                    handleRequestEmailCode,
                verifyEmailCode:
                    handleVerifyEmailCode,
                attachEmail:
                    handleAttachEmail,
                logout:
                    handleLogout,
            }}
        >
            {children}
        </AuthContext.Provider>
    )
}


export function useAuth(): AuthContextValue {

    const context =
        useContext(
            AuthContext,
        )

    if (!context) {

        throw new Error(
            'useAuth must be used inside AuthProvider',
        )
    }

    return context
}