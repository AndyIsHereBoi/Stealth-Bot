import typing
import discord

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

class Voice(ModerationBase):

    @commands.command(
        help="Mutes the specified member with a specified reason. This will prevent them from talking in any VC. If no reason is provided it will not add a reason. The reason cannot be more than 500 characters.",
        aliases=['vc_mute', 'vc-mute', 'mutevc', 'mute_vc', 'mute-vc'],
        brief="vcmute @Noobie\nvcmute @Noobie shutt")
    @commands.has_permissions(mute_members=True)
    @commands.bot_has_permissions(mute_members=True)
    async def vcmute(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User], *, reason=None):
        if reason is None or len(reason) > 500:
            reason = "Reason was not provided or it exceeded the 500-character limit."

        bot_can_execute_action(ctx, member)

        if not can_execute_action(ctx, ctx.author, member):
            return await ctx.send("You can't VC mute that person!")


        await member.edit(mute=True, reason=reason)
        embed = discord.Embed(description=f"Successfully VC muted `{member}` for `{reason}`")
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="Deafens the specified member with a specified reason. This will prevent them from hearing anything in any VC. If no reason is provided it will not add a reason. The reason cannot be more than 500 characters.",
        aliases=['vc_deafen', 'vc-deafen', 'deafenvc', 'deafen_vc', 'deafen-vc'],
        brief="vcdeafen @Noob\nvcdeafen @Noob imagine being deafened smh")
    @commands.has_permissions(deafen_members=True)
    @commands.bot_has_permissions(deafen_members=True)
    async def vcdeafen(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User], *, reason=None):
        if reason is None or len(reason) > 500:
            reason = "Reason was not provided or it exceeded the 500-character limit."

        bot_can_execute_action(ctx, member)

        if not can_execute_action(ctx, ctx.author, member):
            return await ctx.send("You can't VC deafen that person!")

        await member.edit(deafen=True, reason=reason)
        embed = discord.Embed(description=f"Successfully VC deafened `{member}` for `{reason}`")
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)