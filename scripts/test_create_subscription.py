import asyncio

from app.domain.user import User
from app.repositories.user_repository import users_repo
from app.services.vpn_service import vpn_service


async def main():

    user = users_repo.get_by_telegram(
        111111111
    )

    if user is None:

        user = users_repo.create(
            User(
                id=None,
                telegram_id=111111111,
                username="test_user",
                first_name="Test",
                is_admin=False,
            )
        )

        print(
            f"Создан пользователь: {user.id}"
        )


    config = await vpn_service.create(
        user_id=user.id,
        protocol="wireguard",
        days=30,
    )


    print(
        "\nVPN успешно создан!\n"
    )

    print(
        config
    )


if __name__ == "__main__":
    asyncio.run(main())