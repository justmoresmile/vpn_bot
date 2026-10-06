from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

import qrcode

from io import BytesIO
from datetime import datetime, timezone

from fastapi.responses import Response

from pydantic import BaseModel, Field

from app.api.schemas.subscription import (
    ConfigResponse,
    RenewResponse,
    SubscriptionResponse,
    SubscriptionUsageResponse,
    SubscriptionDeviceResponse,
    SubscriptionDevicesResponse,
)
from app.repositories.device_repository import (
    device_repo,
)

from app.api.dependencies.auth import (
    get_current_user,
)

from app.domain.user import User

from app.services.subscription_service import (
    subscription_service,
)

from app.services.vpn_service import (
    vpn_service,
)
from app.services.remnawave_service import (
    remnawave_service,
)
from app.services.pricing_service import (
    get_daily_price_kopecks,
    MIN_DEVICE_LIMIT,
    MAX_DEVICE_LIMIT,
)

from app.config import settings



router = APIRouter(
    prefix="/subscription",
    tags=["Subscription"],
)


class DeviceLimitRequest(BaseModel):
    device_limit: int = Field(
        ge=MIN_DEVICE_LIMIT,
        le=MAX_DEVICE_LIMIT,
    )


def check_subscription_owner(
    subscription,
    user: User,
):
    if subscription.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


@router.get(
    "/{subscription_id}",
    response_model=SubscriptionResponse,
)
async def get_subscription(
    subscription_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    subscription = subscription_service.get_by_id(
        subscription_id
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    check_subscription_owner(
        subscription,
        user,
    )

    return SubscriptionResponse(
        id=subscription.id,
        user_id=subscription.user_id,
        protocol=subscription.protocol,
        status=subscription.status.value,
        expires_at=subscription.expires_at,
        client_email=subscription.client_email,
    )


@router.get(
    "/{subscription_id}/config",
    response_model=ConfigResponse,
)
async def get_config(
    subscription_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    subscription = (
        subscription_service
        .get_by_id(
            subscription_id
        )
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    check_subscription_owner(
        subscription,
        user,
    )

    config = await vpn_service.get_config(
        subscription_id
    )

    if not config:
        raise HTTPException(
            status_code=404,
            detail="Subscription config not found",
        )

    return ConfigResponse(
        config=config,
    )


@router.post(
    "/{subscription_id}/renew",
    response_model=RenewResponse,
)
async def renew_subscription(
    subscription_id: int,
    days: int = 30,
    user: User = Depends(
        get_current_user
    ),
):

    subscription = subscription_service.get_by_id(
        subscription_id
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    check_subscription_owner(
        subscription,
        user,
    )

    subscription = await vpn_service.renew(
        subscription_id,
        days,
    )

    return RenewResponse(
        id=subscription.id,
        status=subscription.status.value,
        expires_at=subscription.expires_at,
    )


@router.post(
    "/{subscription_id}/device-limit"
)
async def set_subscription_device_limit(
    subscription_id: int,
    request: DeviceLimitRequest,
    user: User = Depends(
        get_current_user
    ),
):
    subscription = (
        subscription_service.get_by_id(
            subscription_id
        )
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    check_subscription_owner(
        subscription,
        user,
    )

    # --------------------------------------------------------
    # Во время активного trial бесплатно доступно 1 устройство
    # --------------------------------------------------------

    if user.trial_ends_at is not None:

        trial_ends_at = user.trial_ends_at

        if trial_ends_at.tzinfo is None:
            trial_ends_at = (
                trial_ends_at.replace(
                    tzinfo=timezone.utc
                )
            )

        now = datetime.now(
            timezone.utc
        )

        if (
            trial_ends_at > now
            and request.device_limit > 1
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Во время пробного периода "
                    "бесплатно доступно 1 устройство"
                ),
            )

    # --------------------------------------------------------
    # Нельзя уменьшить лимит ниже числа зарегистрированных
    # устройств в Remnawave.
    # --------------------------------------------------------

    if (
        subscription.provider == "remnawave"
        and request.device_limit
        < subscription.device_limit
    ):

        data = (
            remnawave_service.get_devices(
                subscription.user_id
            )
        )

        remote_devices = (
            data.get("devices", [])
            if data
            else []
        ) or []

        registered_count = len(
            [
                device
                for device
                in remote_devices
                if device.get("hwid")
            ]
        )

        if (
            request.device_limit
            < registered_count
        ):

            need_to_delete = (
                registered_count
                - request.device_limit
            )

            if need_to_delete == 1:
                device_word = "устройство"
            elif (
                need_to_delete % 10
                in (2, 3, 4)
                and need_to_delete % 100
                not in (12, 13, 14)
            ):
                device_word = "устройства"
            else:
                device_word = "устройств"

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Сначала удалите "
                    f"{need_to_delete} "
                    f"{device_word}"
                ),
            )


    try:
        subscription = (
            await vpn_service.set_device_limit(
                subscription=subscription,
                device_limit=(
                    request.device_limit
                ),
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    daily_price_kopecks = (
        get_daily_price_kopecks(
            subscription.device_limit
        )
    )

    return {
        "subscription_id": (
            subscription.id
        ),
        "device_limit": (
            subscription.device_limit
        ),
        "daily_price_kopecks": (
            daily_price_kopecks
        ),
        "daily_price_rubles": (
            daily_price_kopecks / 100
        ),
        "paid_until": (
            subscription.paid_until
        ),
        "status": (
            subscription.status.value
        ),
    }


@router.get(
    "/{subscription_id}/usage",
    response_model=SubscriptionUsageResponse,
)
async def get_subscription_usage(
    subscription_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    subscription = (
        subscription_service.get_by_id(
            subscription_id
        )
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    check_subscription_owner(
        subscription,
        user,
    )

    # --------------------------------------------------------
    # REMNAWAVE
    # --------------------------------------------------------

    if (
        subscription.provider
        == "remnawave"
    ):

        from datetime import (
            datetime,
            timezone,
        )

        start = (
            subscription.created_at
            .date()
            .isoformat()
        )

        end = (
            datetime.now(
                timezone.utc
            )
            .date()
            .isoformat()
        )

        data = (
            remnawave_service.get_usage(
                justvpn_user_id=(
                    subscription.user_id
                ),
                start=start,
                end=end,
            )
        )

        if not data:

            return SubscriptionUsageResponse(
                up=0,
                down=0,
                total=0,
            )

        total = int(
            sum(
                data.get(
                    "sparklineData",
                    [],
                )
            )
        )

        return SubscriptionUsageResponse(
            up=0,
            down=0,
            total=total,
        )

    # --------------------------------------------------------
    # LEGACY
    # --------------------------------------------------------

    server = vpn_service._get_server(
        subscription
    )

    xui = await vpn_service._get_xui(
        server
    )

    inbound = await xui.get_inbound_by_id(
        subscription.inbound_id
    )

    if inbound is None:
        raise HTTPException(
            status_code=404,
            detail="Inbound not found",
        )

    traffic = await xui.get_client_traffic(
        inbound=inbound,
        email=subscription.client_email,
    )

    return SubscriptionUsageResponse(
        up=traffic["up"],
        down=traffic["down"],
        total=traffic["total"],
    )


@router.get(
    "/{subscription_id}/qr"
)
async def get_qr(
    subscription_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    subscription = subscription_service.get_by_id(
        subscription_id
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    check_subscription_owner(
        subscription,
        user,
    )

    config = await vpn_service.get_config(
        subscription_id
    )

    if not config:
        raise HTTPException(
            status_code=404,
            detail="Config not found",
        )

    image = qrcode.make(
        config
    )

    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG",
    )

    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="image/png",
    )


@router.get(
    "/{subscription_id}/file"
)
async def download_file(
    subscription_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    subscription = subscription_service.get_by_id(
        subscription_id
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    check_subscription_owner(
        subscription,
        user,
    )

    filename, content = await vpn_service.get_file(
        subscription
    )

    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )


@router.get(
    "/{subscription_id}/devices",
    response_model=SubscriptionDevicesResponse,
)
async def get_subscription_devices(
    subscription_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    subscription = (
        subscription_service.get_by_id(
            subscription_id
        )
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    check_subscription_owner(
        subscription,
        user,
    )

    # --------------------------------------------------------
    # REMNAWAVE
    # --------------------------------------------------------

    if subscription.provider == "remnawave":

        data = remnawave_service.get_devices(
            subscription.user_id
        )

        if not data:
            return SubscriptionDevicesResponse(
                count=0,
                limit=subscription.device_limit,
                devices=[],
            )

        remote_devices = (
            data.get("devices", [])
            or []
        )

        result = []

        for device in remote_devices:

            hwid = device.get("hwid")

            last_seen = (
                device.get("updatedAt")
                or device.get("createdAt")
            )

            # Response schema requires both fields.
            # Ignore malformed Remnawave records rather
            # than returning invalid API data.
            if not hwid or not last_seen:
                continue

            result.append(
                SubscriptionDeviceResponse(
                    id=str(hwid),
                    model=device.get(
                        "deviceModel"
                    ),
                    os=device.get(
                        "platform"
                    ),
                    os_version=device.get(
                        "osVersion"
                    ),
                    client_app=device.get(
                        "userAgent"
                    ),
                    client_version=None,
                    is_active=True,
                    last_seen_at=last_seen,
                )
            )

        return SubscriptionDevicesResponse(
            count=len(result),
            limit=subscription.device_limit,
            devices=result,
        )

    # --------------------------------------------------------
    # LEGACY
    # --------------------------------------------------------

    devices = (
        device_repo.get_by_subscription(
            subscription.id,
            active_only=True,
        )
    )

    result = []

    for device in devices:

        clients = device_repo.get_clients(
            device.id
        )

        primary_client = (
            clients[0]
            if clients
            else None
        )

        result.append(
            SubscriptionDeviceResponse(
                id=str(device.id),
                model=(
                    device.device_name
                    or device.device_model
                ),
                os=device.device_os,
                os_version=device.os_version,
                client_app=(
                    primary_client.client_app
                    if primary_client
                    else None
                ),
                client_version=(
                    primary_client.client_version
                    if primary_client
                    else None
                ),
                is_active=device.is_active,
                last_seen_at=device.last_seen_at,
            )
        )

    return SubscriptionDevicesResponse(
        count=len(result),
        limit=subscription.device_limit,
        devices=result,
    )


@router.delete(
    "/{subscription_id}/devices/{hwid}"
)
async def delete_subscription_device(
    subscription_id: int,
    hwid: str,
    user: User = Depends(
        get_current_user
    ),
):

    subscription = (
        subscription_service.get_by_id(
            subscription_id
        )
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    check_subscription_owner(
        subscription,
        user,
    )

    if subscription.provider != "remnawave":
        raise HTTPException(
            status_code=400,
            detail=(
                "Device deletion is only available "
                "for Remnawave subscriptions"
            ),
        )

    # --------------------------------------------------------
    # Проверяем, что HWID действительно принадлежит
    # текущему пользователю.
    # --------------------------------------------------------

    devices_data = (
        remnawave_service.get_devices(
            subscription.user_id
        )
    )

    remote_devices = (
        devices_data.get("devices", [])
        if devices_data
        else []
    ) or []

    hwid_exists = any(
        str(device.get("hwid")) == hwid
        for device in remote_devices
        if device.get("hwid")
    )

    if not hwid_exists:
        raise HTTPException(
            status_code=404,
            detail="Device not found",
        )


    try:

        result = remnawave_service.delete_device(
            justvpn_user_id=(
                subscription.user_id
            ),
            hwid=hwid,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception:

        logger.exception(
            "Failed to delete Remnawave device "
            "subscription={} user={} hwid={}",
            subscription.id,
            subscription.user_id,
            hwid,
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Не удалось удалить устройство. "
                "Попробуйте ещё раз позже."
            ),
        )

    return {
        "status": "deleted",
        "subscription_id": (
            subscription.id
        ),
        "hwid": hwid,
        "provider_result": result,
    }


@router.get(
    "/{subscription_id}/link",
    response_model=ConfigResponse,
)
async def get_subscription_link(
    subscription_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    subscription = (
        subscription_service.get_by_id(
            subscription_id
        )
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    check_subscription_owner(
        subscription,
        user,
    )

    if subscription.protocol != "vless":
        raise HTTPException(
            status_code=400,
            detail=(
                "Subscription link is "
                "available only for VLESS"
            ),
        )

    link = await vpn_service.get_config(
        subscription_id
    )

    if not link:
        raise HTTPException(
            status_code=404,
            detail="Subscription link not found",
        )

    return ConfigResponse(
        config=link,
    )
