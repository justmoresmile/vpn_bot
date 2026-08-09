from app.domain.server import Server
from app.repositories.server_repository import server_repo
from app.repositories.subscription_repository import subscription_repo


class ServerService:

    def get_all(
        self,
    ) -> list[Server]:

        return server_repo.get_all()


    def get_enabled(
        self,
    ) -> list[Server]:

        return server_repo.get_enabled()


    def get_best_server(
        self,
    ) -> Server:
        """
        Возвращает лучший доступный сервер.

        Сначала выбирается сервер с наименьшим priority.
        Если priority одинаковый — выбирается сервер
        с наименьшим количеством активных подписок.
        """

        servers = self.get_enabled()

        if not servers:
            raise RuntimeError(
                "Нет доступных VPN-серверов."
            )

        return min(
            servers,
            key=lambda server: (
                server.priority,
                subscription_repo.count_active_by_server(
                    server.id
                ),
            ),
        )


    def get_by_id(
        self,
        server_id: int,
    ) -> Server:

        server = server_repo.get_by_id(
            server_id
        )

        if server is None:
            raise RuntimeError(
                f"Сервер {server_id} не найден."
            )

        return server




    def enable_server(
        self,
        server_id: int,
    ) -> Server:

        server = self.get_by_id(
            server_id
        )

        server_repo.enable(
            server_id
        )

        return self.get_by_id(
            server_id
        )


    def disable_server(
        self,
        server_id: int,
    ) -> Server:

        server = self.get_by_id(
            server_id
        )

        server_repo.disable(
            server_id
        )

        return self.get_by_id(
            server_id
        )


    def delete_server(
        self,
        server_id: int,
    ):

        self.get_by_id(
            server_id
        )

        count = subscription_repo.count_by_server(
            server_id
        )

        if count > 0:
            raise RuntimeError(
                f"Нельзя удалить сервер. На нём находится {count} подписок."
            )

        server_repo.delete(
            server_id
        )

server_service = ServerService()