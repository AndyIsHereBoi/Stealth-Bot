import typing
import difflib
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


class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                member_id = int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f"{argument} is not a valid member or member ID.") from None
            else:
                m = await ctx.bot.get_or_fetch_member(ctx.guild, member_id)
                if m is None:
                    # hackban case
                    return type('_Hackban', (), {'id': member_id, '__str__': lambda s: f'Member ID {s.id}'})()

        if not can_execute_action(ctx, ctx.author, m):
            raise commands.BadArgument('You cannot do this action on this user due to role hierarchy.')
        return m


class BannedMember(commands.Converter):
    async def convert(self, ctx: CustomContext, argument):
        await ctx.trigger_typing()
        if argument.isdigit():
            member_id = int(argument, base=10)
            try:
                return await ctx.guild.fetch_ban(discord.Object(id=member_id))
            except discord.NotFound:
                raise commands.BadArgument('This member has not been banned before.') from None

        ban_list = await ctx.guild.bans()
        if not (entity := discord.utils.find(lambda u: str(u.user).lower() == argument.lower(), ban_list)):
            entity = discord.utils.find(lambda u: str(u.user.name).lower() == argument.lower(), ban_list)
            if not entity:
                matches = difflib.get_close_matches(argument, [str(u.user.name) for u in ban_list])
                if matches:
                    entity = discord.utils.find(lambda u: str(u.user.name) == matches[0], ban_list)
                    if entity:
                        val = await ctx.confirm(f"Closest match: {entity.user}. Are you sure you want to unban this user?",
                                                delete_after_cancel=True, delete_after_confirm=True,
                                                delete_after_timeout=False, timeout=60,
                                                buttons=((None, 'Yes', discord.ButtonStyle.green), (None, 'No', discord.ButtonStyle.grey)))
                        if val is None:
                            raise commands.BadArgument('You did not respond in time.')
                        elif val is False:
                            try:
                                await ctx.message.add_reaction(ctx.tick(True))

                            except discord.HTTPException:
                                pass

                            raise commands.BadArgument('Cancelled.')

        if entity is None:
            raise commands.BadArgument('This member has not been banned before.')
        return entity


class Reason(commands.Converter):
    async def convert(self, ctx, argument):
        ret = f'{ctx.author} (ID: {ctx.author.id}): {argument}'

        if len(ret) > 512:
            reason_max = 512 - len(ret) + len(argument)
            raise commands.BadArgument(f'Reason is too long ({len(argument)}/{reason_max})')
        return ret


class Basic(ModerationBase):

    @commands.command(
        help="With this command you can ban the specified member with a specified reason. You can also specify if I should delete messages. If no reason is provided it will not add a reason. The reason cannot be more than 500 characters.",
        brief="ban @Spammer\nban @Raider 7 Raiding")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User],
                  delete_days: typing.Optional[int] = 1, *, reason: typing.Optional[str] = 1):
        if reason is None or len(reason) > 500:
            reason = "Reason was not provided or it exceeded the 500-character limit."

        bot_can_execute_action(ctx, member)

        if can_execute_action(ctx, ctx.author, member):
            await ctx.guild.ban(member, reason=f"{reason} | Banned by {ctx.author}")

            try:
                await member.send(f"You have been banned from {ctx.guild}\nReason: {reason}")

            except:
                pass

            embed = discord.Embed(description=f":hammer: Successfully banned `{member}` for `{reason}`")
            embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

            return await ctx.send(embed=embed, footer=False)

        return await ctx.send("You can't ban that user!")

    @commands.command(
        help="With this command you can soft-ban the specified member. A soft-ban is basically banning the member and then unbanning them right after.",
        brief="softban @Spammer\nsoftban @Raider 7 Raiding",
        aliases=['soft_ban', 'soft-ban'])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def softban(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User],
                      delete_days: typing.Optional[int] = 1, *, reason: Reason):
        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        bot_can_execute_action(ctx, member)

        if can_execute_action(ctx, ctx.author, member):
            await ctx.guild.ban(member, reason=f"{reason} | Soft-banned by {ctx.author}")
            await ctx.guild.unban(member, reason=f"{reason} | Soft-banned by {ctx.author}")

            embed = discord.Embed(description=f":hammer: Successfully soft-banned `{member}` for `{reason}`")
            embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

            return await ctx.send(embed=embed, footer=False)

        return await ctx.send("You can't soft-ban that user!")

    @commands.command(
        help="With this command you can kick the specified member with a specified reason. If no reason is provided it will not add a reason. The reason cannot be more than 500 characters.",
        brief="kick @Noob\nkick @Gamer Asked for it")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True, kick_members=True)
    async def kick(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User], *, reason: Reason):
        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        bot_can_execute_action(ctx, member)

        if can_execute_action(ctx, ctx.author, member):
            await member.kick(reason=reason)

            try:
                await member.send(f"You have been kicked from {ctx.guild}\nReason: {reason}")

            except:
                pass

            embed = discord.Embed(description=f":boot: Successfully kicked `{member}` for `{reason}`")
            embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

            return await ctx.send(embed=embed, footer=False)

        return await ctx.send("You can't kick that user!")

    @commands.command(
        help="Unbans the given member.")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx: CustomContext, *, user: BannedMember):
        user: discord.guild.BanEntry

        await ctx.guild.unban(user.user)

        extra = f"Previously banned for: {user.reason}" if user.reason else ''
        embed = discord.Embed(title=f"Unbanned {discord.utils.escape_markdown(str(user.user))}", description=f"{extra}")

        return await ctx.send(embed=embed)