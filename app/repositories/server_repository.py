from app.database.database import db
from app.domain.server import Server


class ServerRepository:

    @staticmethod
    def _to_entity(
        row,
    ) -> Server:

        return Server(
            id=row["id"],
            name=row["name"],
            country=row["country"],
            host=row["host"],
            api_url=row["api_url"],
            api_token=row["api_token"],
            wireguard_inbound_id=row["wireguard_inbound_id"],
            enabled=bool(row["enabled"]),
            priority=row["priority"],
        )


    @staticmethod
    def create(
        server: Server,
    ) -> Server:

        db.execute(
            """
            INSERT INTO servers
            (
                name,
                country,
                host,
                api_url,
                api_token,
                wireguard_inbound_id,
                enabled,
                priority
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                server.name,
                server.country,
                server.host,
                server.api_url,
                server.api_token,
                server.wireguard_inbound_id,
                int(server.enabled),
                server.priority,
            ),
        )

        row = db.fetchone(
            """
            SELECT *
            FROM servers
            WHERE id = last_insert_rowid()
            """
        )

        return ServerRepository._to_entity(row)


    @staticmethod
    def update(
        server: Server,
    ):

        db.execute(
            """
            UPDATE servers
            SET
                name = ?,
                country = ?,
                host = ?,
                api_url = ?,
                api_token = ?,
                wireguard_inbound_id = ?,
                enabled = ?,
                priority = ?
            WHERE id = ?
            """,
            (
                server.name,
                server.country,
                server.host,
                server.api_url,
                server.api_token,
                server.wireguard_inbound_id,
                int(server.enabled),
                server.priority,
                server.id,
            ),
        )


    @staticmethod
    def get_by_id(
        server_id: int,
    ) -> Server | None:

        row = db.fetchone(
            """
            SELECT *
            FROM servers
            WHERE id = ?
            """,
            (server_id,),
        )

        if row is None:
            return None

        return ServerRepository._to_entity(row)


    @staticmethod
    def get_all(
    ) -> list[Server]:

        rows = db.fetchall(
            """
            SELECT *
            FROM servers
            ORDER BY priority ASC, id
            """
        )

        return [
            ServerRepository._to_entity(row)
            for row in rows
        ]


    @staticmethod
    def get_enabled(
    ) -> list[Server]:

        rows = db.fetchall(
            """
            SELECT *
            FROM servers
            WHERE enabled = 1
            ORDER BY priority ASC, id
            """
        )

        return [
            ServerRepository._to_entity(row)
            for row in rows
        ]


    @staticmethod
    def get_best() -> Server | None:

        row = db.fetchone(
            """
            SELECT *
            FROM servers
            WHERE enabled = 1
            ORDER BY priority ASC, id ASC
            LIMIT 1
            """
        )

        if row is None:
            return None

        return ServerRepository._to_entity(row)


    @staticmethod
    def delete(
        server_id: int,
    ):

        db.execute(
            """
            DELETE FROM servers
            WHERE id = ?
            """,
            (server_id,),
        )


    @staticmethod
    def enable(
        server_id: int,
    ):

        db.execute(
            """
            UPDATE servers
            SET enabled = 1
            WHERE id = ?
            """,
            (server_id,),
        )


    @staticmethod
    def disable(
        server_id: int,
    ):

        db.execute(
            """
            UPDATE servers
            SET enabled = 0
            WHERE id = ?
            """,
            (server_id,),
        )


    @staticmethod
    def count() -> int:

        row = db.fetchone(
            """
            SELECT COUNT(*) AS total
            FROM servers
            """
        )

        return row["total"]

    @staticmethod
    def count_online() -> int:

        row = db.fetchone(
            """
            SELECT COUNT(*) AS total
            FROM servers
            WHERE enabled = 1
            """
        )

        



server_repo = ServerRepository()