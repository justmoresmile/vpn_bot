import sys

from app.database.database import db


subscription_id = int(sys.argv[1])

db.execute(
    """
    UPDATE subscriptions
    SET
        expires_at = strftime('%s','now') - 60,
        status = 'active'
    WHERE id = ?
    """,
    (subscription_id,),
)

print(f"Subscription #{subscription_id} expired.")