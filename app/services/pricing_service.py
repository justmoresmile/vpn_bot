MIN_DEVICE_LIMIT = 1
MAX_DEVICE_LIMIT = 10

TRIAL_DEVICE_LIMIT = 1


DAILY_PRICES_KOPECKS = {
    1: 300,
    2: 500,
    3: 800,
    4: 1000,
    5: 1300,
    6: 1400,
    7: 1600,
    8: 1800,
    9: 1900,
    10: 2100,
}


def normalize_device_limit(
    device_limit: int | None,
) -> int:

    if device_limit is None:
        return TRIAL_DEVICE_LIMIT

    return max(
        MIN_DEVICE_LIMIT,
        min(
            int(device_limit),
            MAX_DEVICE_LIMIT,
        ),
    )


def get_daily_price_kopecks(
    device_limit: int | None,
) -> int:

    normalized = normalize_device_limit(
        device_limit
    )

    return DAILY_PRICES_KOPECKS[
        normalized
    ]


def get_daily_price_rubles(
    device_limit: int | None,
) -> int:

    return (
        get_daily_price_kopecks(
            device_limit
        )
        // 100
    )
