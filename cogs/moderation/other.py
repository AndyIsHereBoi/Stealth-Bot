import errors
import typing
import discord
import datetime

from helpers import helpers
from helpers import time_inputs
from discord.ext import commands
from ._base import ModerationBase
from helpers.context import CustomContext

def can_execute_action(ctx, user, target):
    if isinstance(target, discord.Member):
        return user == ctx.guild.owner or (user.top_role > target.top_role and target != ctx.guild.owner)
    elif isinstance(target, discord.User):
        return True
    raise TypeError(f'argument \'target\' expected discord.User, received {type(target)} instead')


def bot_can_execute_action(ctx: CustomContext, target: discord.Member):
    if isinstance(target, discord.Member):
        if target.top_role > ctx.guild.me.top_role:
            raise commands.BadArgument('This member has a higher role than me.')
        elif target == ctx.guild.owner:
            raise commands.BadArgument('I cannot perform that action, as the target is the owner.')
        elif target == ctx.guild.me:
            raise commands.BadArgument('I cannot perform that action on myself.')
        return True

class Other(ModerationBase):

    @commands.command(
        help="Changes the specified member's nickname to the specified nickname. If you don't specify a nickname, it will reset it.",
        aliases=['set_nick', 'set-nick', 'changenick', 'change_nick', 'change-nick'],
        brief="setnick @Guy\nsetnick @Jeff Jeffie\nsetnick @Danny Pog guy")
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    async def setnick(self, ctx: CustomContext, member: discord.Member, *, nickname: typing.Optional[str] = None):
        if nickname is None:
            nickname = member.name

        if len(nickname) > 32:
            embed = discord.Embed(description="The nickname is too long! The maximum length is `32` characters.")

            return await ctx.send(embed=embed)

        bot_can_execute_action(ctx, member)

        if not can_execute_action(ctx, ctx.author, member):
            return await ctx.send("You can't change the nickname of that person!")

        old = member.display_name
        new = nickname or member.name

        await member.edit(nick=new)

        embed = discord.Embed(title="Nickname changed!", description=f"""
    Successfully changed {member.mention}'s nickname.
    Old nickname: `{old}`
    New nickname: `{new}`
                                """)

        await ctx.send(embed=embed)

    @commands.command(
        help="Changes the slowmode of the specified channel.",
        aliases=['sm', 'slowm', 'slow', 'slowness', 'slowdown'],
        brief="slowmode 3h, 5m, 2s\nslowmode 5h1m35s\nslowmode")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx: CustomContext, channel: typing.Optional[discord.TextChannel], *,
                       duration: typing.Optional[typing.Union[time_inputs.ShortTime, str]] = None):
        channel = channel if channel and channel.permissions_for(
            ctx.author).manage_channels and channel.permissions_for(ctx.me).manage_channels else ctx.channel

        if not duration or isinstance(duration, str):
            await channel.edit(slowmode_delay=0)

            embed = discord.Embed(description=f"Slow-mode has been disabled in {channel.mention}.")
            embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

            return await ctx.send(embed=embed, footer=False)

        created_at = ctx.message.created_at
        delta: datetime.timedelta = duration.dt > (created_at + datetime.timedelta(hours=6))

        if delta:
            return await ctx.send("The slow-mode cannot be more than 6 hours!")

        seconds = (duration.dt - ctx.message.created_at).seconds
        await channel.edit(slowmode_delay=int(seconds))

        human_delay = helpers.human_timedelta(duration.dt, source=created_at)

        embed = discord.Embed(description=f"Messages in {channel.mention} can now be sent every {human_delay}.")
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        return await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="Locks down a specified channel. You can also specify the role. If no channel is specified it will default to the current channel and if no role is specified it will default to the @everyone role.",
        aliases=['lock', 'ld'])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def lockdown(self, ctx: CustomContext, channel: typing.Optional[discord.TextChannel],
                       role: typing.Optional[discord.Role]):
        role = role if role and (role < ctx.me.top_role or ctx.author == ctx.guild.owner) \
                       and role < ctx.author.top_role else ctx.guild.default_role

        channel = channel if channel and channel.permissions_for(ctx.author).manage_roles and channel.permissions_for(
            ctx.me).manage_roles else ctx.channel

        permisions = channel.overwrites_for(ctx.me)
        permisions.update(send_messages=True, add_reactions=True, create_public_threads=True,
                          create_private_threads=True)

        await channel.set_permissions(ctx.me, overwrite=permisions,
                                      reason=f"Channel lockdown by {ctx.author} ({ctx.author.id})")

        permissions = channel.overwrites_for(role)
        permissions.update(send_messages=False, add_reactions=False, create_public_threads=False,
                           create_private_threads=False)

        await channel.set_permissions(role, overwrite=permissions,
                                      reason=f"Channel lockdown for {role.name} by {ctx.author} ({ctx.author.id})")
        await channel.send(f"This channel has been locked down by {ctx.author.mention}.")

        embed = discord.Embed(description=f"Successfully locked {channel.mention} down for {role.mention}.")
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="Unlocks a specified channel. You can also specify the role. If no channel is specified it will default to the current channel and if no role is specified it will default to the @everyone role.",
        aliases=['unlockdown', 'uld'])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unlock(self, ctx: CustomContext, channel: typing.Optional[discord.TextChannel],
                     role: typing.Optional[discord.Role]):
        role = role if role and (role < ctx.me.top_role or ctx.author == ctx.guild.owner) \
                       and role < ctx.author.top_role else ctx.guild.default_role

        channel = channel if channel and channel.permissions_for(ctx.author).manage_roles and channel.permissions_for(
            ctx.me).manage_roles else ctx.channel

        permissions = channel.overwrites_for(ctx.guild.default_role)
        permissions.update(send_messages=None, add_reactions=None, create_public_threads=None,
                           create_private_threads=None)

        await channel.set_permissions(role, overwrite=permissions,
                                      reason=f"Channel unlocked for {role.name} by {ctx.author} ({ctx.author.id})")
        await channel.send(f"This channel has been unlocked by {ctx.author.mention}.")

        embed = discord.Embed(description=f"Successfully unlocked {channel.mention} for {role.mention}.")
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="Archives the specified thread")
    async def archive(self, ctx: CustomContext, thread: discord.Thread, *, reason: str = None):
        if not isinstance(thread, discord.Thread):
            raise errors.InvalidThread

        if reason is None or len(reason) >= 150:
            reason = f"Reason not provided or it exceeded the 150-character limit"

        await thread.edit(archived=True)

        await thread.send(f"This thread has been archived by {ctx.author.mention} with the reason being {reason}")

        embed = discord.Embed(description=f"Successfully archived {thread.mention}.")
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="Blocks the specified member from using the current channel")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def block(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User]):
        bot_can_execute_action(ctx, member)

        if not can_execute_action(ctx, ctx.author, member):
            raise errors.Forbidden

        try:
            await ctx.channel.set_permissions(member, reason=f"Blocked by {ctx.author} ({ctx.author.id})",
                                              send_messages=False, add_reactions=False, create_public_threads=False,
                                              create_private_threads=False, send_messages_in_threads=False)

        except (discord.Forbidden, discord.HTTPException):
            raise errors.UnknownError

        else:

            embed = discord.Embed(description=f"Successfully blocked {member.mention} from {ctx.channel.mention}.")
            embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

            await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="Unblocks the specified member from the current channel")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unblock(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User]):
        bot_can_execute_action(ctx, member)

        if not can_execute_action(ctx, ctx.author, member):
            raise errors.Forbidden

        try:
            await ctx.channel.set_permissions(member, reason=f"Unblocked by {ctx.author} ({ctx.author.id})",
                                              send_messages=None, add_reactions=None, create_public_threads=None,
                                              create_private_threads=None, send_messages_in_threads=None)

        except (discord.Forbidden, discord.HTTPException):
            await ctx.send('Something went wrong...')

        else:
            embed = discord.Embed(description=f"Successfully unblocked {member.mention} from {ctx.channel.mention}.")
            embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

            await ctx.send(embed=embed, footer=False)