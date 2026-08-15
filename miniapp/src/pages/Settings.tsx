import { useTheme } from '../theme/ThemeContext'
import { themes } from '../theme/themes'
import justfastvpnIcon from '../assets/justfastvpn-icon.png'

type SettingsProps = {
    onClose: () => void
}

function Settings({ onClose }: SettingsProps) {
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

                <h2>Тема JustVPN</h2>

                <div className="theme-grid">

                    {themes.map((item) => (
                        <button
                            key={item.name}
                            className={`theme-card ${theme === item.name
                                ? 'selected'
                                : ''
                                }`}
                            onClick={() =>
                                setTheme(item.name)
                            }
                        >
                            <span
                                className="theme-color"
                                style={{
                                    background: item.accent,
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

            </section>

            <section className="settings-section">

                <h2>Свой цвет</h2>

                <div className="custom-color-card">

                    <div>
                        <strong>
                            Акцентный цвет
                        </strong>

                        <span>
                            Выберите любой цвет
                        </span>
                    </div>

                    <label className="color-picker">

                        <span
                            style={{
                                background: accent,
                            }}
                        />

                        <input
                            type="color"
                            value={accent}
                            onChange={(event) =>
                                setAccent(
                                    event.target.value,
                                )
                            }
                        />

                    </label>

                </div>

            </section>

            <section className="settings-section">

                <div className="setting-row">

                    <div>
                        <h2>Прозрачность</h2>

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
                            Number(event.target.value),
                        )
                    }
                    style={{
                        accentColor: accent,
                    }}
                />

            </section>

            <section className="settings-section">

                <h2>Режим</h2>

                <div className="mode-selector">

                    <button
                        className={
                            mode === 'light'
                                ? 'active'
                                : ''
                        }
                        onClick={() =>
                            setMode('light')
                        }
                    >
                        ☀️
                        <span>Светлая</span>
                    </button>

                    <button
                        className={
                            mode === 'dark'
                                ? 'active'
                                : ''
                        }
                        onClick={() =>
                            setMode('dark')
                        }
                    >
                        🌙
                        <span>Тёмная</span>
                    </button>

                </div>

            </section>

            <div className="settings-preview">

                <div className="preview-label">
                    Предпросмотр
                </div>

                <div className="preview-card">

                    <div className="preview-icon">
                        <img
                            src={justfastvpnIcon}
                            alt="JustFastVPN"
                        />
                    </div>

                    <div>
                        <strong>JustFastVPN</strong>
                        <span>Интерфейс настроен</span>
                    </div>

                    <div className="preview-status">
                        Активен
                    </div>

                </div>

            </div>
            <button
                className="settings-apply-button"
                onClick={onClose}
            >
                Применить
                <span>✓</span>
            </button>
        </div>
    )
}



export default Settings