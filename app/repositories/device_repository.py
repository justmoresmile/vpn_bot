from datetime import datetime
import secrets

from app.database.database import db

from app.domain.device import Device
from app.domain.device_client import DeviceClient


class DeviceRepository:

    # ============================================================
    # DEVICE MAPPERS
    # ============================================================

    @staticmethod
    def _to_device(
        row,
    ) -> Device:

        return Device(
            id=row["id"],
            subscription_id=row["subscription_id"],
            device_token=row["device_token"],
            device_name=row["device_name"],
            device_model=row["device_model"],
            device_os=row["device_os"],
            os_version=row["os_version"],
            is_active=bool(
                row["is_active"]
            ),
            first_seen_at=datetime.fromtimestamp(
                row["first_seen_at"]
            ),
            last_seen_at=datetime.fromtimestamp(
                row["last_seen_at"]
            ),
        )

    @staticmethod
    def _to_client(
        row,
    ) -> DeviceClient:

        return DeviceClient(
            id=row["id"],
            device_id=row["device_id"],
            client_app=row["client_app"],
            client_version=row["client_version"],
            client_identifier=row[
                "client_identifier"
            ],
            first_seen_at=datetime.fromtimestamp(
                row["first_seen_at"]
            ),
            last_seen_at=datetime.fromtimestamp(
                row["last_seen_at"]
            ),
        )

    # ============================================================
    # GET DEVICE
    # ============================================================

    @staticmethod
    def get_by_id(
        device_id: int,
    ) -> Device | None:

        row = db.fetchone(
            """
            SELECT *
            FROM devices_v2
            WHERE id = ?
            """,
            (
                device_id,
            ),
        )

        if row is None:
            return None

        return DeviceRepository._to_device(
            row
        )

    @staticmethod
    def get_by_token(
        device_token: str,
    ) -> Device | None:

        row = db.fetchone(
            """
            SELECT *
            FROM devices_v2
            WHERE device_token = ?
            LIMIT 1
            """,
            (
                device_token,
            ),
        )

        if row is None:
            return None

        return DeviceRepository._to_device(
            row
        )

    @staticmethod
    def get_by_client_identifier(
        subscription_id: int,
        client_identifier: str,
    ) -> Device | None:

        row = db.fetchone(
            """
            SELECT d.*
            FROM devices_v2 d

            JOIN device_clients dc
              ON dc.device_id = d.id

            WHERE d.subscription_id = ?
              AND dc.client_identifier = ?

            LIMIT 1
            """,
            (
                subscription_id,
                client_identifier,
            ),
        )

        if row is None:
            return None

        return DeviceRepository._to_device(
            row
        )

    # ============================================================
    # LIST DEVICES
    # ============================================================

    @staticmethod
    def get_by_subscription(
        subscription_id: int,
        active_only: bool = False,
    ) -> list[Device]:

        if active_only:

            rows = db.fetchall(
                """
                SELECT *
                FROM devices_v2
                WHERE subscription_id = ?
                  AND is_active = 1
                ORDER BY last_seen_at DESC
                """,
                (
                    subscription_id,
                ),
            )

        else:

            rows = db.fetchall(
                """
                SELECT *
                FROM devices_v2
                WHERE subscription_id = ?
                ORDER BY last_seen_at DESC
                """,
                (
                    subscription_id,
                ),
            )

        return [
            DeviceRepository._to_device(
                row
            )
            for row in rows
        ]

    # ============================================================
    # COUNT
    # ============================================================

    @staticmethod
    def count_active(
        subscription_id: int,
    ) -> int:

        row = db.fetchone(
            """
            SELECT COUNT(*) AS total
            FROM devices_v2
            WHERE subscription_id = ?
              AND is_active = 1
            """,
            (
                subscription_id,
            ),
        )

        return row["total"]

    # ============================================================
    # CREATE DEVICE
    # ============================================================

    @staticmethod
    def create(
        *,
        subscription_id: int,
        device_name: str | None = None,
        device_model: str | None = None,
        device_os: str | None = None,
        os_version: str | None = None,
        device_token: str | None = None,
    ) -> Device:

        now = int(
            datetime.now().timestamp()
        )

        if device_token is None:
            device_token = secrets.token_urlsafe(
                24
            )

        db.execute(
            """
            INSERT INTO devices_v2
            (
                subscription_id,
                device_token,
                device_name,
                device_model,
                device_os,
                os_version,
                is_active,
                first_seen_at,
                last_seen_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                subscription_id,
                device_token,
                device_name,
                device_model,
                device_os,
                os_version,
                1,
                now,
                now,
            ),
        )

        row = db.fetchone(
            """
            SELECT *
            FROM devices_v2
            WHERE id = last_insert_rowid()
            """
        )

        return DeviceRepository._to_device(
            row
        )

    # ============================================================
    # UPDATE DEVICE
    # ============================================================

    @staticmethod
    def touch(
        device_id: int,
        *,
        device_name: str | None = None,
        device_model: str | None = None,
        device_os: str | None = None,
        os_version: str | None = None,
    ) -> Device | None:

        now = int(
            datetime.now().timestamp()
        )

        db.execute(
            """
            UPDATE devices_v2
            SET
                device_name = COALESCE(
                    ?,
                    device_name
                ),

                device_model = COALESCE(
                    ?,
                    device_model
                ),

                device_os = COALESCE(
                    ?,
                    device_os
                ),

                os_version = COALESCE(
                    ?,
                    os_version
                ),

                last_seen_at = ?

            WHERE id = ?
            """,
            (
                device_name,
                device_model,
                device_os,
                os_version,
                now,
                device_id,
            ),
        )

        return DeviceRepository.get_by_id(
            device_id
        )

    # ============================================================
    # ACTIVE
    # ============================================================

    @staticmethod
    def set_active(
        device_id: int,
        is_active: bool,
    ):

        db.execute(
            """
            UPDATE devices_v2
            SET is_active = ?
            WHERE id = ?
            """,
            (
                int(is_active),
                device_id,
            ),
        )

    # ============================================================
    # DEVICE CLIENTS
    # ============================================================

    @staticmethod
    def get_clients(
        device_id: int,
    ) -> list[DeviceClient]:

        rows = db.fetchall(
            """
            SELECT *
            FROM device_clients
            WHERE device_id = ?
            ORDER BY last_seen_at DESC
            """,
            (
                device_id,
            ),
        )

        return [
            DeviceRepository._to_client(
                row
            )
            for row in rows
        ]

    @staticmethod
    def get_client(
        *,
        device_id: int,
        client_identifier: str,
    ) -> DeviceClient | None:

        row = db.fetchone(
            """
            SELECT *
            FROM device_clients
            WHERE device_id = ?
              AND client_identifier = ?
            LIMIT 1
            """,
            (
                device_id,
                client_identifier,
            ),
        )

        if row is None:
            return None

        return DeviceRepository._to_client(
            row
        )

    @staticmethod
    def add_or_update_client(
        *,
        device_id: int,
        client_identifier: str,
        client_app: str | None = None,
        client_version: str | None = None,
    ) -> DeviceClient:

        existing = (
            DeviceRepository.get_client(
                device_id=device_id,
                client_identifier=(
                    client_identifier
                ),
            )
        )

        now = int(
            datetime.now().timestamp()
        )

        if existing is not None:

            db.execute(
                """
                UPDATE device_clients
                SET
                    client_app = COALESCE(
                        ?,
                        client_app
                    ),

                    client_version = COALESCE(
                        ?,
                        client_version
                    ),

                    last_seen_at = ?

                WHERE id = ?
                """,
                (
                    client_app,
                    client_version,
                    now,
                    existing.id,
                ),
            )

            row = db.fetchone(
                """
                SELECT *
                FROM device_clients
                WHERE id = ?
                """,
                (
                    existing.id,
                ),
            )

            return DeviceRepository._to_client(
                row
            )

        db.execute(
            """
            INSERT INTO device_clients
            (
                device_id,
                client_app,
                client_version,
                client_identifier,
                first_seen_at,
                last_seen_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                device_id,
                client_app,
                client_version,
                client_identifier,
                now,
                now,
            ),
        )

        row = db.fetchone(
            """
            SELECT *
            FROM device_clients
            WHERE id = last_insert_rowid()
            """
        )

        return DeviceRepository._to_client(
            row
        )


device_repo = DeviceRepository()