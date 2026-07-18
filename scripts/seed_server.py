from app.domain.server import Server
from app.repositories.server_repository import server_repo


def main():
    server = Server(
        id=None,
        name="Russia Reality",

        host="panel.crimea-vpn.ru",

        api_url="https://panel.crimea-vpn.ru/KFjO46n1bgoc1AY7yB",
        api_token="qfCUGB3fHpETcGIb8MEPbdZdjxhSlY83gbOGN29cXO4vBreC",

        country="RU",

        enabled=True,
        )

    server = server_repo.create(server)

    print(f"Сервер добавлен. ID = {server.id}")


if __name__ == "__main__":
    main()