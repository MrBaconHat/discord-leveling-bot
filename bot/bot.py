import discord
from discord.ext import commands

import os

# NestIO for reading/writing files
from nestio.env import Env
from nestio.files import JSON
from nestio.files import TOML

# Colors
from colorama import Fore, Style, init
init(autoreset=True)

# --- Services -----------------
from bot.services.level_service import LevelService


class MyBot(commands.Bot):
    def __init__(self):
        
        self.__env = Env()
        
        self.config = TOML('data/level_config.toml')

        self.level_service = LevelService(self)
        
        super().__init__(command_prefix='!', intents=discord.Intents.all(), help_command=None)


    async def setup_hook(self):
        cogs = os.listdir("bot/cogs")
        for cog in cogs:
            
            if cog.endswith(".py") and not cog.startswith("_"):
                
                try:
                    await self.load_extension(f"bot.cogs.{cog[:-3]}")
                    print(
                        Fore.GREEN + Style.BRIGHT +
                        f"Loaded cog {cog[:-3]}"
                    )
                    
                except Exception as e:
                    print(
                        Fore.RED + Style.BRIGHT +
                        f"Failed to load cog {cog[:-3]}: {e}"
                    )

    async def on_ready(self):
        await self.tree.sync()
        print(
            Fore.GREEN + Style.BRIGHT +
            f"Logged in as {self.user.name} ({self.user.id})"
        )

    async def start_bot(self):
        token = self.__env.get("BOT_TOKEN")
        if token is None:
            print(
                Fore.RED + Style.BRIGHT +
                "No bot token found in .env file"
            )
            return

        await self.start(token)


bot = MyBot()