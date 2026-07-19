import sqlite3

from app.config import settings


class Database:
    def __init__(self):
        self.connection = sqlite3.connect(
          settings.database_path,
            check_same_thread=False,
            timeout=30,
        )

        self.connection.row_factory = sqlite3.Row

        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA synchronous=NORMAL")
        self.connection.execute("PRAGMA foreign_keys=ON")

        self.connection.row_factory = sqlite3.Row

        # Включаем поддержку внешних ключей
        self.connection.execute("PRAGMA foreign_keys = ON")

    def execute(self, query: str, params: tuple = ()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor

    def fetchone(self, query: str, params: tuple = ()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def fetchall(self, query: str, params: tuple = ()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def close(self):
        self.connection.close()


db = Database()