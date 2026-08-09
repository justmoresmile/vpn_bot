
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from app.domain.inbound import Inbound
from app.domain.subscription import Subscription


class ProtocolHandler(ABC):
    """
    Базовый интерфейс всех VPN-протоколов.

    Каждый протокол наследуется от этого класса и указывает
    собственное имя через class attribute `protocol`.

    Например:

        class VlessHandler(ProtocolHandler):
            protocol = "vless"

        class WireGuardHandler(ProtocolHandler):
            protocol = "wireguard"

    После импорта класса он автоматически регистрируется
    в общем реестре ProtocolHandler.
    """

    protocol: ClassVar[str]

    _registry: ClassVar[
        dict[str, type["ProtocolHandler"]]
    ] = {}

    def __init_subclass__(cls, **kwargs):
        """
        Автоматически регистрирует наследников
        в реестре протоколов.
        """

        super().__init_subclass__(**kwargs)

        protocol = getattr(cls, "protocol", None)

        if protocol:
            ProtocolHandler._registry[protocol] = cls

    @classmethod
    def create(
        cls,
        protocol: str,
        server=None,
    ) -> "ProtocolHandler":
        """
        Создаёт обработчик указанного протокола.

        Например:

            handler = ProtocolHandler.create(
                "vless",
                server,
            )
        """

        handler_cls = cls._registry.get(protocol)

        if handler_cls is None:
            raise ValueError(
                f"Unsupported protocol '{protocol}'. "
                f"Available protocols: {cls.protocols()}"
            )

        return handler_cls(server)

    @classmethod
    def protocols(cls) -> list[str]:
        """
        Возвращает список зарегистрированных протоколов.
        """

        return sorted(cls._registry.keys())

    @abstractmethod
    async def get_inbound(
        self,
        xui,
    ) -> Inbound | None:
        """
        Находит подходящий inbound для данного протокола.
        """
        raise NotImplementedError

    @abstractmethod
    def build_payload(
        self,
        subscription: Subscription,
        inbound: Inbound,
    ) -> dict:
        """
        Формирует payload клиента для XUI.
        """
        raise NotImplementedError

    @abstractmethod
    def build_config(
        self,
        subscription: Subscription,
        inbound: Inbound,
    ) -> str:
        """
        Формирует клиентскую конфигурацию.
        """
        raise NotImplementedError

    @abstractmethod
    async def create_subscription(
        self,
        xui,
        server,
        user_id: int,
        days: int,
    ) -> Subscription:
        """
        Создаёт новую VPN-подписку и клиента
        в соответствующем протоколе.
        """
        raise NotImplementedError

    @abstractmethod
    async def restore_client(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:
        """
        Восстанавливает клиента протокола.
        """
        raise NotImplementedError

    @abstractmethod
    async def restore(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:
        """
        Восстанавливает подписку после необходимости
        пересоздания/восстановления клиента.
        """
        raise NotImplementedError

    @abstractmethod
    async def renew(
        self,
        xui,
        subscription: Subscription,
        days: int,
    ) -> Subscription:
        """
        Продлевает существующую подписку.
        """
        raise NotImplementedError

    @abstractmethod
    async def disable(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:
        """
        Отключает клиента в XUI.
        """
        raise NotImplementedError

    @abstractmethod
    async def sync(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:
        """
        Синхронизирует состояние подписки
        с XUI.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(
        self,
        xui,
        subscription: Subscription,
    ) -> None:
        """
        Удаляет клиента из XUI.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_file(
        self,
        xui,
        subscription: Subscription,
    ) -> tuple[str, bytes]:
        """
        Возвращает готовый конфигурационный файл.

        Returns:
            (
                filename,
                file_bytes
            )
        """
        raise NotImplementedError

