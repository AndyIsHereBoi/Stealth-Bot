import discord

from discord.ext import commands
from helpers.context import CustomContext


def setup(client):
    client.add_cog(Levels(client))


class Levels(commands.Cog):
    """Levelling system."""

    def __init__(self, client):
        self.client = client
        self.hidden = True
        self.select_emoji = "<:lightningbolt:903706434791956561>"
        self.select_brief = "Levelling system."

    async def level_up(self, id: int):
        currentXP = id['xp']
        currentLevel = id['level']

        if currentXP >= round(10 * ((1 + 2) ** (1.5 * 2 - (1 / 100))) + ((((1 - 1) * 5) + 1) / 5) / 3):
            await self.client.db.execute("UPDATE users SET level = $1 WHERE user_id = $2 AND guild_id = $3",
                                         currentLevel + 1, id['user_id'],
                                         id['guild_id'])

            return True  # returns true (the author has levelled up)

        else:
            return False  # returns false (the author hasn't levelled up)
