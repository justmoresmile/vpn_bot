from app.database.database import db
import sys
from pathlib import Path

rows = db.fetchall("""
SELECT
    id,
    user_id,
    protocol,
    status,
    created_at,
    expires_at
FROM subscriptions
ORDER BY id
""")

for r in rows:
    print(dict(r))