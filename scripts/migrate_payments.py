from app.database.database import db


def migrate():

    columns = [
        (
            "protocol",
            "TEXT NOT NULL DEFAULT 'vless'"
        ),
        (
            "subscription_days",
            "INTEGER NOT NULL DEFAULT 30"
        ),
        (
            "provider_payment_id",
            "TEXT"
        ),
        (
            "confirmation_url",
            "TEXT"
        ),
        (
            "paid_at",
            "INTEGER"
        ),
    ]


    existing = db.fetchall(
        "PRAGMA table_info(payments)"
    )

    existing_names = {
        row["name"]
        for row in existing
    }


    for name, definition in columns:

        if name not in existing_names:

            print(
                f"Adding column: {name}"
            )

            db.execute(
                f"""
                ALTER TABLE payments
                ADD COLUMN {name} {definition}
                """
            )

        else:

            print(
                f"Exists: {name}"
            )


    print(
        "Payments migration completed"
    )


if __name__ == "__main__":
    migrate()