import discord
from discord.ext import commands, tasks
from discord import app_commands

from typing import Optional

# --- Utils -----------------
from bot.utils.embed import level_up_embed


class ExpCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.level_service = bot.level_service

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
        level_config = await self.bot.config.get("levels")
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

        profile = await self.level_service.get_user(guild.id, user.id)

        embed = discord.Embed(
            title=f"📊 {user.display_name}'s Level",
            color=discord.Color.blurple()
        )

        embed.set_thumbnail(url=user.display_avatar.url)

        embed.add_field(
            name="🏆 Level",
            value=f"`{profile.level}`",
            inline=True
        )

        embed.add_field(
            name="✨ XP",
            value=f"`{profile.exp:,}/{profile.exp_goal:,}`",
            inline=True
        )

        progress = profile.progress
        filled = int(progress * 10)
        bar = "█" * filled + "░" * (10 - filled)

        embed.add_field(
            name="📈 Progress",
            value=f"`{bar}` ({progress:.0%})",
            inline=True
        )
        embed.set_footer(
            text=f"Requested by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)


    @app_commands.command(
        name="add-exp",
        description="Adds exp to a user"
    )
    @app_commands.describe(
        user="The user to add exp to",
        exp="The amount of exp to add"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def add_exp(self, interaction: discord.Interaction, user: discord.User, exp: int):
        guild = interaction.guild
        if user.bot:
            await interaction.response.send_message(
                "Bots don't have levels", 
                ephemeral=True
            )

        current_profile = await self.level_service.get_user(guild.id, user.id)

        new_profile = await self.level_service.add_exp(guild.id, user.id, exp)

        # Indicator for if user has leveled up!
        if new_profile.level > current_profile.level:
            cmd_channel: discord.TextChannel = self.bot.get_channel(interaction.channel_id)
            if cmd_channel:
                await cmd_channel.send(embed=level_up_embed(user, new_profile.level))
            
        await interaction.response.send_message(
            f"Added **{exp:,}** exp to {user.mention}", 
            ephemeral=True
        )


    @app_commands.command(
        name="reset",
        description="Reset's server's levels for all users"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def reset_levels(self, interaction: discord.Interaction):
        guild = interaction.guild
        await self.level.delete(f"{guild.id}")
        await interaction.response.send_message(
            "Reset all levels for this server",
            ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ExpCommands(bot))