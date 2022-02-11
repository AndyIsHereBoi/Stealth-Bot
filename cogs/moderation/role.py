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

class Role(ModerationBase):

    @commands.command(
        help="Gives a member a role",
        aliases=['give_role'])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True, manage_roles=True)
    async def giverole(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User],
                       role: discord.Role):
        bot_can_execute_action(ctx, member)

        if not can_execute_action(ctx, ctx.author, member):
            return await ctx.send("You can't add that role to that person!")

        await member.add_roles(role, reason=f'Added by `{ctx.author}` using command')

        embed = discord.Embed(description=f"Successfully gave {member.mention} the {role.mention} role.")
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="Removes a role from a member",
        aliases=['remove_role'])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True, manage_roles=True)
    async def removerole(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User],
                         role: discord.Role):
        bot_can_execute_action(ctx, member)

        if not can_execute_action(ctx, ctx.author, member):
            return await ctx.send("You can't remove that role from that person!")

        await member.remove_roles(role, reason=f'Removed by `{ctx.author}` using command')

        embed = discord.Embed(description=f"Successfully removed the {role.mention} role from {member.mention}.")
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)
