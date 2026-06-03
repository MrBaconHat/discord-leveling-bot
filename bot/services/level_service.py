from __future__ import annotations

from typing import TYPE_CHECKING

from nestio.files import JSON, TOML

from bot.models.level_model import LevelModel


class LevelService:
    def __init__(self, bot):
        self.bot = bot
        
        self.level = JSON("data/levels.json")
        self.config = TOML("data/level_config.toml")

    async def get_user(self, guild_id: int, user_id: int) -> LevelModel:
        data = await self.level.get(f"{guild_id}.{user_id}", {})
        config = await self.config.get("levels", {})
        return LevelModel(self, config, data, guild_id, user_id)

    async def add_exp(self, guild_id: int, user_id: int, exp: int) -> LevelModel:
        current_exp = await self.level.set_default(f"{guild_id}.{user_id}.exp", 0)
        current_level = await self.level.set_default(f"{guild_id}.{user_id}.level", 1)

        starter_exp = await self.config.get("levels.starter_xp", 100)

        level = current_level
        xp = current_exp + exp

        # Calculate the new level for the user if they level up
        while xp >= starter_exp * level:
            xp -= starter_exp * level
            level += 1

        await self.level.set(f"{guild_id}.{user_id}.exp", xp)
        await self.level.set(f"{guild_id}.{user_id}.level", level)

        return LevelModel(self, await self.config.get("levels", {}), {"level": level, "exp": xp}, guild_id, user_id)