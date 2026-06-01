import discord
from discord.ext import commands, tasks
from discord import app_commands

from typing import Optional


class ExpCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.level = self.bot.level
        self.config: dict[str, int] = {
            "starter_xp": 100,
            "exp_per_msg": 10,
            "cooldown_between_msgs": 20
        }

    async def cog_load(self): self.config_updater.start()
    async def cog_unload(self): self.config_updater.cancel()

    @tasks.loop(seconds=10)
    async def config_updater(self):
        config = self.bot.config
        level_config = await config.get("levels")
        if level_config:
            self.config.update(level_config)

    @app_commands.command(
        name="level",
        description="Shows the current level and exp"
    )
    @app_commands.describe(
        user="The user to show the level and exp for"
    )
    async def check_level(self, interaction: discord.Interaction, user: Optional[discord.User]):
        user = user or interaction.user
        guild = interaction.guild
        if user.bot:
            await interaction.response.send_message(
                "Bots don't have levels",
                ephemeral=True
            )

        data_path = f"{guild.id}.{user.id}"

        level = await self.level.get(f"{data_path}.level", 1)
        exp = await self.level.get(f"{data_path}.xp", 0)

        starter_exp = self.config["starter_xp"]
        exp_goal = starter_exp * level

        embed = discord.Embed(
            title=f"📊 {user.display_name}'s Level",
            color=discord.Color.blurple()
        )

        embed.set_thumbnail(url=user.display_avatar.url)

        embed.add_field(
            name="🏆 Level",
            value=f"`{level}`",
            inline=True
        )

        embed.add_field(
            name="✨ XP",
            value=f"`{exp:,}/{exp_goal:,}`",
            inline=True
        )

        progress = min(exp / exp_goal, 1)
        filled = int(progress * 10)
        bar = "█" * filled + "░" * (10 - filled)

        embed.add_field(
            name="📈 Progress",
            value=f"`{bar}` ({progress:.0%})",
            inline=False
        )
        embed.set_footer(
            text=f"Requested by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(ExpCommands(bot))