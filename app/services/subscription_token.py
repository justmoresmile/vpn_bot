import secrets


def generate_subscription_token(
    length: int = 16,
) -> str:

    alphabet = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
    )

    return "_" + "".join(
        secrets.choice(alphabet)
        for _ in range(length)
    )