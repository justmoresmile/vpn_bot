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
    mode: ColorMode

    setTheme: (theme: ThemeName) => void
    setAccent: (accent: string) => void
    setMode: (mode: ColorMode) => void
}

const ThemeContext = createContext<ThemeContextValue | null>(null)

const STORAGE_KEY = 'justvpn-theme'


function hexToRgba(
    hex: string,
    alpha: number,
) {
    let value =
        hex.replace('#', '')

    if (value.length === 3) {
        value =
            value
                .split('')
                .map((char) => char + char)
                .join('')
    }

    if (value.length !== 6) {
        return `rgba(0, 0, 0, ${alpha})`
    }

    const red =
        parseInt(
            value.slice(0, 2),
            16,
        )

    const green =
        parseInt(
            value.slice(2, 4),
            16,
        )

    const blue =
        parseInt(
            value.slice(4, 6),
            16,
        )

    return `rgba(
        ${red},
        ${green},
        ${blue},
        ${alpha}
    )`
}

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

    const setMode = (value: ColorMode) => {
        setModeState(value)

        localStorage.setItem(
            `${STORAGE_KEY}-mode`,
            value,
        )
    }

    useEffect(() => {

        const root = document.documentElement

        /*
         * Основной цвет остаётся насыщенным.
         * Ползунок влияет только на мягкие
         * акцентные фоны и подсветку.
         */
        const softAlpha = 0.28
        const lightAlpha = 0.37


        root.style.setProperty(
            '--accent',
            accent,
        )

        root.style.setProperty(
            '--accent-soft',
            hexToRgba(
                accent,
                softAlpha,
            ),
        )

        root.style.setProperty(
            '--accent-light',
            hexToRgba(
                accent,
                lightAlpha,
            ),
        )

        root.dataset.theme = mode
    }, [accent, mode])

    return (
        <ThemeContext.Provider
            value={{
                theme,
                accent,
                mode,
                setTheme,
                setAccent,
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