import {
    useRef,
} from 'react'

import { useTheme } from '../theme/ThemeContext'
import { themes } from '../theme/themes'


type SettingsProps = {
    onClose: () => void
}


function Settings({
    onClose,
}: SettingsProps) {

    const {
        theme,
        accent,
        opacity,
        mode,
        setTheme,
        setAccent,
        setOpacity,
        setMode,
    } = useTheme()

    const colorBarRef =
        useRef<HTMLDivElement | null>(null)


    function hsvToHex(
        hue: number,
        saturation: number,
        value: number,
    ) {

        const chroma =
            value * saturation

        const section =
            hue / 60

        const x =
            chroma
            * (
                1
                - Math.abs(
                    section % 2 - 1,
                )
            )

        let red = 0
        let green = 0
        let blue = 0

        if (section >= 0 && section < 1) {
            red = chroma
            green = x
        } else if (
            section >= 1
            && section < 2
        ) {
            red = x
            green = chroma
        } else if (
            section >= 2
            && section < 3
        ) {
            green = chroma
            blue = x
        } else if (
            section >= 3
            && section < 4
        ) {
            green = x
            blue = chroma
        } else if (
            section >= 4
            && section < 5
        ) {
            red = x
            blue = chroma
        } else {
            red = chroma
            blue = x
        }

        const match =
            value - chroma

        const toHex = (
            channel: number,
        ) =>
            Math.round(
                (channel + match) * 255,
            )
                .toString(16)
                .padStart(2, '0')

        return `#${
            toHex(red)
        }${
            toHex(green)
        }${
            toHex(blue)
        }`
    }


    function selectColor(
        clientX: number,
    ) {

        const bar =
            colorBarRef.current

        if (!bar) {
            return
        }

        const rect =
            bar.getBoundingClientRect()

        const position =
            Math.max(
                0,
                Math.min(
                    1,
                    (clientX - rect.left)
                    / rect.width,
                ),
            )

        const hue =
            position * 360

        setAccent(
            hsvToHex(
                hue,
                1,
                1,
            ),
        )
    }

    return (
        <div className="settings-page">

            <div className="settings-header">

                <button
                    className="back-button"
                    onClick={onClose}
                >
                    ←
                </button>

                <div>

                    <div className="settings-title">
                        Оформление
                    </div>

                    <div className="settings-subtitle">
                        Настройте JustVPN под себя
                    </div>

                </div>

            </div>


            <section className="settings-section">

                <h2>
                    Тема JustVPN
                </h2>

                <div className="theme-grid">

                    {themes.map((item) => (

                        <button
                            key={item.name}
                            className={`theme-card ${
                                theme === item.name
                                    ? 'selected'
                                    : ''
                            }`}
                            onClick={() =>
                                setTheme(
                                    item.name,
                                )
                            }
                        >

                            <span
                                className="theme-color"
                                style={{
                                    background:
                                        item.accent,
                                }}
                            />

                            <span className="theme-name">
                                {item.label}
                            </span>

                            {theme === item.name && (

                                <span className="theme-check">
                                    ✓
                                </span>

                            )}

                        </button>

                    ))}

                </div>

                <div
                    style={{
                        marginTop: 18,
                    }}
                >

                    <div
                        className="setting-description"
                        style={{
                            marginBottom: 10,
                        }}
                    >
                        Свой цвет
                    </div>

                    <div
                        ref={colorBarRef}
                        onPointerDown={(event) => {

                            event.currentTarget
                                .setPointerCapture(
                                    event.pointerId,
                                )

                            selectColor(
                                event.clientX,
                            )
                        }}
                        onPointerMove={(event) => {

                            if (
                                event.currentTarget
                                    .hasPointerCapture(
                                        event.pointerId,
                                    )
                            ) {
                                selectColor(
                                    event.clientX,
                                )
                            }
                        }}
                        onPointerUp={(event) => {

                            if (
                                event.currentTarget
                                    .hasPointerCapture(
                                        event.pointerId,
                                    )
                            ) {
                                event.currentTarget
                                    .releasePointerCapture(
                                        event.pointerId,
                                    )
                            }
                        }}
                        style={{
                            width: '100%',
                            height: 34,
                            borderRadius: 17,
                            cursor: 'pointer',
                            touchAction: 'none',
                            background: `
                                linear-gradient(
                                    90deg,
                                    #ff0000 0%,
                                    #ffff00 16.66%,
                                    #00ff00 33.33%,
                                    #00ffff 50%,
                                    #0000ff 66.66%,
                                    #ff00ff 83.33%,
                                    #ff0000 100%
                                )
                            `,
                            boxShadow:
                                'inset 0 0 0 1px rgba(127,127,127,0.18)',
                            userSelect: 'none',
                        }}
                    />

                </div>


            </section>


            <section className="settings-section">

                <div className="setting-row">

                    <div>

                        <h2>
                            Прозрачность
                        </h2>

                        <span className="setting-description">
                            Прозрачность акцентных элементов
                        </span>

                    </div>

                    <strong>
                        {opacity}%
                    </strong>

                </div>

                <input
                    className="opacity-slider"
                    type="range"
                    min="20"
                    max="100"
                    value={opacity}
                    onChange={(event) =>
                        setOpacity(
                            Number(
                                event.target.value,
                            ),
                        )
                    }
                    style={{
                        accentColor:
                            accent,
                    }}
                />

            </section>


            <section className="settings-section">

                <h2>
                    Режим
                </h2>

                <div className="mode-selector">

                    <button
                        className={
                            mode === 'light'
                                ? 'active'
                                : ''
                        }
                        onClick={() =>
                            setMode(
                                'light',
                            )
                        }
                    >
                        ☀️
                        <span>
                            Светлая
                        </span>
                    </button>

                    <button
                        className={
                            mode === 'dark'
                                ? 'active'
                                : ''
                        }
                        onClick={() =>
                            setMode(
                                'dark',
                            )
                        }
                    >
                        🌙
                        <span>
                            Тёмная
                        </span>
                    </button>

                </div>

            </section>








        </div>
    )
}


export default Settings