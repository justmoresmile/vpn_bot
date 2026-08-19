from app.database.database import db


def create_tables():

    # =========================
    # USERS
    # =========================

    db.execute("""
        CREATE TABLE IF NOT EXISTS users
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            telegram_id INTEGER UNIQUE,

            username TEXT,

            first_name TEXT,

            is_admin INTEGER DEFAULT 0,

            is_blocked INTEGER DEFAULT 0,

            api_key TEXT,

            created_at INTEGER DEFAULT (strftime('%s','now'))
        )
    """)

    # =========================
    # SERVERS
    # =========================

    db.execute("""
        CREATE TABLE IF NOT EXISTS servers
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            country TEXT NOT NULL,

            host TEXT NOT NULL,

            api_url TEXT NOT NULL,

            api_token TEXT NOT NULL,

            wireguard_inbound_id INTEGER NOT NULL,

            enabled INTEGER NOT NULL DEFAULT 1,

            priority INTEGER NOT NULL DEFAULT 100
        )
    """)

    # =========================
    # SUBSCRIPTIONS
    # =========================

    db.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            server_id INTEGER NOT NULL,

            protocol TEXT NOT NULL,

            inbound_id INTEGER NOT NULL,

            client_uuid TEXT NOT NULL,

            client_email TEXT NOT NULL,

            sub_id TEXT,

            subscription_token TEXT UNIQUE,


            config TEXT NOT NULL,

            status TEXT NOT NULL,

            device_limit INTEGER NOT NULL DEFAULT 2,

            created_at INTEGER NOT NULL,

            expires_at INTEGER NOT NULL,

            FOREIGN KEY(user_id)
                REFERENCES users(id),

            FOREIGN KEY(server_id)
                REFERENCES servers(id)
        )
    """)

        # =========================
    # DEVICES
    # =========================

    db.execute("""
        CREATE TABLE IF NOT EXISTS devices
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            subscription_id INTEGER NOT NULL,

            hwid TEXT NOT NULL,

            device_model TEXT,

            device_os TEXT,

            os_version TEXT,

            client_app TEXT,

            client_version TEXT,

            is_active INTEGER NOT NULL DEFAULT 1,

            first_seen_at INTEGER NOT NULL,

            last_seen_at INTEGER NOT NULL,

            UNIQUE(
                subscription_id,
                hwid
            ),

            FOREIGN KEY(subscription_id)
                REFERENCES subscriptions(id)
        )
    """)



    # =========================
    # PAYMENTS
    # =========================

    db.execute("""
        CREATE TABLE IF NOT EXISTS payments
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            protocol TEXT NOT NULL,

            subscription_days INTEGER NOT NULL,

            subscription_id INTEGER,

            amount REAL NOT NULL,

            currency TEXT NOT NULL,

            status TEXT NOT NULL,

            provider TEXT NOT NULL,

            provider_payment_id TEXT UNIQUE,

            confirmation_url TEXT,

            created_at INTEGER NOT NULL,

            paid_at INTEGER,

            updated_at INTEGER,

            FOREIGN KEY(user_id)
                REFERENCES users(id),

            FOREIGN KEY(subscription_id)
                REFERENCES subscriptions(id)
        )
    """)

    # =========================
    # SUBSCRIPTION NOTIFICATIONS
    # =========================

    db.execute("""
        CREATE TABLE IF NOT EXISTS subscription_notifications
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            subscription_id INTEGER NOT NULL,

            notification_type TEXT NOT NULL,

            expires_at INTEGER NOT NULL,

            created_at INTEGER NOT NULL,

            UNIQUE(
                subscription_id,
                notification_type,
                expires_at
            )
        )

    
    """)



 