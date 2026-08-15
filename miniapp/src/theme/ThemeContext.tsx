import {
    createContext,
    useContext,
    useEffect,
    useState,
    type ReactNode,
} from 'react'

import {
    themes,
    type ThemeName,
} from './themes'

type ColorMode = 'light' | 'dark'

type ThemeContextValue = {
    theme: ThemeName
    accent: string
    opacity: number
    mode: ColorMode

    setTheme: (theme: ThemeName) => void
    setAccent: (accent: string) => void
    setOpacity: (opacity: number) => void
    setMode: (mode: ColorMode) => void
}

const ThemeContext = createContext<ThemeContextValue | null>(null)

const STORAGE_KEY = 'justvpn-theme'

export function ThemeProvider({
    children,
}: {
    children: ReactNode
}) {
    const [theme, setThemeState] =
        useState<ThemeName>(() => {
            return (
                localStorage.getItem(
                    `${STORAGE_KEY}-name`,
                ) as ThemeName
            ) || 'classic'
        })

    const [accent, setAccentState] =
        useState<string>(() => {
            return (
                localStorage.getItem(
                    `${STORAGE_KEY}-accent`,
                ) || '#111111'
            )
        })

    const [opacity, setOpacityState] =
        useState<number>(() => {
            const value = localStorage.getItem(
                `${STORAGE_KEY}-opacity`,
            )

            return value
                ? Number(value)
                : 100
        })

    const [mode, setModeState] =
        useState<ColorMode>(() => {
            return (
                localStorage.getItem(
                    `${STORAGE_KEY}-mode`,
                ) as ColorMode
            ) || 'light'
        })

    const setTheme = (value: ThemeName) => {
        setThemeState(value)

        localStorage.setItem(
            `${STORAGE_KEY}-name`,
            value,
        )

        if (value !== 'custom') {
            const selected = themes.find(
                (item) => item.name === value,
            )

            if (selected) {
                setAccentState(selected.accent)

                localStorage.setItem(
                    `${STORAGE_KEY}-accent`,
                    selected.accent,
                )
            }
        }
    }

    const setAccent = (value: string) => {
        setAccentState(value)

        localStorage.setItem(
            `${STORAGE_KEY}-accent`,
            value,
        )

        setThemeState('custom')

        localStorage.setItem(
            `${STORAGE_KEY}-name`,
            'custom',
        )
    }

    const setOpacity = (value: number) => {
        setOpacityState(value)

        localStorage.setItem(
            `${STORAGE_KEY}-opacity`,
            String(value),
        )
    }

    const setMode = (value: ColorMode) => {
        setModeState(value)

        localStorage.setItem(
            `${STORAGE_KEY}-mode`,
            value,
        )
    }

    useEffect(() => {
        const root = document.documentElement

        root.style.setProperty(
            '--accent',
            accent,
        )

        root.style.setProperty(
            '--accent-opacity',
            String(opacity / 100),
        )

        root.dataset.theme = mode
    }, [accent, opacity, mode])

    return (
        <ThemeContext.Provider
            value={{
                theme,
                accent,
                opacity,
                mode,
                setTheme,
                setAccent,
                setOpacity,
                setMode,
            }}
        >
            {children}
        </ThemeContext.Provider>
    )
}

export function useTheme() {
    const context = useContext(ThemeContext)

    if (!context) {
        throw new Error(
            'useTheme must be used inside ThemeProvider',
        )
    }

    return context
}