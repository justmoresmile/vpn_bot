from datetime import datetime, timedelta, timezone

from loguru import logger

from app.domain.subscription import Subscription
from app.domain.enums.subscription_status import SubscriptionStatus
from app.protocols.handlers.base import ProtocolHandler
from app.repositories.subscription_repository import subscription_repo
from app.repositories.subscription_notification_repository import (
    subscription_notification_repo,
)
from app.services.server_service import server_service
from app.services.xui_client import XUIClient
from app.services.subscription_token import (
    generate_subscription_token,
)
from app.services.remnawave_service import (
    remnawave_service,
)
from app.services.pricing_service import (
    MIN_DEVICE_LIMIT,
    MAX_DEVICE_LIMIT,
    TRIAL_DEVICE_LIMIT,
)

class VPNService:

    def __init__(self):
        self._xui_clients: dict[int, XUIClient] = {}

    # ============================================================
    # SERVER
    # ============================================================

    @staticmethod
    def _get_server(
        subscription: Subscription,
    ):
        server = server_service.get_by_id(
            subscription.server_id
        )

        if server is None:
            raise RuntimeError(
                f"Server {subscription.server_id} not found."
            )

        return server

    # ============================================================
    # XUI
    # ============================================================

    async def _get_xui(
        self,
        server,
    ) -> XUIClient:

        if server.id not in self._xui_clients:
            self._xui_clients[server.id] = XUIClient(
                server
            )

        return self._xui_clients[server.id]

    # ============================================================
    # PROTOCOL
    # ============================================================

    @staticmethod
    def _get_handler(
        subscription: Subscription,
    ) -> ProtocolHandler:

        server = VPNService._get_server(
            subscription
        )

        return ProtocolHandler.create(
            protocol=subscription.protocol,
            server=server,
        )

    @staticmethod
    def get_protocols() -> list[str]:
        """
        Возвращает все зарегистрированные протоколы.

        Например:

            [
                "vless",
                "wireguard",
            ]
        """

        return ProtocolHandler.protocols()

    # ============================================================
    # CREATE
    # ============================================================

    async def create(
        self,
        user_id: int,
        protocol: str = "vless",
        days: int = 30,
    ) -> Subscription:

        protocol = protocol.lower().strip()

        if protocol != "vless":
            raise ValueError(
                f"Unsupported VPN protocol: {protocol}"
            )

        if days <= 0:
            raise ValueError(
                "days must be greater than 0"
            )

        now = datetime.now(
            timezone.utc
        )

        expires_at = (
            now
            + timedelta(
                days=days
            )
        )

        provider_user = (
            remnawave_service.ensure_user(
                justvpn_user_id=user_id,
                expire_at=expires_at,
                hwid_device_limit=1,
            )
        )

        subscription = Subscription(
            id=None,
            user_id=user_id,
            provider="remnawave",
            protocol=protocol,
            server_id=None,
            inbound_id=None,
            client_id=(
                provider_user.get(
                    "vlessUuid"
                )
            ),
            client_email=None,
            sub_id=None,
            subscription_token=(
                generate_subscription_token()
            ),
            config="",
            status=(
                SubscriptionStatus.ACTIVE
            ),
            device_limit=1,
            created_at=now,
            expires_at=expires_at,
        )

        created = subscription_repo.create(
            subscription
        )

        logger.info(
            "Remnawave subscription created "
            "user={} subscription={} "
            "provider_user={} protocol={}",
            user_id,
            created.id,
            provider_user.get("id"),
            protocol,
        )

        return created

    # ============================================================
    # CREATE BALANCE SUBSCRIPTION
    # ============================================================

    async def create_balance_subscription(
        self,
        user_id: int,
        protocol: str = "vless",
    ) -> Subscription:

        protocol = protocol.lower().strip()

        if protocol != "vless":
            raise ValueError(
                f"Unsupported VPN protocol: {protocol}"
            )

        # Не выдаём бесплатный период.
        # Новая balance-подписка создаётся уже due.
        now = datetime.now(
            timezone.utc
        )

        due_at = (
            now
            - timedelta(seconds=5)
        )

        provider_user = (
            remnawave_service.ensure_user(
                justvpn_user_id=user_id,
                expire_at=due_at,
                hwid_device_limit=TRIAL_DEVICE_LIMIT,
            )
        )

        # Пользователь до успешного списания
        # обязан оставаться выключенным.
        remote_status = str(
            provider_user.get(
                "status",
                "",
            )
        ).upper()

        if remote_status != "DISABLED":
            remnawave_service.disable_user(
                user_id
            )

        subscription = Subscription(
            id=None,
            user_id=user_id,
            provider="remnawave",
            protocol=protocol,
            server_id=None,
            inbound_id=None,
            client_id=(
                provider_user.get(
                    "vlessUuid"
                )
            ),
            client_email=None,
            sub_id=None,
            subscription_token=(
                generate_subscription_token()
            ),
            config="",
            status=(
                SubscriptionStatus.DISABLED
            ),
            device_limit=TRIAL_DEVICE_LIMIT,
            created_at=now,
            expires_at=due_at,
            billing_mode="balance",
            paid_until=due_at,
            billing_day_index=0,
            billing_enabled=True,
        )

        created = subscription_repo.create(
            subscription
        )

        logger.info(
            "Balance subscription created "
            "user={} subscription={} "
            "provider_user={}",
            user_id,
            created.id,
            provider_user.get("id"),
        )

        return created

    # ============================================================
    # DEVICE LIMIT
    # ============================================================

    async def set_device_limit(
        self,
        subscription: Subscription,
        device_limit: int,
    ) -> Subscription:

        if subscription.billing_mode != "balance":
            raise ValueError(
                "Изменение количества устройств "
                "доступно только для balance-подписки"
            )

        if (
            device_limit < MIN_DEVICE_LIMIT
            or device_limit > MAX_DEVICE_LIMIT
        ):
            raise ValueError(
                f"Количество устройств должно быть "
                f"от {MIN_DEVICE_LIMIT} "
                f"до {MAX_DEVICE_LIMIT}"
            )

        if (
            subscription.status
            == SubscriptionStatus.DELETED
        ):
            raise ValueError(
                "Подписка удалена"
            )

        if (
            subscription.device_limit
            == device_limit
        ):
            return subscription

        expire_at = (
            subscription.paid_until
            or subscription.expires_at
        )

        if expire_at is None:
            raise ValueError(
                "У подписки отсутствует дата "
                "окончания оплаченного периода"
            )

        # Запоминаем состояние до изменения.
        # Изменение device_limit не должно
        # самостоятельно включать VPN.
        remote_before = (
            remnawave_service.get_user(
                subscription.user_id
            )
        )

        remote_status_before = (
            str(
                remote_before.get(
                    "status",
                    "",
                )
            ).upper()
            if remote_before
            else ""
        )

        remnawave_service.ensure_user(
            justvpn_user_id=subscription.user_id,
            expire_at=expire_at,
            hwid_device_limit=device_limit,
        )

        # Если пользователь был отключён,
        # оставляем его отключённым.
        if (
            remote_status_before
            == "DISABLED"
        ):
            remote_after = (
                remnawave_service.get_user(
                    subscription.user_id
                )
            )

            remote_status_after = (
                str(
                    remote_after.get(
                        "status",
                        "",
                    )
                ).upper()
                if remote_after
                else ""
            )

            if remote_status_after != "DISABLED":
                remnawave_service.disable_user(
                    subscription.user_id
                )

        # Локальную БД меняем только после
        # успешного обновления Remnawave.
        old_device_limit = (
            subscription.device_limit
        )

        subscription.device_limit = (
            device_limit
        )

        subscription_repo.update(
            subscription
        )

        logger.info(
            "Subscription device limit changed "
            "subscription={} user={} "
            "old_limit={} new_limit={}",
            subscription.id,
            subscription.user_id,
            old_device_limit,
            device_limit,
        )

        return subscription

    # ============================================================
    # PURCHASE
    # ============================================================

    async def purchase(
        self,
        user_id: int,
        protocol: str = "vless",
        days: int = 30,
    ) -> Subscription:

        protocol = protocol.lower().strip()

        if protocol != "vless":
            raise ValueError(
                f"Unsupported VPN protocol: {protocol}"
            )

        existing = (
            subscription_repo
            .get_active_by_user(
                user_id
            )
        )

        if existing is not None:

            logger.info(
                "Active subscription exists, "
                "renew instead "
                "user={} subscription={} days={}",
                user_id,
                existing.id,
                days,
            )

            return await self.renew(
                subscription_id=existing.id,
                days=days,
            )

        logger.info(
            "Creating new Remnawave subscription "
            "user={} protocol={} days={}",
            user_id,
            protocol,
            days,
        )

        return await self.create(
            user_id=user_id,
            protocol=protocol,
            days=days,
        )

    # ============================================================
    # RENEW
    # ============================================================

    async def renew(
        self,
        subscription_id: int,
        days: int,
    ) -> Subscription:

        if days <= 0:
            raise ValueError(
                "days must be greater than 0"
            )

        subscription = (
            subscription_repo.get_by_id(
                subscription_id
            )
        )

        if subscription is None:
            raise ValueError(
                "Подписка не найдена"
            )

        provider_user = (
            remnawave_service.renew_user(
                justvpn_user_id=(
                    subscription.user_id
                ),
                days=days,
            )
        )

        expire_value = (
            provider_user.get(
                "expireAt"
            )
        )

        if not expire_value:
            raise RuntimeError(
                "Remnawave response "
                "has no expireAt"
            )

        subscription.expires_at = (
            datetime.fromisoformat(
                expire_value.replace(
                    "Z",
                    "+00:00",
                )
            )
        )

        subscription.status = (
            SubscriptionStatus.ACTIVE
        )

        subscription.provider = (
            "remnawave"
        )

        subscription_repo.update(
            subscription
        )

        subscription_notification_repo.delete_by_subscription(
            subscription.id
        )

        logger.info(
            "Subscription {} renewed "
            "via Remnawave days={}",
            subscription.id,
            days,
        )

        return subscription

    # ============================================================
    # EXTEND
    # ============================================================

    async def extend(
        self,
        subscription_id: int,
        days: int,
    ) -> Subscription:

        subscription = await self.renew(
            subscription_id,
            days,
        )

        subscription_notification_repo.delete_by_subscription(
            subscription.id
        )

        logger.info(
            "Notifications reset for subscription {}",
            subscription.id,
        )

        return subscription

    # ============================================================
    # DISABLE
    # ============================================================

    async def disable(
        self,
        subscription: Subscription,
    ) -> Subscription:

        remnawave_service.disable_user(
            subscription.user_id
        )

        subscription.status = (
            SubscriptionStatus.DISABLED
        )

        subscription_repo.update(
            subscription
        )

        logger.warning(
            "Subscription {} disabled "
            "via Remnawave",
            subscription.id,
        )

        return subscription

    # ============================================================
    # DISABLE BY ID
    # ============================================================

    async def disable_subscription(
        self,
        subscription_id: int,
    ) -> Subscription | None:

        subscription = (
            subscription_repo.get_by_id(
                subscription_id
            )
        )

        if subscription is None:
            return None

        return await self.disable(
            subscription
        )

    # ============================================================
    # GET CONFIG
    # ============================================================

    async def get_config(
        self,
        subscription_id: int,
    ) -> str | None:

        subscription = (
            subscription_repo.get_by_id(
                subscription_id
            )
        )

        if subscription is None:
            return None

        # --------------------------------------------------------
        # REMNAWAVE
        # --------------------------------------------------------

        if (
            subscription.provider
            == "remnawave"
        ):

            return (
                remnawave_service
                .get_subscription_url(
                    subscription.user_id
                )
            )

        # --------------------------------------------------------
        # LEGACY
        # --------------------------------------------------------

        if subscription.config:
            return subscription.config

        return None

    # ============================================================
    # GET FILE
    # ============================================================

    async def get_file(
        self,
        subscription: Subscription,
    ) -> tuple[str, bytes]:

        # --------------------------------------------------------
        # REMNAWAVE
        # --------------------------------------------------------

        if (
            subscription.provider
            == "remnawave"
        ):

            url = (
                remnawave_service
                .get_subscription_url(
                    subscription.user_id
                )
            )

            if not url:
                raise RuntimeError(
                    "Remnawave subscription URL not found"
                )

            content = (
                url.strip()
                + "\n"
            ).encode(
                "utf-8"
            )

            return (
                "justvpn-subscription.txt",
                content,
            )

        # --------------------------------------------------------
        # LEGACY
        # --------------------------------------------------------

        server = self._get_server(
            subscription
        )

        handler = self._get_handler(
            subscription
        )

        xui = await self._get_xui(
            server
        )

        return await handler.get_file(
            xui=xui,
            subscription=subscription,
        )

    # ============================================================
    # GET USER SUBSCRIPTIONS
    # ============================================================

    def get_by_user(
        self,
        user_id: int,
    ) -> list[Subscription]:

        return subscription_repo.get_by_user(
            user_id
        )

    # ============================================================
    # GET SUBSCRIPTION
    # ============================================================

    async def get_subscription(
        self,
        subscription_id: int,
    ) -> Subscription | None:

        subscription = (
            subscription_repo.get_by_id(
                subscription_id
            )
        )

        if subscription is None:
            return None

        return await self.sync_subscription(
            subscription
        )

    # ============================================================
    # SYNC
    # ============================================================

    async def sync_subscription(
        self,
        subscription: Subscription,
    ) -> Subscription:

        # Deleted is a terminal local state.
        # Remote provider status must never revive it.
        if subscription.status == SubscriptionStatus.DELETED:
            return subscription

        # --------------------------------------------------------
        # REMNAWAVE
        # --------------------------------------------------------

        if (
            subscription.provider
            == "remnawave"
        ):

            remote = (
                remnawave_service
                .get_user(
                    subscription.user_id
                )
            )

            if remote is None:

                logger.warning(
                    "Remnawave user not found "
                    "for subscription {} user={}",
                    subscription.id,
                    subscription.user_id,
                )

                return subscription

            # ----------------------------------------------------
            # EXPIRATION
            # ----------------------------------------------------

            expire_value = remote.get(
                "expireAt"
            )

            if expire_value:

                try:
                    subscription.expires_at = (
                        datetime.fromisoformat(
                            expire_value.replace(
                                "Z",
                                "+00:00",
                            )
                        )
                    )

                except (
                    ValueError,
                    TypeError,
                ):

                    logger.warning(
                        "Invalid Remnawave expireAt "
                        "subscription={} value={}",
                        subscription.id,
                        expire_value,
                    )

            # ----------------------------------------------------
            # STATUS
            # ----------------------------------------------------

            remote_status = str(
                remote.get(
                    "status",
                    "",
                )
            ).upper()

            if remote_status == "ACTIVE":

                subscription.status = (
                    SubscriptionStatus.ACTIVE
                )

            elif remote_status == "DISABLED":

                subscription.status = (
                    SubscriptionStatus.DISABLED
                )

            elif remote_status == "EXPIRED":

                subscription.status = (
                    SubscriptionStatus.EXPIRED
                )

            elif remote_status == "LIMITED":

                # Remnawave LIMITED означает,
                # что доступ фактически ограничен.
                subscription.status = (
                    SubscriptionStatus.DISABLED
                )

            # ----------------------------------------------------
            # VLESS UUID
            # ----------------------------------------------------

            vless_uuid = remote.get(
                "vlessUuid"
            )

            if vless_uuid:
                subscription.client_id = str(
                    vless_uuid
                )

            subscription.provider = (
                "remnawave"
            )

            subscription_repo.update(
                subscription
            )

            logger.debug(
                "Subscription {} synced "
                "from Remnawave status={} "
                "expire_at={}",
                subscription.id,
                remote_status,
                subscription.expires_at,
            )

            return subscription

        # --------------------------------------------------------
        # LEGACY / OTHER PROVIDERS
        # --------------------------------------------------------

        server = self._get_server(
            subscription
        )

        handler = self._get_handler(
            subscription
        )

        xui = await self._get_xui(
            server
        )

        synced = await handler.sync(
            xui=xui,
            subscription=subscription,
        )

        subscription_repo.update(
            synced
        )

        return synced

    # ============================================================
    # RESTORE
    # ============================================================

    async def restore_client(
        self,
        subscription: Subscription,
    ) -> Subscription:

        now = datetime.now(
            timezone.utc
        )

        if (
            subscription.expires_at
            is not None
            and subscription.expires_at.tzinfo
            is None
        ):
            expires_at = (
                subscription.expires_at
                .replace(
                    tzinfo=timezone.utc
                )
            )
        else:
            expires_at = (
                subscription.expires_at
            )

        if (
            expires_at is not None
            and expires_at <= now
        ):
            raise ValueError(
                "Подписка истекла"
            )

        remnawave_service.enable_user(
            subscription.user_id
        )

        subscription.status = (
            SubscriptionStatus.ACTIVE
        )

        subscription.provider = (
            "remnawave"
        )

        subscription_repo.update(
            subscription
        )

        logger.info(
            "Subscription {} restored "
            "via Remnawave",
            subscription.id,
        )

        return subscription

    # ============================================================
    # DELETE
    # ============================================================

    async def delete(
        self,
        subscription: Subscription,
    ) -> None:

        # --------------------------------------------------------
        # REMNAWAVE
        # --------------------------------------------------------

        if (
            subscription.provider
            == "remnawave"
        ):

            remnawave_service.disable_user(
                subscription.user_id
            )

            subscription_repo.delete(
                subscription.id
            )

            logger.info(
                "Subscription {} deleted locally "
                "and Remnawave user disabled",
                subscription.id,
            )

            return

        # --------------------------------------------------------
        # LEGACY
        # --------------------------------------------------------

        server = self._get_server(
            subscription
        )

        handler = self._get_handler(
            subscription
        )

        xui = await self._get_xui(
            server
        )

        await handler.delete(
            xui=xui,
            subscription=subscription,
        )

        subscription_repo.delete(
            subscription.id
        )

        logger.info(
            "Subscription {} deleted protocol={}",
            subscription.id,
            subscription.protocol,
        )

    # ============================================================
    # CLOSE XUI CLIENTS
    # ============================================================

    async def close(self):

        for xui in self._xui_clients.values():
            await xui.close()

        self._xui_clients.clear()

        logger.info(
            "XUI clients closed"
        )


vpn_service = VPNService()