from app.database.database import db


rows = db.fetchall(
    """
    SELECT *
    FROM subscriptions
    """
)

for row in rows:
    print(dict(row))