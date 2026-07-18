from app.database.database import db

db.execute(
    """
    UPDATE servers
    SET api_token = ?
    WHERE id = 1
    """,
    (
        "n76xXdruzoXajAjZYnAAZrScbizYo191wg4MHUfCFEZiNUE2",
    ),
)

print("Токен обновлен.")