import re
import shlex

import errors
import random
import typing
import asyncio
import discord
import datetime
import argparse

from collections import Counter
from helpers import helpers as helpers
from helpers.context import CustomContext
from helpers import time_inputs as time_inputs
from discord.ext import commands, menus, tasks
from discord.ext.menus.views import ViewMenuPages

def can_execute_action(ctx, member, target):
    return target.id == member.id or target.id == ctx.me.id or target.id == ctx.guild.owner.id or target.guild_permissions.administrator or (member.top_role > target.top_role and target != ctx.guild.owner)

def ensure_muterole(*, required: bool = True):
    async def predicate(ctx):
        if not ctx.guild:
            raise commands.BadArgument('Only servers can have mute roles')
        if not required:
            return True
        if not (role := await ctx.bot.db.fetchval('SELECT muted_role_id FROM guilds WHERE guild_id = $1', ctx.guild.id)):
            raise commands.BadArgument('This server has no mute role set')
        if not (role := ctx.guild.get_role(role)):
            raise commands.BadArgument("It seems like I could not find this server's mute role. Was it deleted?")
        if role >= ctx.me.top_role:
            raise commands.BadArgument("This server's mute role seems to be above my top role. I can't assign it!")
        return True
    return commands.check(predicate)


async def muterole(ctx) -> discord.Role:
    if not ctx.guild:
        raise commands.BadArgument('Only servers can have mute roles')
    if not (role := await ctx.bot.db.fetchval('SELECT muted_role_id FROM guilds WHERE guild_id = $1', ctx.guild.id)):
        raise commands.BadArgument('This server has no mute role set')
    if not (role := ctx.guild.get_role(role)):
        raise commands.BadArgument("It seems like I could not find this server's mute role. Was it deleted?")
    if role >= ctx.me.top_role:
        raise commands.BadArgument("This server's mute role seems to be above my top role. I can't assign it!")
    return role


def setup(client):
    client.add_cog(Moderation(client))
    
class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)


class ServerBansEmbedPage(menus.ListPageSource):
    def __init__(self, data, guild):
        self.data = data
        self.guild = guild
        super().__init__(data, per_page=20)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        colors = [0x910023, 0xA523FF]
        color = random.choice(colors)
        bans = await self.guild.bans()
        embed = discord.Embed(title=f"{self.guild}'s bans ({len(bans)})",
                              description="\n".join(f'{i + 1}. {v}' for i, v in enumerate(entries, start=offset)),
                              timestamp=discord.utils.utcnow(), color=color)
        return embed


class Moderation(commands.Cog):
    """Commands useful for staff members of the server."""

    def __init__(self, client):
        self.client = client
        self.select_emoji = "<:staff:858326975869485077>"
        self.select_brief = "Commands useful for staff members of the server."

    @staticmethod
    async def do_removal(ctx, limit: int, predicate, *, before=None, after=None, bulk: bool = True):
        if limit > 2000:
            return await ctx.send(f'Too many messages to search given ({limit}/2000)')

        async with ctx.typing():
            if before is None:
                before = ctx.message
            else:
                before = discord.Object(id=before)

            if after is not None:
                after = discord.Object(id=after)

            try:
                deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate, bulk=bulk)
            except discord.Forbidden:
                return await ctx.send('I do not have permissions to delete messages.')
            except discord.HTTPException as e:
                return await ctx.send(f'Error: {e} (try a smaller search?)')

            spammers = Counter(m.author.display_name for m in deleted)
            deleted = len(deleted)
            messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
            if deleted:
                messages.append('')
                spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
                messages.extend(f'**{name}**: {count}' for name, count in spammers)

            to_send = '\n'.join(messages)

            if len(to_send) > 2000:
                embed = discord.Embed(description=f"Successfully removed {deleted} messages.")
                embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

                await ctx.send(embed=embed, footer=False, reply=False, delete_after=10)
                
                try:
                    await ctx.message.delete()
                    
                except:
                    pass
                
            else:
                embed = discord.Embed(description=f"{to_send}")
                embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

                await ctx.send(embed=embed, footer=False, reply=False, delete_after=10)
                
                try:
                    await ctx.message.delete()
                    
                except:
                    pass
                
    @tasks.loop()
    async def temporary_mutes(self):
        # if you don't care about keeping records of old tasks, remove this WHERE and change the UPDATE to DELETE
        next_task = await self.client.db.fetchrow('SELECT * FROM temporary_mutes ORDER BY end_time LIMIT 1')
        # if no remaining tasks, stop the loop
        if next_task is None:
            self.temporary_mutes.cancel()
            return

        await discord.utils.sleep_until(next_task['end_time'])

        guild: discord.Guild = self.client.get_guild(next_task['guild_id'])

        if guild:

            mute_role = await self.client.db.fetchval('SELECT muted_role_id FROM guilds WHERE guild_id = $1',
                                                   next_task['guild_id'])
            if mute_role:

                role = guild.get_role(int(mute_role))
                if isinstance(role, discord.Role):

                    if not role > guild.me.top_role:
                        try:
                            member = (guild.get_member(next_task['member_id']) or
                                      await guild.fetch_member(next_task['member_id']))
                            if member:
                                await member.remove_roles(role)
                        except(discord.Forbidden, discord.HTTPException):
                            pass

        await self.client.db.execute('DELETE FROM temporary_mutes WHERE (guild_id, member_id) = ($1, $2)',
                                  next_task['guild_id'], next_task['member_id'])

    @temporary_mutes.before_loop
    async def wait_for_bot_ready(self):
        await self.client.wait_until_ready()

    def mute_task(self):
        if self.temporary_mutes.is_running():
            self.temporary_mutes.restart()
        else:
            self.temporary_mutes.start()

    @commands.command(
        help="Cleans up the bots messages.",
        brief="cleanup\ncleanup 50")
    async def cleanup(self, ctx: CustomContext, amount: int = 25):
        if amount > 25:

            if not ctx.channel.permissions_for(ctx.author).manage_messages:
                return await ctx.send("You must have `manage_messages` permission to perform a search greater than 25")

            if not ctx.channel.permissions_for(ctx.me).manage_messages:
                return await ctx.send("I need the `manage_messages` permission to perform a search greater than 25")

        if ctx.channel.permissions_for(ctx.me).manage_messages:
            prefix = tuple(await self.client.get_pre(self.client, ctx.message))
            bulk = True

            def check(msg):
                return msg.author == ctx.me or msg.content.startswith(prefix)
        else:
            bulk = False

            def check(msg):
                return msg.author == ctx.me

        await self.do_removal(ctx, predicate=check, bulk=bulk, limit=amount)

    @commands.command(
        help="Gets the current guild's list of bans")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True, ban_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def bans(self, ctx: CustomContext):
        guild = ctx.guild

        guildBans = await guild.bans()
        bans = []

        if not guildBans:
            raise errors.NoBannedMembers

        for ban in guildBans:
            bans.append(
                f"[{ban.user}](https://discord.com/users/{ban.user.id} \'Name: {ban.user.name}\nID: {ban.user.id}\nDiscriminator: #{ban.user.discriminator}') | [Hover for reason](https://discord.com/ '{ban.reason}')")

        paginator = ViewMenuPages(source=ServerBansEmbedPage(bans, guild), clear_reactions_after=True)
        page = await paginator._source.get_page(0)
        kwargs = await paginator._get_kwargs_from_page(page)
        if paginator.build_view():
            paginator.message = await ctx.send(embed=kwargs['embed'], view=paginator.build_view())
        else:
            paginator.message = await ctx.send(embed=kwargs['embed'])
        await paginator.start(ctx)

    @commands.command(
        help="Announces a message in a specified channel. If no channel is specified it will default to the current one.")
    @commands.has_permissions(manage_messages=True)
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    async def announce(self, ctx: CustomContext, channel: typing.Optional[discord.TextChannel] = None, *, message):
        if channel is None:
            channel = ctx.channel

        channelid = channel.id
        channel = self.client.get_channel(channelid)

        try:
            await ctx.message.delete()

        except:
            pass

        await channel.send(message)

    @commands.command(
        help="With this command you can ban the specified member with a specified reason. You can also specify if I should delete messages. If no reason is provided it will not add a reason. The reason cannot be more than 500 characters.",
        brief="ban @Spammer\nban @Raider 7 Raiding")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User], delete_days: typing.Optional[int] = 1, *, reason: typing.Optional[str] = 1):
        if delete_days and 7 < delete_days < 0:
            return await ctx.send("Delete days must be between 0 and 7")
        
        if member.id == ctx.author.id:
            return await ctx.send("You can't ban yourself!")
        
        if member.id == self.client.user.id:
            return await ctx.send("Noooo! Don't ban me :(")

        if member.id == ctx.guild.owner.id:
            return await ctx.send("You can't ban the owner of this server!")
        
        if member.guild_permissions.administrator:
            return await ctx.send("You can't ban that user since they have the administrator permission!")

        if isinstance(member, discord.Member):
            if member.top_role >= ctx.me.top_role:
                raise errors.Forbidden

        if reason is None or len(reason) > 500:
            reason = "Reason was not provided or it exceeded the 500-character limit."

        embed = discord.Embed(description=f"Successfully banned `{member}` for `{reason}`")
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

        try:
            await member.send(f"You have been banned from {ctx.guild}\nReason: {reason}")
            return await member.ban(reason=reason)

        except:
            return await member.ban(reason=reason)
        
    @commands.command(
        help="With this command you can soft-ban the specified member. A soft-ban is basically banning the member and then unbanning them right after.",
        brief="softban @Spammer\nsoftban @Raider 7 Raiding",
        aliases=['soft_ban', 'soft-ban'])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def softban(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User], delete_days: typing.Optional[int] = 1, *, reason: typing.Optional[str] = 1):
        if delete_days and 7 < delete_days < 0:
            return await ctx.send("Delete days must be between 0 and 7")
        
        if member.id == ctx.author.id:
            return await ctx.send("You can't soft-ban yourself!")
        
        if member.id == self.client.user.id:
            return await ctx.send("Noooo! Don't soft-ban me :(")

        if member.id == ctx.guild.owner.id:
            return await ctx.send("You can't soft-ban the owner of this server!")
        
        if member.guild_permissions.administrator:
            return await ctx.send("You can't soft-ban that user since they have the administrator permission!")

        if isinstance(member, discord.Member):
            if member.top_role >= ctx.me.top_role:
                raise errors.Forbidden

        if reason is None or len(reason) > 500:
            reason = "Reason was not provided or it exceeded the 500-character limit."

        embed = discord.Embed(description=f"Successfully soft-banned `{member}` for `{reason}`")
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

        try:
            await member.send(f"You have been soft-banned from {ctx.guild}\nReason: {reason}")
            await ctx.guild.ban(member, reason=reason, delete_message_days=delete_days)
            return await ctx.guild.unban(member, reason=reason)

        except:
            await ctx.guild.ban(member, reason=reason, delete_message_days=delete_days)
            return await ctx.guild.unban(member, reason=reason)

    @commands.command(
        help="With this command you can kick the specified member with a specified reason. If no reason is provided it will not add a reason. The reason cannot be more than 500 characters.",
        brief="kick @Noob\nkick @Gamer Asked for it")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True, kick_members=True)
    async def kick(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User], *, reason=None):
        if member.id == ctx.author.id:
            return await ctx.send("You can't kick yourself!")
        
        if member.id == self.client.user.id:
            return await ctx.send("Noooo! Don't kick me :(")

        if member.id == ctx.guild.owner.id:
            return await ctx.send("You can't kick the owner of this server!")
        
        if member.guild_permissions.administrator:
            return await ctx.send("You can't kick that user since they have the administrator permission!")

        if isinstance(member, discord.Member):
            if member.top_role >= ctx.me.top_role:
                raise errors.Forbidden

        if reason is None or len(reason) > 500:
            reason = "Reason was not provided or it exceeded the 500-character limit."
            
        embed = discord.Embed(description=f"Successfully kicked `{member}` for `{reason}`")
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

        try:
            await member.message(f"You have been kicked from {ctx.guild}\nReason: {reason}")
            await member.kick(reason=reason)

        except:
            return await member.kick(reason=reason)
        
    @commands.command(
        help="With this command you can kick a lot of members at once.",
        brief="masskick @Noob @Fusion @Leo\nkick @Gamer @Danny @Buco Asked for it",
        aliases=['mass_kick', 'mass-kick', 'multikick', 'multi_kick', 'multi-kick'])
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True, kick_members=True)
    async def masskick(self, ctx: CustomContext, members: commands.Greedy[typing.Union[discord.Member, discord.User]], *, reason: typing.Optional[str]):
        if reason is None or len(reason) > 500:
            reason = "Reason was not provided or it exceeded the 500-character limit."
            
        if members is None:
            return await ctx.send("You need to specify who you want me to kick!")

        successful: typing.List[discord.Member] = []
        failed_perms: typing.List[discord.Member] = []
        failed_internal: typing.List[discord.Member] = []

        for member in members:
            if member.id == ctx.author.id:
                failed_perms.append(member)
                continue
            
            if member.id == self.client.user.id:
                failed_perms.append(member)
                continue

            if member.id == ctx.guild.owner.id:
                failed_perms.append(member)
                continue
            
            if member.guild_permissions.administrator:
                failed_perms.append(member)
                continue

            if isinstance(member, discord.Member):
                if member.top_role >= ctx.me.top_role:
                    failed_perms.append(member)
                    continue
            
            try:
                try:
                    await member.send(f"You have been kicked from {ctx.guild}\nReason: {reason}")
                    await member.kick(reason=str(reason))
                    
                except:
                    await member.kick(reason=str(reason))
                    
                successful.append(member)
                
            except (discord.Forbidden, discord.HTTPException):
                failed_internal.append(member)
                continue
            
        embed = discord.Embed(description=f"""
Successfully kicked `{len(successful)}` members for `{reason}`

**Successfully kicked**: {len(successful)}/{len(members)}
**Successful**: {', '.join([member.display_name for member in successful]) if successful else 'N/A'}
**Failed**: {', '.join([m.display_name for m in failed_perms + failed_internal]) if failed_perms or failed_internal else 'N/A'}
                              """)
        
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="With this command you can ban a lot of members at once.",
        brief="massban @Noob @Fusion @Leo\nmassban @Gamer @Danny @Buco Asked for it",
        aliases=['mass_ban', 'mass-ban', 'multiban', 'multi_ban', 'multi-ban'])
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True, kick_members=True)
    async def massban(self, ctx: CustomContext, members: commands.Greedy[typing.Union[discord.Member]], delete_days: typing.Optional[int], *, reason: typing.Optional[str]):
        if reason is None or len(reason) > 500:
            reason = "Reason was not provided or it exceeded the 500-character limit."

        if members is None:
            return await ctx.send("You need to specify who you want me to ban!")

        successful: typing.List[discord.Member] = []
        failed_perms: typing.List[discord.Member] = []
        failed_internal: typing.List[discord.Member] = []

        for member in members:
            if member.id == ctx.author.id:
                failed_perms.append(member)
                continue

            if member.id == self.client.user.id:
                failed_perms.append(member)
                continue

            if member.id == ctx.guild.owner.id:
                failed_perms.append(member)
                continue

            if member.guild_permissions.administrator:
                failed_perms.append(member)
                continue

            if isinstance(member, discord.Member):
                if member.top_role >= ctx.me.top_role:
                    failed_perms.append(member)
                    continue

            try:
                try:
                    await member.send(f"You have been banned from {ctx.guild}\nReason: {reason}")
                    await ctx.guild.ban(member, reason=reason, delete_days=delete_days)

                except:
                    await ctx.guild.ban(member, reason=reason, delete_days=delete_days)

                successful.append(member)

            except (discord.Forbidden, discord.HTTPException):
                failed_internal.append(member)
                continue

        embed = discord.Embed(description=f"""
Successfully banned `{len(successful)}` members for `{reason}`

**Successfully banned**: {len(successful)}/{len(members)}
**Successful**: {', '.join([member.display_name for member in successful]) if successful else 'N/A'}
**Failed**: {', '.join([m.display_name for m in failed_perms + failed_internal]) if failed_perms or failed_internal else 'N/A'}
                              """)

        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)
        
    @commands.command(
        help="Changes the specified member's nickname to the specified nickname. If you don't specify a nickname, it will reset it.",
        aliases=['set_nick', 'set-nick', 'changenick', 'change_nick', 'change-nick'],
        brief="setnick @Guy\nsetnick @Jeff Jeffie\nsetnick @Danny Pog guy")
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    async def setnick(self, ctx: CustomContext, member: discord.Member, *, nickname: typing.Optional[str] = None):
        if member.id == ctx.guild.owner.id:
            return await ctx.send("You can't change the nickname of the server owner.")
        
        if member.guild_permissions.administrator:
            return await ctx.send("You can't change that member's nickname since they're an administrator.")

        if isinstance(member, discord.Member):
            if member.top_role >= ctx.me.top_role:
                raise errors.Forbidden
        
        if nickname is None:
            nickname = member.name
            
        if len(nickname) > 32:
            embed = discord.Embed(description="The nickname is too long! The maximum length is `32` characters.")
            
            return await ctx.send(embed=embed)
        
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
        help="Mutes the specified member with a specified reason. This will prevent them from talking in any VC. If no reason is provided it will not add a reason. The reason cannot be more than 500 characters.",
        aliases=['vc_mute', 'vc-mute', 'mutevc', 'mute_vc', 'mute-vc'],
        brief="vcmute @Noobie\nvcmute @Noobie shutt")
    @commands.has_permissions(mute_members=True)
    @commands.bot_has_permissions(mute_members=True)
    async def vcmute(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User], *, reason=None):
        if not can_execute_action(ctx, ctx.author, member):
            return await ctx.send("You can't VC mute that person!")

        if reason is None or len(reason) > 500:
            reason = "Reason was not provided or it exceeded the 500-character limit."

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
        if not can_execute_action(ctx, ctx.author, member):
            return await ctx.send("You can't VC deafen that person!")

        if reason is None or len(reason) > 500:
            reason = "Reason was not provided or it exceeded the 500-character limit."

        await member.edit(deafen=True, reason=reason)
        embed = discord.Embed(description=f"Successfully VC deafened `{member}` for `{reason}`")
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)
        
    @commands.group(
        help="<:trash:904107565129027594> | Removes messages that meet a criteria.\nNote: If ran without any sub-commands, it will remove all messages that are NOT pinned to the channel.\nUse \"remove all <amount>\" to remove all messages, including pinned.",
        aliases=['purge', 'cls', 'clr'],
        brief="remove 100\nremove user @Spammer#6942\nremove embeds 53")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def remove(self, ctx: CustomContext, search: typing.Optional[int] = 100):
        if ctx.invoked_subcommand is None:
            await self.do_removal(ctx, search, lambda e: not e.pinned)

    @remove.command(
        name="embeds",
        help="Removes messages that have embeds in them.",
        aliases=['embed'])
    async def remove_embeds(self, ctx: CustomContext, search=100):
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @remove.command(
        name="files",
        help="Removes messages that have attachments in them.",
        aliases=["attachments"])
    async def remove_files(self, ctx: CustomContext, search=100):
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @remove.command(
        name="images",
        help="Removes messages that have embeds or attachments.",
        aliases=['imgs'])
    async def remove_images(self, ctx: CustomContext, search=100):
        await self.do_removal(ctx, search, lambda e: len(e.embeds) or len(e.attachments))

    @remove.command(
        name="all",
        help="Removes all messages.",
        aliases=['everything'])
    async def remove_all(self, ctx: CustomContext, search=100):
        await self.do_removal(ctx, search, lambda e: True)

    @remove.command(
        name="user",
        help="Removes all messages sent by the specified member.",
        aliases=['member'])
    async def remove_user(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User], search=100):
        await self.do_removal(ctx, search, lambda e: e.author == member)

    @remove.command(
        name="contains",
        help="Removes all messages containing a substring.\nThe substring must be at least 3 characters long.",
        aliases=["has"])
    async def remove_contains(self, ctx: CustomContext, *, text: str):
        if len(text) < 3:
            return await ctx.send("The substring must be at least 3 characters!")
            
        else:
            await self.do_removal(ctx, 100, lambda e: text in e.content)

    @remove.command(
        name="bot",
        help="Removes a bot user's messages and messages with their optional prefix.",
        aliases=['bots', 'robot'])
    async def remove_bot(self, ctx: CustomContext, prefix: typing.Optional[str] = None, search=100):
        def predicate(m):
            return (m.webhook_id is None and m.author.bot) or (prefix and m.content.startswith(prefix))

        await self.do_removal(ctx, search, predicate)

    @remove.command(
        name="emoji",
        help="Removes all messages containing custom emojis.",
        aliases=['emojis', 'emote', 'emotes'])
    async def remove_emoji(self, ctx: CustomContext, search=100):
        custom_emoji = re.compile(r'<a?:[a-zA-Z0-9_]+:([0-9]+)>')

        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @commands.has_permissions(manage_threads=True)
    @commands.bot_has_permissions(manage_threads=True)
    @remove.command(
        name="threads",
        help="Removes the given amount of threads",
        aliases=['thread'])
    async def remove_threads(self, ctx: CustomContext, search: int = 100):
        async with ctx.typing():
            if search > 2000:
                return await ctx.send(f'Too many messages to search given ({search}/2000)')

            def check(m: discord.Message):
                return m.flags.has_thread

            deleted = await ctx.channel.purge(limit=search, check=check)
            thread_ids = [m.id for m in deleted]
            
            if not thread_ids:
                return await ctx.send("No threads found!")

            for thread_id in thread_ids:
                thread = self.client.get_channel(thread_id)
                
                if isinstance(thread, discord.Thread):
                    await thread.delete()
                    await asyncio.sleep(0.5)

            spammers = Counter(m.author.display_name for m in deleted)
            deleted = len(deleted)
            messages = [f'{deleted} message'
                        f'{" and its associated thread was" if deleted == 1 else "s and their associated messages were"} '
                        f'removed.']

            if deleted:
                messages.append('')
                spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
                messages.extend(f'**{name}**: {count}' for name, count in spammers)

            to_send = '\n'.join(messages)

            if len(to_send) > 2000:
                await ctx.send(f"Successfully removed `{deleted}` messages and their associated threads.", delete_after=10, reply=False)

            else:
                await ctx.send(f"{to_send}", delete_after=10, reply=False)

    @remove.command(
        name="reactions",
        help="Removes all reactions from messages that have them.",
        aliases=['reaction'])
    async def remove_reactions(self, ctx: CustomContext, search=100):
        async with ctx.typing():
            if search > 2000:
                return await ctx.send(f'Too many messages to search for ({search}/2000)')

            total_reactions = 0
            async for message in ctx.history(limit=search, before=ctx.message):
                if len(message.reactions):
                    total_reactions += sum(r.count for r in message.reactions)
                    await message.clear_reactions()
                    await asyncio.sleep(0.5)

            await ctx.send(f'Successfully removed {total_reactions} reactions.')

    @remove.command(
        name="custom",
        help="A more advanced purge command, with a command-line-like syntax.\nDo \"sb!remove help\" for usage.",
        aliases=['c'])
    async def remove_custom(self, ctx: CustomContext, *, args: str):
        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument('--user', nargs='+')
        parser.add_argument('--contains', nargs='+')
        parser.add_argument('--starts', nargs='+')
        parser.add_argument('--ends', nargs='+')
        parser.add_argument('--or', action='store_true', dest='_or')
        parser.add_argument('--not', action='store_true', dest='_not')
        parser.add_argument('--emoji', action='store_true')
        parser.add_argument('--bot', action='store_const', const=lambda m: m.author.bot)
        parser.add_argument('--embeds', action='store_const', const=lambda m: len(m.embeds))
        parser.add_argument('--files', action='store_const', const=lambda m: len(m.attachments))
        parser.add_argument('--reactions', action='store_const', const=lambda m: len(m.reactions))
        parser.add_argument('--search', type=int)
        parser.add_argument('--after', type=int)
        parser.add_argument('--before', type=int)

        try:
            args = parser.parse_args(shlex.split(args))
        except Exception as e:
            await ctx.send(str(e))
            return

        predicates = []
        if args.bot:
            predicates.append(args.bot)

        if args.embeds:
            predicates.append(args.embeds)

        if args.files:
            predicates.append(args.files)

        if args.reactions:
            predicates.append(args.reactions)

        if args.emoji:
            custom_emoji = re.compile(r'<:(\w+):(\d+)>')
            predicates.append(lambda m: custom_emoji.search(m.content))

        if args.user:
            users = []
            converter = commands.MemberConverter()
            for u in args.user:
                try:
                    user = await converter.convert(ctx, u)
                    users.append(user)
                except Exception as e:
                    await ctx.send(str(e))
                    return

            predicates.append(lambda m: m.author in users)

        if args.contains:
            predicates.append(lambda m: any(sub in m.content for sub in args.contains))

        if args.starts:
            predicates.append(lambda m: any(m.content.startswith(s) for s in args.starts))

        if args.ends:
            predicates.append(lambda m: any(m.content.endswith(s) for s in args.ends))

        op = all if not args._or else any

        def predicate(m):
            r = op(p(m) for p in predicates)
            if args._not:
                return not r
            return r

        if args.after:
            if args.search is None:
                args.search = 2000

        if args.search is None:
            args.search = 100

        args.search = max(0, min(2000, args.search))  # clamp from 0-2000
        await self.do_removal(ctx, args.search, predicate, before=args.before, after=args.after)

    @remove.command(name="help", hidden=True)
    async def remove_custom_readme(self, ctx: CustomContext):
        """A more advanced purge command.
        This command uses a powerful "command line" syntax.
        Most options support multiple values to indicate 'any' match.
        If the value has spaces it must be quoted.
        The messages are only deleted if all options are met unless
        the --or flag is passed, in which case only if any is met.
        The following options are valid.
         --user: A mention or name of the user to remove.
         --contains: A substring to search for in the message.
         --starts: A substring to search if the message starts with.
         --ends: A substring to search if the message ends with.
         --search: Messages to search. Default 100. Max 2000.
         --after: Messages after this message ID.
         --before: Messages before this message ID.
        Flag options (no arguments):
         --bot: Check if it's a bot user.
         --embeds: Checks for embeds.
         --files: Checks for attachments.
         --emoji: Checks for custom emoji.
         --reactions: Checks for reactions.
         --or: Use logical OR for ALL options.
         --not: Use logical NOT for ALL options.
        """
        await ctx.send_help(ctx.command)
        
    @commands.command(
        help="Changes the slowmode of the specified channel.",
        aliases=['sm', 'slowm', 'slow', 'slowness', 'slowdown'],
        brief="slowmode 3h, 5m, 2s\nslowmode 5h1m35s\nslowmode")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx: CustomContext, channel: typing.Optional[discord.TextChannel], *, duration: time_inputs.ShortTime = None):
        channel = channel if channel and channel.permissions_for(ctx.author).manage_channels and channel.permissions_for(ctx.me).manage_channels else ctx.channel

        if not duration:
            await channel.edit(slowmode_delay=0)
            
            await channel.send(f"The slowmode has been removed from this channel.")
            return await ctx.send(f"Removed slowmode from {channel.mention}.")

        created_at = ctx.message.created_at
        delta: datetime.timedelta = duration.dt > (created_at + datetime.timedelta(hours=6))
        
        if delta:
            return await ctx.send("The slowmode cannot be more than 6 hours!")
        
        seconds = (duration.dt - ctx.message.created_at).seconds
        await channel.edit(slowmode_delay=int(seconds))

        human_delay = helpers.human_timedelta(duration.dt, source=created_at)
        
        embed = discord.Embed(description=f"Messages in {channel.mention} can now be sent every {human_delay}")
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(help="Gives a member a role", aliases=['give_role'])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True, manage_roles=True)
    async def giverole(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User], role: discord.Role):
        await member.add_roles(role, reason=f'Added by `{ctx.author}` using command')
        
        embed = discord.Embed(description=f"Successfully gave {member.mention} the {role.mention} role.")
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(help="Removes a role from a member", aliases=['remove_role'])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True, manage_roles=True)
    async def removerole(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User], role: discord.Role):
        await member.remove_roles(role, reason=f'Removed by `{ctx.author}` using command')
        
        embed = discord.Embed(description=f"Successfully removed the {role.mention} role from {member.mention}.")
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="Locks down a specified channel. You can also specify the role. If no channel is specified it will default to the current channel and if no role is specified it will default to the @everyone role.",
        aliases=['lock', 'ld'])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def lockdown(self, ctx: CustomContext, channel: typing.Optional[discord.TextChannel], role: typing.Optional[discord.Role]):
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
    async def unlock(self, ctx: CustomContext, channel: typing.Optional[discord.TextChannel], role: typing.Optional[discord.Role]):
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

    @commands.command(
        help="Mutes the specified member forever.",
        brief="mute @Joy Spamming in #general :angy:")
    @ensure_muterole()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx: CustomContext, member: discord.Member, *, reason: str = None):
        if member.id == ctx.author.id:
            return await ctx.send("You can't mute yourself!")

        if member.id == self.client.user.id:
            return await ctx.send("Noooo! Don't mute me :(")

        if member.id == ctx.guild.owner.id:
            return await ctx.send("You can't mute the owner of this server!")

        if member.guild_permissions.administrator:
            return await ctx.send("You can't mute that user since they have the administrator permission!")

        if isinstance(member, discord.Member):
            if member.top_role >= ctx.me.top_role:
                raise errors.Forbidden

        if reason is None or len(reason) > 500:
            reason = "Reason was not provided or it exceeded the 500-character limit."

        role = await muterole(ctx)

        await member.add_roles(role,
                               reason=f"Muted by {ctx.author} ({ctx.author.id}) {f'for: {reason}' if reason else ''}"[
                                      0:500])

        await self.client.db.execute("DELETE FROM temporary_mutes WHERE (guild_id, member_id) = ($1, $2)", ctx.guild.id, member.id)

        self.mute_task()

        if ctx.channel.permissions_for(role).send_messages_in_threads:
            try:
                embed = discord.Embed(title="Mute role has permissions to create threads!", description=f"""
The mute role in your server (`{ctx.guild.name}`) has permissions to create threads!
You may want to fix that using the `mute_role fix` command.
                """, color=discord.Color.red())

                await ctx.author.send(embed=embed)

            except:
                pass

        embed = discord.Embed(description=f"Successfully muted `{member}` for `{reason}`", color=discord.Color.green())
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        return await ctx.send(embed=embed)

    @commands.command(
        help="Unmutes the specified member",
        aliases=['un_mute', 'un-mute'],
        brief="unmute @Jeff Good guy")
    @ensure_muterole()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(self, ctx: CustomContext, member: discord.Member, *, reason: str = None):
        if member.id == ctx.author.id:
            return await ctx.send("You can't un-mute yourself!")

        if member.id == self.client.user.id:
            return await ctx.send("Noooo! Don't un-mute me :(")

        if member.id == ctx.guild.owner.id:
            return await ctx.send("You can't un-mute the owner of this server!")

        if member.guild_permissions.administrator:
            return await ctx.send("You can't un-mute that user since they have the administrator permission!")

        if isinstance(member, discord.Member):
            if member.top_role >= ctx.me.top_role:
                raise errors.Forbidden

        if reason is None or len(reason) > 500:
            reason = "Reason was not provided or it exceeded the 500-character limit."

        role = await muterole(ctx)

        await member.remove_roles(role, reason=f"Unmuted by {ctx.author} ({ctx.author.id}) {f'for {reason}' if reason else ''}"[0:500])

        await self.client.db.execute("DELETE FROM temporary_mutes WHERE (guild_id, member_id) = ($1, $2)", ctx.guild.id, member.id)

        self.mute_task()

        embed = discord.Embed(description=f"Successfully un-muted `{member}` for `{reason}`", color=discord.Color.green())
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        return await ctx.send(embed=embed)

    @commands.command(
        help="Temporary mutes the specified member for the specified duration.\nDuration must be a short time for example: 1h, 2d, 5m or a combination of those like 1h2d5m",
        aliases=['temp_mute', 'temp-mute', 'tmute'],
        brief="tempmute @Noob 5h\ntempmute @Cat 5m1s")
    @ensure_muterole()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def tempmute(self, ctx: CustomContext, member: discord.Member, *, duration: time_inputs.ShortTime):
        if member.id == ctx.author.id:
            return await ctx.send("You can't temp-mute yourself!")

        if member.id == self.client.user.id:
            return await ctx.send("Noooo! Don't temp-mute me :(")

        if member.id == ctx.guild.owner.id:
            return await ctx.send("You can't temp-mute the owner of this server!")

        if member.guild_permissions.administrator:
            return await ctx.send("You can't temp-mute that user since they have the administrator permission!")

        if isinstance(member, discord.Member):
            if member.top_role >= ctx.me.top_role:
                raise errors.Forbidden

        role = await muterole(ctx)

        created_at = ctx.message.created_at
        if duration.dt < (created_at + datetime.timedelta(minutes=1)):
            return await ctx.send("You can't temp-mute someone for less than a minute!")

        delta = helpers.human_timedelta(duration.dt, source=created_at)

        try:
            await member.add_roles(role, reason=f"Temporary mute by {ctx.author} ({ctx.author.id})")

        except discord.Forbidden:
            return await ctx.send(f"I don't seem to have permissions to add the `{role.name}` role")

        await self.client.db.execute("INSERT INTO temporary_mutes(guild_id, member_id, reason, end_time) VALUES ($1, $2, $3, $4) ON CONFLICT (guild_id, member_id) DO UPDATE SET reason = $3, end_time = $4", ctx.guild.id, member.id, f"Temporary mute by {ctx.author} ({ctx.author.id})", duration.dt)

        self.mute_task()

        embed = discord.Embed(description=f"Successfully temp-muted `{member}` for `{delta}`", color=discord.Color.green())
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        return await ctx.send(embed=embed)
