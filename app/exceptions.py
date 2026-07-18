class VPNError(Exception):
    """
    Базовая ошибка VPN системы.
    """
    

class XUIError(VPNError):
    """
    Ошибка взаимодействия с 3x-ui.
    """


class XUIRequestError(XUIError):
    """
    Ошибка HTTP запроса.
    """


class XUIResponseError(XUIError):
    """
    3x-ui вернул ошибку.
    """


class InboundNotFoundError(VPNError):
    """
    Подходящий inbound не найден.
    """


class SubscriptionNotFoundError(VPNError):
    """
    Подписка отсутствует.
    """


class ProtocolNotSupportedError(VPNError):
    """
    Нет обработчика протокола.
    """


class ClientCreateError(VPNError):
    """
    Не удалось создать клиента.
    """