from typing import Any
from copy import deepcopy
import json
import httpx
from app.config import settings
from app.logger import logger
from app.domain.inbound import Inbound
from urllib.parse import urlparse
from app.exceptions import (
    XUIRequestError,
    XUIResponseError,
)


class XUIClient:
    """
    Клиент для работы с 3x-ui API.

    Не знает:
    - Telegram
    - Database
    - Subscription

    Отвечает только за API панели.
    """

    def __init__(self):

        self.client = httpx.AsyncClient(
            base_url=settings.api_url,
            headers={
                "Authorization": (
                    f"Bearer {settings.api_token}"
                ),
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            verify=False,
            timeout=30,
        )


    async def close(self):

        await self.client.aclose()



    async def _request(
        self,
        method: str,
        url: str,
        **kwargs,
    ) -> dict[str, Any]:

        logger.info(
            f"XUI request: {method} {url}"
        )

        try:

            response = await self.client.request(
                method,
                url,
                **kwargs,
            )

            logger.info(
                f"XUI response status: {response.status_code}"
            )

            response.raise_for_status()


        except httpx.HTTPError as e:

            logger.error(
                f"XUI HTTP error: {e}"
            )

            raise XUIRequestError(
                str(e)
            )


        try:

            data = response.json()

        except Exception:

            raise XUIResponseError(
                "Invalid JSON response"
            )


        if not data.get(
            "success",
            False
        ):

            raise XUIResponseError(
                data.get(
                    "msg",
                    "Unknown XUI error"
                )
            )


        return data



    # ==================================================
    # INBOUNDS
    # ==================================================

    async def get_inbounds(
        self,
    ) -> list[Inbound]:

        data = await self._request(
            "GET",
            "/panel/api/inbounds/list",
        )


        result = []


        for item in data.get(
            "obj",
            []
        ):

            result.append(
                Inbound(
                    id=item["id"],
                    remark=item.get(
                        "remark",
                        ""
                    ),
                    protocol=item["protocol"],
                    port=item.get(
                        "port",
                        0
                    ),
                    raw=item,
                )
            )


        return result



    async def get_inbound(
        self,
        protocol: str,
    ) -> Inbound | None:

        inbounds = await self.get_inbounds()


        for inbound in inbounds:

            if inbound.protocol == protocol:

                return inbound


        return None

    async def get_inbound_by_id(
        self,
        inbound_id: int,
    ) -> Inbound | None:

        data = await self._request(
            "GET",
            "/panel/api/inbounds/list",
        )

        for item in data.get("obj", []):

            if item["id"] == inbound_id:

                return Inbound(
                    id=item["id"],
                    remark=item.get("remark", ""),
                    protocol=item["protocol"],
                    port=item.get("port", 0),
                    raw=item,
                )

        return None

    async def get_default_inbound(
            self,
            protocol: str,
        ) -> Inbound | None:

            inbound_map = {
                "vless": settings.vpn_vless_inbound,
            }

            inbound_id = inbound_map.get(protocol)

            if inbound_id is None:
                raise ValueError(
                    f"Unsupported protocol: {protocol}"
                )

            return await self.get_inbound_by_id(
                inbound_id
            )

    async def refresh_inbound(
        self,
        inbound: Inbound,
    ) -> Inbound | None:

        return await self.get_inbound_by_id(
            inbound.id
    )

    # ==================================================
    # CLIENTS
    # ==================================================

    async def get_client(
        self,
        inbound: Inbound,
        client_uuid: str,
    ) -> dict | None:


        clients = (
            inbound.raw
            .get(
                "settings",
                {}
            )
            .get(
                "clients",
                []
            )
        )


        for client in clients:

            if client.get(
                "id"
            ) == client_uuid:

                return client


        return None

    async def get_wireguard_client(
        self,
        inbound: Inbound,
        email: str,
    ) -> dict | None:

        clients = (
            inbound.raw
            .get(
                "settings",
                {}
            )
            .get(
                "clients",
                []
            )
        )

        for client in clients:

            if client.get("email") == email:
                return client

        return None

  

    async def client_exists(
        self,
        inbound: Inbound,
        client_uuid: str,
    ) -> bool:

        client = await self.get_client(
            inbound,
            client_uuid,
        )

        return client is not None



    async def add_client(
        self,
        inbound_id: int,
        client: dict,
    ):


        await self._request(
            "POST",
            "/panel/api/clients/add",
            json={
                "client": client,
                "inboundIds": [
                    inbound_id
                ],
            },
        )


        logger.info(
            f"Client created in inbound {inbound_id}"
        )



    async def delete_client(
            self,
            client_uuid: str,
        ):


            await self._request(
                "POST",
                f"/panel/api/clients/del/{client_uuid}",
            )


            logger.info(
                f"Client deleted {client_uuid}"
            )


    async def update_client(
        self,
        inbound: Inbound,
        client_uuid: str,
        *,
        email: str | None = None,
        expiry_time: int | None = None,
        enable: bool | None = None,
        total_gb: int | None = None,
    ) -> bool:

        inbound = await self.refresh_inbound(inbound)

        if inbound is None:
            return False

        payload = deepcopy(inbound.raw)

        clients = (
            payload
            .get("settings", {})
            .get("clients", [])
        )

        if inbound.protocol == "wireguard":

            client = next(
                (
                    c
                    for c in clients
                    if c.get("email") == email
                ),
                None,
            )

        else:

            client = next(
                (
                    c
                    for c in clients
                    if c.get("id") == client_uuid
                ),
                None,
            )

        if client is None:

            logger.warning(
                f"Client not found ({email or client_uuid})"
            )

            return False

        if expiry_time is not None:
            client["expiryTime"] = expiry_time

        if enable is not None:
            client["enable"] = enable

        if total_gb is not None:
            client["totalGB"] = total_gb

        await self._request(
            "POST",
            f"/panel/api/inbounds/update/{inbound.id}",
            json=payload,
        )

        logger.info(
            f"Client updated ({email or client_uuid})"
        )

        return True


    async def set_client_enabled(
        self,
        inbound: Inbound,
        client_uuid: str,
        enabled: bool,
        email: str | None = None,
    ) -> bool:


        return await self.update_client(
            inbound=inbound,
            client_uuid=client_uuid,
            email=email,
            enable=enabled,
        )

    async def recreate_client(
        self,
        inbound: Inbound,
        client: dict,
    ) -> Inbound:

        await self.add_client(
            inbound.id,
            client,
        )

        updated = await self.refresh_inbound(
            inbound
        )

        if updated is None:
            raise XUIResponseError(
                "Inbound refresh failed"
            )

        return updated

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        tb,
    ):
        await self.close()

    async def get_subscription_links(
        self,
        sub_id: str,
    ) -> list[str]:

        data = await self._request(
            "GET",
            f"/panel/api/clients/subLinks/{sub_id}",
            
            
        )

        return data.get(
            "obj",
            [],
        )
    
    async def get_client_by_email(
        self,
        inbound: Inbound,
        email: str,
    ) -> dict | None:

        clients = (
            inbound.raw
            .get("settings", {})
            .get("clients", [])
        )

        for client in clients:

            if client.get("email") == email:
                return client

        return None
    
    async def get_client_link(
        self,
        sub_id: str,
        email: str,
    ) -> str | None:

        links = await self.get_subscription_links(sub_id)

        for link in links:

            if f"#{email}" in link:
                return link

        return None
    

    async def get_wireguard_config(
        self,
        inbound: Inbound,
        email: str,
    ) -> str:

        from app.protocols.wireguard.link_parser import (
            wireguard_link_to_config,
        )

        client = await self.get_wireguard_client(
            inbound,
            email,
        )

        if client is None:
            raise RuntimeError(
                "Клиент WireGuard не найден"
            )

        links = await self.get_subscription_links(
            client["subId"]
        )

        if not links:
            raise RuntimeError(
                "3x-ui не вернул WireGuard ссылку"
            )

        return wireguard_link_to_config(
            links[0]
        )