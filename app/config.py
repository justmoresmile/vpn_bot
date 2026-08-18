
from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:

    # ------------------------------------------------------------------
    # Telegram
    # ------------------------------------------------------------------

    bot_token: str
    admin_id: int
    miniapp_url: str
    # ------------------------------------------------------------------
    # 3x-ui
    # ------------------------------------------------------------------

    xui_api_url: str
    xui_api_token: str

    # ------------------------------------------------------------------
    # VPN
    # ------------------------------------------------------------------

    vpn_host: str
    vpn_name: str
    vpn_country: str
    vpn_wg_dns: str

    # ------------------------------------------------------------------
    # Protocols
    # ------------------------------------------------------------------

    enable_vless: bool

    # ------------------------------------------------------------------
    # Inbounds
    # ------------------------------------------------------------------

    vpn_vless_inbound: int
    wireguard_inbound_id: int

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    database_path: str

    # ------------------------------------------------------------------
    # YooKassa
    # ------------------------------------------------------------------

    yookassa_shop_id: str
    yookassa_secret_key: str
    payment_return_url: str

    # ------------------------------------------------------------------
    # JWT
    # ------------------------------------------------------------------

    jwt_secret: str
    jwt_algorithm: str
    jwt_expire_days: int

    # ------------------------------------------------------------------
    # Backend API
    # ------------------------------------------------------------------

    backend_api_url: str
    backend_api_key: str
    public_subscription_base_url: str

    # ------------------------------------------------------------------
    # Debug
    # ------------------------------------------------------------------

    debug: bool


def require_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Environment variable '{name}' is missing."
        )

    return value


settings = Settings(

    # ------------------------------------------------------------------
    # Telegram
    # ------------------------------------------------------------------

    bot_token=require_env(
        "BOT_TOKEN"
    ),

    admin_id=int(
        os.getenv(
            "ADMIN_ID",
            "0",
        )
    ),

    miniapp_url=require_env(
    "MINIAPP_URL"
    ),

    # ------------------------------------------------------------------
    # 3x-ui
    # ------------------------------------------------------------------

    xui_api_url=require_env(
        "XUI_API_URL"
    ),

    xui_api_token=require_env(
        "XUI_API_TOKEN"
    ),

    # ------------------------------------------------------------------
    # VPN
    # ------------------------------------------------------------------

    vpn_host=require_env(
        "VPN_HOST"
    ),

    vpn_name=require_env(
        "VPN_NAME"
    ),

    vpn_country=os.getenv(
        "VPN_COUNTRY",
        "",
    ),

    vpn_wg_dns=os.getenv(
        "VPN_WG_DNS",
        "1.1.1.1",
    ),

    # ------------------------------------------------------------------
    # Protocols
    # ------------------------------------------------------------------

    enable_vless=os.getenv(
        "ENABLE_VLESS",
        "true",
    ).lower() == "true",

    # ------------------------------------------------------------------
    # Inbounds
    # ------------------------------------------------------------------

    vpn_vless_inbound=int(
        os.getenv(
            "VPN_VLESS_INBOUND",
            "1",
        )
    ),

    wireguard_inbound_id=int(
        os.getenv(
            "VPN_WIREGUARD_INBOUND",
            "1",
        )
    ),

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    database_path=os.getenv(
        "DATABASE_PATH",
        "vpn.db",
    ),

    # ------------------------------------------------------------------
    # YooKassa
    # ------------------------------------------------------------------

    yookassa_shop_id=require_env(
        "YOOKASSA_SHOP_ID"
    ),

    yookassa_secret_key=require_env(
        "YOOKASSA_SECRET_KEY"
    ),

    payment_return_url=require_env(
        "PAYMENT_RETURN_URL"
    ),

    # ------------------------------------------------------------------
    # JWT
    # ------------------------------------------------------------------

    jwt_secret=require_env(
        "JWT_SECRET"
    ),

    jwt_algorithm=os.getenv(
        "JWT_ALGORITHM",
        "HS256",
    ),

    jwt_expire_days=int(
        os.getenv(
            "JWT_EXPIRE_DAYS",
            "30",
        )
    ),

    # ------------------------------------------------------------------
    # Backend API
    # ------------------------------------------------------------------

    backend_api_url=require_env(
        "BACKEND_API_URL"
    ),

    backend_api_key=require_env(
        "BACKEND_API_KEY"
    ),
    public_subscription_base_url=require_env(
    "PUBLIC_SUBSCRIPTION_BASE_URL"
    ),

    # ------------------------------------------------------------------
    # Debug
    # ------------------------------------------------------------------

    debug=os.getenv(
        "DEBUG",
        "false",
    ).lower() == "true",
)

