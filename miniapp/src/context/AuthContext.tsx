import {
    createContext,
    useContext,
    useEffect,
    useState,
    type ReactNode,
} from 'react'

import { loginWithTelegram } from '../api/auth'
import { getCurrentUser } from '../api/user'

import type { UserResponse } from '../api/user'


type AuthContextValue = {
    user: UserResponse | null
    loading: boolean
    error: string | null
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


    useEffect(() => {

        async function initializeAuth() {

            try {

                setLoading(true)
                setError(null)

                await loginWithTelegram()

                const currentUser =
                    await getCurrentUser()

                setUser(currentUser)

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

            } finally {

                setLoading(false)

            }
        }


        initializeAuth()

    }, [])


    return (
        <AuthContext.Provider
            value={{
                user,
                loading,
                error,
            }}
        >
            {children}
        </AuthContext.Provider>
    )
}


export function useAuth(): AuthContextValue {

    const context =
        useContext(AuthContext)

    if (!context) {

        throw new Error(
            'useAuth must be used inside AuthProvider',
        )

    }

    return context
}