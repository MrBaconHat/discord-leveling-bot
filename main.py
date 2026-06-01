from bot.bot import bot
import asyncio


async def main():
    await bot.start_bot()

asyncio.run(main())