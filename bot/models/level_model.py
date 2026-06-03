from __future__ import annotations

from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from bot.services.level_service import LevelService

class LevelModel:
    def __init__(
        self, 
        level: LevelService,
        config: dict,
        data: dict, 
        guild_id: int,
        user_id: int
    ):
        self.__service = level

        self.__config = config

        self.guild_id = guild_id
        self.user_id = user_id
        
        self.level: int = data.get("level", 1)
        self.exp: int = data.get("exp", 0)

        self.cooldown_per_msg = self.__config.get("cooldown_between_msgs", 20)
        self.exp_per_msg = self.__config.get("exp_per_msg", 10)
        self.starter_xp = self.__config.get("starter_xp", 100)

    @property
    def exp_goal(self) -> int:
        return self.starter_xp * self.level

    @property
    def progress(self) -> float:
        return min(self.exp / self.exp_goal, 1)

    @property
    def remaining_exp(self) -> int | None:
        return self.exp_goal - self.exp


    async def add_exp(self, exp: int) -> LevelModel:
        return await self.__service.add_exp(self.guild_id, self.user_id, exp)