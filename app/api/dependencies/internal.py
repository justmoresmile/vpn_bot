from fastapi import (
    Header,
    HTTPException,
)


from app.config import settings



async def verify_internal_api_key(
    x_api_key: str = Header(...),
):

    if x_api_key != settings.backend_api_key:

        raise HTTPException(
            status_code=401,
            detail="Invalid internal API key",
        )


    return True