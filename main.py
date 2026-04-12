import asyncio
from bot.bot import MyBot

async def main():
    bot = MyBot()
    await bot.run_bot()

if __name__ == "__main__":
    asyncio.run(main())