import errors
import random
import discord
import asyncio

from discord.ext import commands, menus
from helpers.context import CustomContext
from discord.ext.menus.views import ViewMenuPages
from discord.ext.commands.cooldowns import BucketType
from helpers.decorators import has_started, has_ref_started


def setup(client):
    client.add_cog(Economy(client))


class RichestUsersEmbedPage(menus.ListPageSource):
    def __init__(self, data, guild):
        self.data = data
        self.guild = guild
        super().__init__(data, per_page=10)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        colors = [0x910023, 0xA523FF]
        color = random.choice(colors)

        embed = discord.Embed(title=f"Richest users in {self.guild.name}",
                              description="\n".join(f'{i + 1}. {v}' for i, v in enumerate(entries, start=offset)),
                              timestamp=discord.utils.utcnow(), color=color)
        embed.set_footer(text=f"Remember this is wallets not banks")

        if self.guild.icon:
            embed.set_thumbnail(url=self.guild.icon.url)

        return embed


class Economy(commands.Cog):
    """Economy commands"""

    def __init__(self, client):
        self.client = client
        self.hidden = True
        self.select_emoji = "<:money_with_wings:903620152606744586>"
        self.select_brief = "Economy commands."

    async def add_money(self, user: int, amount: int):
        """Add money to a user's wallet"""
        balance = await self.client.db.fetchval("SELECT balance FROM economy WHERE user_id = $1", user)
        await self.client.db.execute("UPDATE economy SET balance = $1 WHERE user_id = $2", balance + amount, user)