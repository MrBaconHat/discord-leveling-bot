import traceback

import discord
from discord.ext import commands
from discord import app_commands


class ExceptionHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.bot.tree.on_error = self.on_app_command_error

    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ):
        # Go through the basic errors.
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"⏳ This command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
            return

        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
            return

        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
            return

        
        # Unwrap original exception if present
        if isinstance(error, app_commands.CommandInvokeError):
            error = error.original

        traceback.print_exception(
            type(error),
            error,
            error.__traceback__,
        )

        try:
            message = "❌ An unexpected error occurred."

            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(
                    message,
                    ephemeral=True,
                )

        except Exception:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(ExceptionHandler(bot))