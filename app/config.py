from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    # Telegram
    bot_token: str
    admin_id: int

    # Database
    db_name: str

    # 3x-ui
    api_url: str
    api_token: str

    # VPN
    vpn_host: str
    vpn_name: str
    vpn_country: str
    vpn_wg_dns: str

    # Default inbound IDs
    vpn_vless_inbound: int


def require_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Environment variable '{name}' is missing."
        )

    return value


settings = Settings(
    # Telegram
    bot_token=require_env("BOT_TOKEN"),

    admin_id=int(
        os.getenv("ADMIN_ID", "0")
    ),

    # Database
    db_name=os.getenv(
        "DB_NAME",
        "vpn.db",
    ),

    # 3x-ui
    api_url=require_env("API_URL"),

    api_token=require_env("API_TOKEN"),

    # VPN
    vpn_host=require_env("VPN_HOST"),

    vpn_name=require_env("VPN_NAME"),

    vpn_country=os.getenv(
        "VPN_COUNTRY",
        "",
    ),

    vpn_wg_dns=os.getenv(
        "VPN_WG_DNS",
        "1.1.1.1",
    ),

    # Inbounds
    vpn_vless_inbound=int(
        os.getenv(
            "VPN_VLESS_INBOUND",
            "1",
        )
    ),
)