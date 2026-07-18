from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from app.domain.inbound import Inbound
from app.domain.subscription import Subscription


class ProtocolHandler(ABC):
    """
    Базовый класс всех VPN-протоколов.

    Каждый наследник автоматически регистрируется
    по своему имени protocol.
    """

    protocol: ClassVar[str]

    _registry: dict[str, type["ProtocolHandler"]] = {}


    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        protocol = getattr(cls, "protocol", None)

        if protocol:
            ProtocolHandler._registry[protocol] = cls


    @classmethod
    def create(
        cls,
        protocol: str,
    ) -> "ProtocolHandler":
        """
        Создает обработчик по имени протокола.
        """

        handler_cls = cls._registry.get(
            protocol
        )

        if handler_cls is None:
            raise ValueError(
                f"Unsupported protocol '{protocol}'"
            )

        return handler_cls()



    @classmethod
    def protocols(
        cls,
    ) -> list[str]:
        """
        Список доступных протоколов.
        """

        return sorted(
            cls._registry.keys()
        )



    @abstractmethod
    async def get_inbound(
        self,
        xui,
    ) -> Inbound | None:
        """
        Найти inbound протокола.
        """
        raise NotImplementedError



    @abstractmethod
    def build_payload(
        self,
        subscription: Subscription,
        inbound: Inbound,
    ) -> dict:
        """
        Создать payload клиента для XUI.
        """
        raise NotImplementedError



    @abstractmethod
    def build_config(
        self,
        subscription: Subscription,
        inbound: Inbound,
    ) -> str:
        """
        Создать VPN конфигурацию.
        """
        raise NotImplementedError



    @abstractmethod
    async def create_subscription(
        self,
        xui,
        user_id: int,
        days: int,
    ) -> Subscription:
        """
        Создание нового клиента.
        """
        raise NotImplementedError



    @abstractmethod
    async def restore_client(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:
        """
        Восстановление клиента в XUI.
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
        Продление клиента.
        """
        raise NotImplementedError



    @abstractmethod
    async def disable(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:
        """
        Отключение клиента.
        """
        raise NotImplementedError



    @abstractmethod
    async def sync(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:
        """
        Синхронизация состояния клиента
        между XUI и БД.
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
    
    # Автоматически загружаем все протоколы
from app.protocols.loader import load_protocol_handlers

load_protocol_handlers()