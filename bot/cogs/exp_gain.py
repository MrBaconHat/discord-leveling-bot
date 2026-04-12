import discord
from discord.ext import commands

import time
import asyncio

from utils.lock import LockManager

class ExpGain(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.__lock = LockManager()
        self.is_ready: bool = False

        self.level_json = None
        
        # User cooldown between each message
        self.user_cooldown = {}

    async def wait_until_ready(self):
        while True:
            if self.is_ready:
                break
            await asyncio.sleep(1)

    async def cog_load(self):
         self.level_json = await self.bot.json("level.json").read()
         self.is_ready = True

    async def _lock(self, user_id):
        return await self.__lock.get_lock(f"exp_gain:{user_id}")

    async def get_user_exp(self, user_id: int):
        return await self.level_json.read(str(user_id), 0)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.wait_until_ready()

        async with await self._lock(message.author.id):
            # Ignore messages from bots
            if message.author.bot:
                return

            # Ignore messages in DMs
            if not message.guild:
                return

            # Ignore messages in channels that are not allowed
            # todo
            if False:
                return

            # Get user cooldown
            user_cooldown_guild =  self.user_cooldown.setdefault(message.guild.id, {})
            user_cooldown = user_cooldown_guild.setdefault(message.author.id, 0)

            sent_at_ts = message.created_at.timestamp()

            if user_cooldown > sent_at_ts:
                return

            print("hi")

async def setup(bot: commands.Bot):
    await bot.add_cog(ExpGain(bot))