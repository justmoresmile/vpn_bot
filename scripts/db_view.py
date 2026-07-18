from app.database.database import db


def print_table(name: str):
    rows = db.fetchall(f"SELECT * FROM {name}")

    print(f"\n{name.upper()} ({len(rows)} записей)")
    print("-" * 80)

    if not rows:
        print("Таблица пустая.")
        return

    for row in rows:
        print(dict(row))


if __name__ == "__main__":
    print_table("servers")
    print_table("users")
    print_table("subscriptions")
    print_table("payments")