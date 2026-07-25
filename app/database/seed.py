from app.config import settings
from app.domain.server import Server
from app.repositories.server_repository import server_repo


def seed_database():

    if server_repo.get_all():
        return

    server_repo.create(
        Server(
            id=0,
            name=settings.vpn_name,
            country=settings.vpn_country,
            host=settings.vpn_host,
            api_url=settings.xui_api_url,
            api_token=settings.xui_api_token,
            wireguard_inbound_id=int(
            settings.wireguard_inbound_id
            ),
            enabled=True,
            priority=100,
        )
    )