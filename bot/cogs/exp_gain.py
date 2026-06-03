from discord.ext import commands, tasks

import time
import traceback

# --- Utils -----------------
from bot.utils.embed import level_up_embed


class ExpHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.level_service = bot.level_service

        # Default config in case the config file is empty
        self.level_config: dict[str, int] = {
            "starter_xp": 100,
            "exp_per_msg": 10,
            "cooldown_between_msgs": 20
        }

        # Cooldowns for each user
        self.cooldowns: dict[str, int] = {}

    async def cog_load(self): self.config_updater.start()
    async def cog_unload(self): self.config_updater.cancel()

    @tasks.loop(seconds=10)
    async def config_updater(self):
        config = self.bot.config
        level_config = await config.get("levels")
        if level_config:
            self.level_config.update(level_config)

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from bots
        if message.author.bot:
            return

        # Get user id in string
        user_id = str(message.author.id)

        # Check if user is on cooldown
        if (
            user_id in self.cooldowns
            and self.cooldowns[user_id] > time.time()
        ):
            # If user is on cooldown, ignore the message
            return

        # Get the user's current level and exp
        profile = await self.level_service.get_user(message.guild.id, message.author.id)

        # Add exp to the user
        new_profile = await profile.add_exp(profile.exp_per_msg)

        # Check if the user has reached the exp goal
        if new_profile.level >= profile.exp_goal:
            # If the user has reached the exp goal, send a level up message
            await message.channel.send(embed=level_up_embed(message.author, new_profile.level))

        # Set the cooldown
        self.cooldowns[user_id] = int(time.time() + self.level_config["cooldown_between_msgs"])


async def setup(bot: commands.Bot):
    await bot.add_cog(ExpHandler(bot))