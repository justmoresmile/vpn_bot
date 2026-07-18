from app.database.database import db
from pprint import pprint

rows = db.fetchall(
    """
    SELEC
        id,
        user_id,
        client_email,
        status,
        expires_at
    FROM subscriptions
    """
)

for row in rows:
    pprint(dict(row))