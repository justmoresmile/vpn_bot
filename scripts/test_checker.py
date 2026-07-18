import asyncio

from app.services.subscription_checker import subscription_checker


async def main():
    await subscription_checker.run()


asyncio.run(main())