from discord.ext import commands, tasks

import time
import traceback

# --- Utils -----------------
from bot.utils.embed import level_up_embed


class ExpHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.level = self.bot.level

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

        # set a default path where user's data will be stored
        data_path = f"{message.guild.id}.{user_id}"

        # Get user's current level and exp
        current_level = await self.level.get(f"{data_path}.level", self.level_config["starter_xp"])
        current_exp = await self.level.get(f"{data_path}.xp", 0)

        # Calculate the exp goal for the next level
        exp_goal = self.level_config["starter_xp"] * current_level

        # Calculate the new exp and level
        new_exp = current_exp + self.level_config["exp_per_msg"]
        new_level = None

        # Check if the user has reached the exp goal
        if new_exp >= exp_goal:
            new_exp = new_exp - exp_goal
            new_level = current_level + 1

        # Update the level and exp
        await self.level.set(f"{data_path}.xp", new_exp)
        if new_level:
            await self.level.set(f"{data_path}.level", new_level)
            # Send a message if the user has leveled up
            await message.channel.send(embed=level_up_embed(message.author, new_level))

        # Set the cooldown
        self.cooldowns[user_id] = int(time.time() + self.level_config["cooldown_between_msgs"])


async def setup(bot: commands.Bot):
    await bot.add_cog(ExpHandler(bot))