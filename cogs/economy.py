import errors
import random
import discord

from discord.ext import commands, menus
from helpers.context import CustomContext


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

    async def set_money(self, user: int, amount: int):
        """Set a user's wallet to a specific amount"""
        await self.client.db.execute("UPDATE economy SET balance = $1 WHERE user_id = $2", amount, user)

    async def remove_money(self, user: int, amount: int):
        """Remove money from a user's wallet"""
        balance = await self.client.db.fetchval("SELECT balance FROM economy WHERE user_id = $1", user)
        await self.client.db.execute("UPDATE economy SET balance = $1 WHERE user_id = $2", balance - amount, user)

    @commands.command()
    async def start(self, ctx: CustomContext):
        """" Creates a balance for you if you don't have one. """
        if await self.client.db.fetchval("SELECT user_id FROM economy WHERE user_id = $1", ctx.author.id):
            await ctx.send("You already have a balance.")

        else:
            await self.client.db.execute("INSERT INTO economy (user_id, created_at, balance) VALUES ($1, $2, $3)", ctx.author.id, ctx.message.created_at, 0)
            await ctx.send("You now have a balance.")

    @commands.command()
    async def balance(self, ctx: CustomContext, user: discord.Member = None):
        """Check your balance."""
        if user is None:
            user = ctx.author

        balance = await self.client.db.fetchval("SELECT balance FROM economy WHERE user_id = $1", user.id)
        if not balance:
            await ctx.send("You don't have a balance.")

        else:
            await ctx.send(f"{user.mention} has {balance} .")