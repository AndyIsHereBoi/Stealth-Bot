import typing
import discord
import contextlib

from discord.ext import commands
from ._base import ModerationBase

class Announce(ModerationBase):

    @commands.group(
        invoke_without_command=True,
        help="Announces a message to the server.")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def announce(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @announce.command(
        help="Pings @everyone and announces the message to the specified channel. If no channel is specified, it will send it to the current one.")
    async def everyone(self, ctx, channel: typing.Optional[discord.TextChannel], *, message: str):
        if not channel:
            channel = ctx.channel

        if len(message) > 1500:
            return await ctx.send("Woah that message is over 1500 characters long! Please make it shorter.")

        message = f"""
    ~~−−−−~~**[** @everyone **]**~~−−−−~~

    Hello everyone,
    {message}

    Best regards, {ctx.author.display_name}."""

        delete_confirmation = await ctx.confirm("Would you like me to delete your message as well?",
                                                delete_after_confirm=True, delete_after_cancel=True,
                                                delete_after_timeout=True)
        if not delete_confirmation:
            with contextlib.suppress(discord.HTTPException, discord.Forbidden):
                await ctx.message.add_reaction("<:greenTick:895688440690147370>")

        else:
            with contextlib.suppress(discord.HTTPException, discord.Forbidden):
                await ctx.message.delete()

        return await channel.send(message,
                                  allowed_mentions=discord.AllowedMentions(everyone=True, replied_user=True, roles=True,
                                                                           users=True))

    @announce.command(
        help="Pings @here and announces the message to the specified channel. If no channel is specified, it will send it to the current one.")
    async def here(self, ctx, channel: typing.Optional[discord.TextChannel], *, message: str):
        if not channel:
            channel = ctx.channel

        if len(message) > 1500:
            return await ctx.send("Woah that message is over 1500 characters long! Please make it shorter.")

        message = f"""
    ~~−−−−~~**[** @here **]**~~−−−−~~

    Hello everyone,
    {message}

    Best regards, {ctx.author.display_name}."""

        delete_confirmation = await ctx.confirm("Would you like me to delete your message as well?",
                                                delete_after_confirm=True, delete_after_cancel=True,
                                                delete_after_timeout=True)
        if not delete_confirmation:
            with contextlib.suppress(discord.HTTPException, discord.Forbidden):
                await ctx.message.add_reaction("<:greenTick:895688440690147370>")

        else:
            with contextlib.suppress(discord.HTTPException, discord.Forbidden):
                await ctx.message.delete()

        return await channel.send(message,
                                  allowed_mentions=discord.AllowedMentions(everyone=True, replied_user=True, roles=True,
                                                                           users=True))

    @announce.command(
        help="Pings the specified role and announces the message to the specified channel. If no channel is specified, it will send it to the current one.")
    async def role(self, ctx, role: typing.Optional[discord.Role], channel: typing.Optional[discord.TextChannel], *,
                   message: str):
        if not role:
            role = ctx.guild.default_role

        if not channel:
            channel = ctx.channel

        if len(message) > 1500:
            return await ctx.send("Woah that message is over 1500 characters long! Please make it shorter.")

        message = f"""
    ~~−−−−~~**[** {role.mention} **]**~~−−−−~~

    Hello everyone,
    {message}

    Best regards, {ctx.author.display_name}."""

        delete_confirmation = await ctx.confirm("Would you like me to delete your message as well?",
                                                delete_after_confirm=True, delete_after_cancel=True,
                                                delete_after_timeout=True)
        if not delete_confirmation:
            with contextlib.suppress(discord.HTTPException, discord.Forbidden):
                await ctx.message.add_reaction("<:greenTick:895688440690147370>")

        else:
            with contextlib.suppress(discord.HTTPException, discord.Forbidden):
                await ctx.message.delete()

        return await channel.send(message,
                                  allowed_mentions=discord.AllowedMentions(everyone=True, replied_user=True, roles=True,
                                                                           users=True))