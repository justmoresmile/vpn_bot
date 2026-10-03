import sqlite3
import threading
from contextlib import contextmanager

from app.config import settings


class Database:
    def __init__(self):
        self.connection = sqlite3.connect(
            settings.database_path,
            check_same_thread=False,
            timeout=30,
        )

        self.connection.row_factory = sqlite3.Row

        self.connection.execute(
            "PRAGMA journal_mode=WAL"
        )
        self.connection.execute(
            "PRAGMA synchronous=NORMAL"
        )
        self.connection.execute(
            "PRAGMA foreign_keys=ON"
        )

        self._lock = threading.RLock()

    def execute(
        self,
        query: str,
        params: tuple = (),
    ):
        with self._lock:
            cursor = self.connection.cursor()

            cursor.execute(
                query,
                params,
            )

            self.connection.commit()

            return cursor

    def fetchone(
        self,
        query: str,
        params: tuple = (),
    ):
        with self._lock:
            cursor = self.connection.cursor()

            cursor.execute(
                query,
                params,
            )

            return cursor.fetchone()

    def fetchall(
        self,
        query: str,
        params: tuple = (),
    ):
        with self._lock:
            cursor = self.connection.cursor()

            cursor.execute(
                query,
                params,
            )

            return cursor.fetchall()

    @contextmanager
    def transaction(self):
        """
        Atomic database transaction.

        BEGIN IMMEDIATE is important for balance operations:
        SQLite acquires a write lock before the balance is read/changed.
        """

        with self._lock:

            cursor = self.connection.cursor()

            try:

                cursor.execute(
                    "BEGIN IMMEDIATE"
                )

                yield cursor

                self.connection.commit()

            except Exception:

                self.connection.rollback()

                raise

            finally:

                cursor.close()

    def close(self):
        with self._lock:
            self.connection.close()


db = Database()
