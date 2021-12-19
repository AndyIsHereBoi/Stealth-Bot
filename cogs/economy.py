import errors
import random
import typing
import discord

from discord.ext import commands, menus
from helpers.context import CustomContext


def setup(client):
    client.add_cog(Economy(client))


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
        return await self.client.db.fetchval("SELECT balance FROM economy WHERE user_id = $1", user)

    async def set_money(self, user: int, amount: int):
        """Set a user's wallet to a specific amount"""
        await self.client.db.execute("UPDATE economy SET balance = $1 WHERE user_id = $2", amount, user)
        return await self.client.db.fetchval("SELECT balance FROM economy WHERE user_id = $1", user)

    async def remove_money(self, user: int, amount: int):
        """Remove money from a user's wallet"""
        balance = await self.client.db.fetchval("SELECT balance FROM economy WHERE user_id = $1", user)
        await self.client.db.execute("UPDATE economy SET balance = $1 WHERE user_id = $2", balance - amount, user)
        return await self.client.db.fetchval("SELECT balance FROM economy WHERE user_id = $1", user)

    @commands.command(
        help="Creates a balance for you if you don't have one.",
        aliases=['begin'])
    async def start(self, ctx: CustomContext) -> discord.Message:
        if await self.client.db.fetchval("SELECT user_id FROM economy WHERE user_id = $1", ctx.author.id):
            return await ctx.send("You already have a balance.")

        await self.client.db.execute("INSERT INTO economy (user_id, created_at, balance) VALUES ($1, $2, $3)", ctx.author.id, ctx.message.created_at, 0)
        return await ctx.send("You now have a balance.")