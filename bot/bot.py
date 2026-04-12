import os

import discord
from discord.ext import commands

# ========== BOT UTILITIES ==========
from utils.env import Env
from utils.file import JsonFile, TomlFile

class LevelConfig:
    def __init__(self):
        raw_config = TomlFile("level.toml").read_sync()
        print(raw_config)
        for key, value in raw_config.items():
            setattr(self, key, value)

    def get(self, key: str, default=None):
        return getattr(self, key, default)
        

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix='!', intents=intents
        )
        
        self.ENV = Env()
        self.CONFIG = LevelConfig()
        self.json = JsonFile
        self.toml = TomlFile

    async def load_cogs(self):
        print("Loading cogs...")
        cogs = os.listdir("bot/cogs")
        print(cogs)
        for cog in cogs:
            print(cog)
            if cog in ["__init__.py", "__pycache__"]:
                print("Skipping:", cog)
                continue 

            try:
                print("Loading:", cog)
                await self.load_extension(f"bot.cogs.{cog[:-3]}")
                print("Loaded:", cog)

            except Exception as e:
                print("Failed to load:", cog)
                print(f"Error loading {cog}: {e}")
        
    async def setup_hook(self):
        await self.load_cogs()

    async def on_ready(self):
        print("Successfuly logged in as", self.user)

    async def run_bot(self):
        await self.start(self.ENV.get("BOT_TOKEN", ""))