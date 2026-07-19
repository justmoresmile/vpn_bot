from app.database.database import db


def print_table(name: str):

    print("\n======================")
    print(name)
    print("======================")

    rows = db.fetchall(
        f"SELECT * FROM {name}"
    )

    for row in rows:
        print(dict(row))


if __name__ == "__main__":

    tables = [
        "users",
        "subscriptions",
        "payments",
    ]

    for table in tables:
        print_table(table)