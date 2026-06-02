import discord

def level_up_embed(user: discord.Member, level: int) -> discord.Embed:
    embed = discord.Embed(
        title="🎉 Level Up!",
        description=f"{user.mention} reached **Level {level}**!",
        color=discord.Color.gold()
    )

    embed.set_thumbnail(url=user.display_avatar.url)

    return embed