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

            email TEXT,

            username TEXT,

            first_name TEXT,

            is_admin INTEGER DEFAULT 0,

            is_blocked INTEGER DEFAULT 0,

            api_key TEXT,

            vpn_provider TEXT,

            provider_user_id INTEGER,

            provider_username TEXT,

            balance_kopecks INTEGER NOT NULL DEFAULT 0,

            created_at INTEGER DEFAULT (strftime('%s','now'))
        )
    """)

    # =========================
    # USERS MIGRATIONS
    # =========================

    user_columns = {
        row["name"]
        for row in db.fetchall(
            "PRAGMA table_info(users)"
        )
    }

    if "email" not in user_columns:
        db.execute("""
            ALTER TABLE users
            ADD COLUMN email TEXT
        """)

    if "vpn_provider" not in user_columns:
        db.execute("""
            ALTER TABLE users
            ADD COLUMN vpn_provider TEXT
        """)

    if "provider_user_id" not in user_columns:
        db.execute("""
            ALTER TABLE users
            ADD COLUMN provider_user_id INTEGER
        """)

    if "provider_username" not in user_columns:
        db.execute("""
            ALTER TABLE users
            ADD COLUMN provider_username TEXT
        """)

    if "balance_kopecks" not in user_columns:
        db.execute("""
            ALTER TABLE users
            ADD COLUMN balance_kopecks INTEGER NOT NULL DEFAULT 0
        """)

    db.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS
        idx_users_email_unique
        ON users(LOWER(email))
        WHERE email IS NOT NULL
    """)

    # =========================
    # EMAIL AUTH CODES
    # =========================

    db.execute("""
        CREATE TABLE IF NOT EXISTS email_auth_codes
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            email TEXT NOT NULL,

            code_hash TEXT NOT NULL,

            expires_at INTEGER NOT NULL,

            attempts INTEGER NOT NULL DEFAULT 0,

            used_at INTEGER,

            created_at INTEGER NOT NULL
                DEFAULT (strftime('%s','now'))
        )
    """)

    db.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_email_auth_codes_email
        ON email_auth_codes(email)
    """)

    db.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_email_auth_codes_expires
        ON email_auth_codes(expires_at)
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
    # USER TRIAL MIGRATIONS
    # =========================

    user_columns = {
        row["name"]
        for row in db.fetchall(
            "PRAGMA table_info(users)"
        )
    }

    if "trial_used" not in user_columns:
        db.execute("""
            ALTER TABLE users
            ADD COLUMN trial_used INTEGER NOT NULL DEFAULT 0
        """)

    if "trial_started_at" not in user_columns:
        db.execute("""
            ALTER TABLE users
            ADD COLUMN trial_started_at INTEGER
        """)

    if "trial_ends_at" not in user_columns:
        db.execute("""
            ALTER TABLE users
            ADD COLUMN trial_ends_at INTEGER
        """)

    # =========================
    # SUBSCRIPTIONS
    # =========================

    db.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            provider TEXT NOT NULL
                DEFAULT 'remnawave',

            protocol TEXT NOT NULL,

            status TEXT NOT NULL,

            device_limit INTEGER NOT NULL
                DEFAULT 2,

            subscription_token TEXT UNIQUE,

            created_at INTEGER NOT NULL,

            expires_at INTEGER NOT NULL,

            billing_mode TEXT NOT NULL DEFAULT 'fixed',

            paid_until INTEGER,

            billing_day_index INTEGER NOT NULL DEFAULT 0,

            billing_enabled INTEGER NOT NULL DEFAULT 1,

            server_id INTEGER,

            inbound_id INTEGER,

            client_uuid TEXT,

            client_email TEXT,

            sub_id TEXT,

            config TEXT NOT NULL
                DEFAULT '',

            FOREIGN KEY(user_id)
                REFERENCES users(id),

            FOREIGN KEY(server_id)
                REFERENCES servers(id)
        )
    """)

    # =========================
    # SUBSCRIPTIONS MIGRATIONS
    # =========================

    subscription_columns = {
        row["name"]
        for row in db.fetchall(
            "PRAGMA table_info(subscriptions)"
        )
    }

    if "billing_mode" not in subscription_columns:
        db.execute("""
            ALTER TABLE subscriptions
            ADD COLUMN billing_mode TEXT NOT NULL DEFAULT 'fixed'
        """)

    if "paid_until" not in subscription_columns:
        db.execute("""
            ALTER TABLE subscriptions
            ADD COLUMN paid_until INTEGER
        """)

    if "billing_day_index" not in subscription_columns:
        db.execute("""
            ALTER TABLE subscriptions
            ADD COLUMN billing_day_index INTEGER NOT NULL DEFAULT 0
        """)

    if "billing_enabled" not in subscription_columns:
        db.execute("""
            ALTER TABLE subscriptions
            ADD COLUMN billing_enabled INTEGER NOT NULL DEFAULT 1
        """)

    if "device_limit_locked_until" not in subscription_columns:
        db.execute("""
            ALTER TABLE subscriptions
            ADD COLUMN device_limit_locked_until INTEGER
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

            amount_kopecks INTEGER,

            payment_type TEXT NOT NULL DEFAULT 'subscription',

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
    # WALLET TRANSACTIONS
    # =========================

    db.execute("""
        CREATE TABLE IF NOT EXISTS wallet_transactions
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            type TEXT NOT NULL,

            amount_kopecks INTEGER NOT NULL,

            balance_after_kopecks INTEGER NOT NULL,

            payment_id INTEGER,

            description TEXT,

            created_at INTEGER NOT NULL
                DEFAULT (strftime('%s','now')),

            FOREIGN KEY(user_id)
                REFERENCES users(id),

            FOREIGN KEY(payment_id)
                REFERENCES payments(id)
        )
    """)

    db.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_wallet_transactions_user
        ON wallet_transactions(user_id)
    """)

    db.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_wallet_transactions_created
        ON wallet_transactions(created_at)
    """)

    # =========================
    # PAYMENTS MIGRATIONS
    # =========================

    payment_columns = {
        row["name"]
        for row in db.fetchall(
            "PRAGMA table_info(payments)"
        )
    }

    if "amount_kopecks" not in payment_columns:
        db.execute("""
            ALTER TABLE payments
            ADD COLUMN amount_kopecks INTEGER
        """)

    if "payment_type" not in payment_columns:
        db.execute("""
            ALTER TABLE payments
            ADD COLUMN payment_type TEXT NOT NULL
            DEFAULT 'subscription'
        """)

    db.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS
        idx_wallet_transactions_payment_unique
        ON wallet_transactions(payment_id)
        WHERE payment_id IS NOT NULL
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