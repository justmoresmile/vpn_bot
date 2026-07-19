from app.database.database import db


rows = db.fetchall(
    "PRAGMA table_info(payments)"
)


for row in rows:
    print(dict(row))