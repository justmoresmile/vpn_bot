import {
    useRef,
    useState,
} from 'react'

import { useTheme } from '../theme/ThemeContext'
import { useAuth } from '../context/AuthContext'
import { themes } from '../theme/themes'





type AccountPage =
    | 'menu'
    | 'profile'
    | 'appearance'


type SettingsProps = {
    onClose: () => void
}


function Settings({
    onClose,
}: SettingsProps) {

    const {
        theme,
        setTheme,
        setAccent,
    } = useTheme()

    const colorBarRef =
        useRef<HTMLDivElement | null>(null)

    const [
        accountPage,
        setAccountPage,
    ] = useState<AccountPage>('menu')

    const {
        user,
    } = useAuth()



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
        <div
            className="settings-page"
            style={{
                display: 'flex',
                flexDirection: 'column',
            }}
        >

            <div
                className="settings-header"
                style={{
                    order: 0,
                }}
            >

                <button
                    className="back-button"
                    onClick={() => {
                        if (accountPage === 'menu') {
                            onClose()
                            return
                        }

                        setAccountPage('menu')
                    }}
                >
                    ←
                </button>

                <div>

                    <div className="settings-title">
                        {accountPage === 'profile'
                            ? 'Профиль'
                            : accountPage === 'appearance'
                                ? 'Оформление'
                                : 'Аккаунт'}
                    </div>

                    <div className="settings-subtitle">
                        {accountPage === 'profile'
                            ? 'Данные вашего аккаунта'
                            : accountPage === 'appearance'
                                ? 'Внешний вид JustVPN'
                                : 'Профиль и настройки JustVPN'}
                    </div>

                </div>

            </div>


            {accountPage === 'menu' && (

                <section
                    className="settings-section"
                    style={{
                        padding: 0,
                        overflow: 'hidden',
                    }}
                >

                    <button
                        type="button"
                        onClick={() =>
                            setAccountPage('profile')
                        }
                        style={{
                            width: '100%',
                            minHeight: 64,
                            padding: '0 16px',
                            border: 0,
                            borderBottom:
                                '1px solid rgba(127,127,127,0.14)',
                            background: 'transparent',
                            color: 'inherit',
                            display: 'flex',
                            alignItems: 'center',
                            textAlign: 'left',
                            cursor: 'pointer',
                        }}
                    >

                        <div
                            style={{
                                flex: 1,
                                minWidth: 0,
                            }}
                        >
                            <div
                                style={{
                                    fontSize: 16,
                                    fontWeight: 600,
                                }}
                            >
                                Профиль
                            </div>

                            <div
                                className="setting-description"
                                style={{
                                    marginTop: 2,
                                }}
                            >
                                Telegram и Email
                            </div>
                        </div>

                        <div
                            style={{
                                fontSize: 24,
                                opacity: 0.35,
                            }}
                        >
                            ›
                        </div>

                    </button>


                    <button
                        type="button"
                        onClick={() =>
                            setAccountPage('appearance')
                        }
                        style={{
                            width: '100%',
                            minHeight: 64,
                            padding: '0 16px',
                            border: 0,
                            background: 'transparent',
                            color: 'inherit',
                            display: 'flex',
                            alignItems: 'center',
                            textAlign: 'left',
                            cursor: 'pointer',
                        }}
                    >

                        <div
                            style={{
                                flex: 1,
                                minWidth: 0,
                            }}
                        >
                            <div
                                style={{
                                    fontSize: 16,
                                    fontWeight: 600,
                                }}
                            >
                                Оформление
                            </div>

                            <div
                                className="setting-description"
                                style={{
                                    marginTop: 2,
                                }}
                            >
                                Тема, цвет и режим
                            </div>
                        </div>

                        <div
                            style={{
                                fontSize: 24,
                                opacity: 0.35,
                            }}
                        >
                            ›
                        </div>

                    </button>

                </section>

            )}


            <section
                className="settings-section"
                style={{
                    paddingTop: 4,
                    display:
                        accountPage === 'profile'
                            ? undefined
                            : 'none',
                }}
            >

                <div
                    className="setting-description"
                    style={{
                        marginBottom: 8,
                        textTransform: 'uppercase',
                        letterSpacing: '0.06em',
                        fontSize: 12,
                        fontWeight: 600,
                    }}
                >
                    Профиль
                </div>

                <div
                    style={{
                        padding: '10px 0 18px',
                    }}
                >

                    <div
                        style={{
                            fontSize: 20,
                            fontWeight: 700,
                        }}
                    >
                        {user?.first_name
                            || user?.username
                            || 'Пользователь'}
                    </div>

                </div>


                <div
                    style={{
                        borderTop:
                            '1px solid rgba(127,127,127,0.14)',
                    }}
                >

                    <div
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            gap: 16,
                            minHeight: 52,
                            borderBottom:
                                '1px solid rgba(127,127,127,0.14)',
                        }}
                    >

                        <div
                            style={{
                                fontWeight: 500,
                                flexShrink: 0,
                            }}
                        >
                            Telegram
                        </div>

                        <div
                            className="setting-description"
                            style={{
                                textAlign: 'right',
                                wordBreak: 'break-all',
                            }}
                        >
                            {user?.telegram_id
                                ? user.telegram_id
                                : 'Не привязан'}
                        </div>

                    </div>


                    <div
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            gap: 16,
                            minHeight: 52,
                            borderBottom:
                                '1px solid rgba(127,127,127,0.14)',
                        }}
                    >

                        <div
                            style={{
                                fontWeight: 500,
                                flexShrink: 0,
                            }}
                        >
                            Email
                        </div>

                        <div
                            className="setting-description"
                            style={{
                                textAlign: 'right',
                                wordBreak: 'break-word',
                            }}
                        >
                            {user?.email
                                ? user.email
                                : 'Не привязан'}
                        </div>

                    </div>

                </div>

            </section>




            <section
                className="settings-section"
                style={{
                    display:
                        accountPage === 'appearance'
                            ? undefined
                            : 'none',
                }}
            >

                <h2>
                    Оформление
                </h2>

                <div
                    className="setting-description"
                    style={{
                        marginBottom: 18,
                    }}
                >
                    Тема, цвет и внешний вид приложения
                </div>

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





        </div>
    )
}


export default Settings
