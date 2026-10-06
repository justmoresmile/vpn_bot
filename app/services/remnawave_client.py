from typing import Any

import httpx

from app.config import settings


class RemnawaveClient:

    def __init__(self) -> None:

        self.base_url = (
            settings.remnawave_api_url
            .rstrip("/")
        )

        self.api_token = (
            settings.remnawave_api_token
        )

        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=20.0,
            headers={
                "Authorization":
                    f"Bearer {self.api_token}",
                "Accept":
                    "application/json",
            },
        )

    # ==============================================================
    # REQUEST
    # ==============================================================

    def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:

        response = self._client.request(
            method=method,
            url=path,
            json=json,
            params=params,
        )

        response.raise_for_status()

        if not response.content:
            return None

        return response.json()

    # ==============================================================
    # USERS
    # ==============================================================

    def get_user(
        self,
        user_uuid: str,
    ) -> Any:

        return self.request(
            "GET",
            f"/api/users/{user_uuid}",
        )

    def get_user_by_username(
        self,
        username: str,
    ) -> Any:

        return self.request(
            "GET",
            f"/api/users/by-username/{username}",
        )

    def create_user(
        self,
        payload: dict[str, Any],
    ) -> Any:

        return self.request(
            "POST",
            "/api/users",
            json=payload,
        )

    def update_user(
        self,
        payload: dict[str, Any],
    ) -> Any:

        return self.request(
            "PATCH",
            "/api/users",
            json=payload,
        )

    def delete_user(
        self,
        user_id: int,
    ) -> Any:

        return self.request(
            "DELETE",
            f"/api/users/{user_id}",
        )

    # ==============================================================
    # SUBSCRIPTIONS
    # ==============================================================

    def get_subscription(
        self,
        user_uuid: str,
    ) -> Any:

        return self.request(
            "GET",
            f"/api/subscriptions/by-id/{user_uuid}",
        )

    # ==============================================================
    # BANDWIDTH
    # ==============================================================

    def get_user_usage(
        self,
        user_id: int,
        start: str,
        end: str,
    ) -> Any:

        return self.request(
            "GET",
            f"/api/bandwidth-stats/users/{user_id}",
            params={
                "start": start,
                "end": end,
            },
        )

    # ==============================================================
    # DEVICES
    # ==============================================================

    def get_devices(
        self,
        user_uuid: str,
    ) -> Any:

        return self.request(
            "GET",
            f"/api/hwid/devices/{user_uuid}",
        )


    def delete_device(
        self,
        user_id: int,
        hwid: str,
    ) -> Any:

        return self.request(
            "POST",
            "/api/hwid/devices/delete",
            json={
                "userId": user_id,
                "hwid": hwid,
            },
        )

    # ==============================================================
    # CLOSE
    # ==============================================================

    def close(self) -> None:
        self._client.close()


remnawave_client = RemnawaveClient()
