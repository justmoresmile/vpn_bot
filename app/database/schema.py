from app.database.database import db


def create_tables():

    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL,
        username TEXT,
        first_name TEXT,
        is_admin INTEGER DEFAULT 0
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER NOT NULL,

        protocol TEXT NOT NULL,
        inbound_id INTEGER NOT NULL,

        client_uuid TEXT NOT NULL,
        client_email TEXT NOT NULL,

        sub_id TEXT,

        config TEXT NOT NULL,

        status TEXT NOT NULL,

        created_at INTEGER NOT NULL,
        expires_at INTEGER NOT NULL,

        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        currency TEXT NOT NULL,
        status TEXT NOT NULL,
        provider TEXT NOT NULL,
        created_at INTEGER NOT NULL,

        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)