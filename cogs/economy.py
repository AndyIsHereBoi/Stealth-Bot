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

    @commands.command(
        help="Shows you the balance of the specified member.",
        aliases=['bal', 'money'])
    async def balance(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None) -> discord.Message:
        await ctx.trigger_typing()

        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        if member.bot:
            return await ctx.send("Bots don't have a balance.")

        if not await self.client.db.fetchval("SELECT user_id FROM economy WHERE user_id = $1", member.id):
            return await ctx.send(f"{'You dont' if member.id == ctx.author.id else f'{member.mention} doesnt'} have a balance.")

        balance = await self.client.db.fetchval("SELECT balance FROM economy WHERE user_id = $1", member.id)
        await ctx.send(f"{'You have' if member.id == ctx.author.id else f'{member.mention} has'} {balance:,} money.")

    @commands.group(
        invoke_without_command=True,
        help="Economy commands for the owner.",
        aliases=['admineco', 'ecoadmin', 'eco_admin'])
    async def admin_eco(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None) -> discord.Message:
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @admin_eco.command(
        name="add",
        help="Adds money to the specified member's balance.",
        aliases=['give', '+'])
    async def admin_eco_add(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User]], amount: int) -> discord.Message:
        await ctx.trigger_typing()

        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        if member.bot:
            return await ctx.send("Bots don't have a balance.")

        if not await self.client.db.fetchval("SELECT user_id FROM economy WHERE user_id = $1", member.id):
            return await ctx.send(f"{'You dont' if member.id == ctx.author.id else f'{member.mention} doesnt'} have a balance.")

        return await ctx.send(f"Successfully added {amount:,} money to {'your' if member.id == ctx.author.id else f'{member.mention}s'} balance. {'You' if member.id == ctx.author.id else 'They'} now have {await self.add_money(member.id, amount):,} money.")

    @admin_eco.command(
        name="remove",
        help="Removes  money from the specified member's balance.",
        aliases=['delete', '-'])
    async def admin_eco_remove(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User]], amount: int) -> discord.Message:
        await ctx.trigger_typing()

        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        if member.bot:
            return await ctx.send("Bots don't have a balance.")

        if not await self.client.db.fetchval("SELECT user_id FROM economy WHERE user_id = $1", member.id):
            return await ctx.send(f"{'You dont' if member.id == ctx.author.id else f'{member.mention} doesnt'} have a balance.")

        return await ctx.send(f"Successfully removed {amount:,} money from {'your' if member.id == ctx.author.id else f'{member.mention}s'} balance. {'You' if member.id == ctx.author.id else 'They'} now have {await self.remove_money(member.id, amount):,} money.")
