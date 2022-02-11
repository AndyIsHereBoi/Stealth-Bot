import os
import sys
import shutil
import psutil
import errors
import typing
import pathlib
import discord
import humanize

from helpers import helpers
from ._base import UtilityBase
from discord.ext import commands
from helpers.context import CustomContext
from discord.ext.commands.cooldowns import BucketType

def get_ram_usage():
    return int(psutil.virtual_memory().total - psutil.virtual_memory().available)


def get_ram_total():
    return int(psutil.virtual_memory().total)

class Info(UtilityBase):

    @commands.command(
        slash_command=True,
        message_command=True,
        help="Shows information about the specified member. If no member is specified it will default to the author of the message.",
        aliases=['ui', 'user', 'member', 'memberinfo'],
        brief="userinfo\nuserinfo @Andy\nuserinfo Jake#9999")
    @commands.cooldown(1, 5, BucketType.member)
    async def userinfo(self, ctx: CustomContext,
                       member: typing.Union[discord.Member, discord.User] = None) -> discord.Message:
        await ctx.trigger_typing()

        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        if isinstance(member, discord.Member):
            fetched_member = await self.bot.fetch_user(member.id)

            embed = discord.Embed(title=member.name if member.name else "No name",
                                  url=f"https://discord.com/users/{member.id}",
                                  description=f"<:greyTick:895688440690114560> ID: {member.id}")

            embed.add_field(name="__**General**__", value=f"""
<:nickname:895688440912437258> Nick: {member.nick if member.nick else f'{member.name} (No nick)'}
:hash: Discriminator:  #{member.discriminator}
<:mention:908055690277433365> Mention: {member.mention}
:robot: Bot: {'Yes' if member.bot else 'No'} **|** :zzz: AFK {'Yes' if member.id in self.bot.afk_users else 'No'}
                """, inline=True)

            embed.add_field(name="__**Activity**__", value=f"""
{helpers.get_member_status_emote(member)} Status: {helpers.get_member_custom_status(member)}
:video_game: Activity: {helpers.get_member_activity(member)}
<:discord:904442480450224191> Client: {helpers.get_member_client(member)}
<:spotify:899263771342700574> Spotify: {helpers.get_member_spotify(member)}
                """, inline=True)

            embed.add_field(name="__**Something**__", value=f"""
<:invite:895688440639799347> Created: {discord.utils.format_dt(member.created_at, style="F")} ({discord.utils.format_dt(member.created_at, style="R")})
<:joined:895688440786595880> Joined: {discord.utils.format_dt(member.joined_at, style="F")} ({discord.utils.format_dt(member.joined_at, style="R")})
<:boost:858326699234164756> Boosting: {f'{discord.utils.format_dt(member.premium_since, style="F")} ({discord.utils.format_dt(member.premium_since, style="R")})' if member.premium_since else 'Not boosting'}
                """, inline=False)

            embed.add_field(name="__**Assets**__", value=f"""
{helpers.get_member_avatar_urls(member, ctx, member.id)}
{helpers.get_member_banner_urls(fetched_member, ctx, member.id)}
:art: Color: {helpers.get_member_color(member)}
:art: Accent color: {helpers.get_member_accent_color(fetched_member)}
                """, inline=True)

            ack = await self.bot.db.fetchval("SELECT acknowledgment FROM acknowledgments WHERE user_id = $1",
                                                member.id)

            embed.add_field(name="__**Other**__", value=f"""
<:role:895688440513974365> Top role: {member.top_role.mention if member.top_role else 'No top role'}
<:role:895688440513974365> Roles: {helpers.get_member_roles(member, ctx.guild)}
<:staff:895688440887279647> Staff permissions: {helpers.get_member_permissions(member.guild_permissions)}
<a:badges:932296423070896150> Badges: {helpers.get_member_badges(member, fetched_member)}
<:voice_channel:904474834526937120> Voice: {member.voice.channel.mention if member.voice else 'Not in a VC'} {f'**|** Muted: {"Yes" if member.voice.mute or member.voice.self_mute else "No"} **|** Deafened: {"Yes" if member.voice.deaf or member.voice.self_deaf else "No"}' if member.voice else ''}
Mutual servers: {len(member.mutual_guilds) if member.id != 760179628122964008 else 'No mutual servers'}
:star: Acknowledgments: {ack if ack else 'No acknowledgments'}
                """, inline=False)

            view = discord.ui.View()

            if member.avatar:
                item = discord.ui.Button(style=discord.ButtonStyle.gray, emoji="🎨", label="Avatar",
                                         url=member.avatar.url, row=1)
                view.add_item(item=item)

                embed.set_thumbnail(url=member.avatar.url)

            if fetched_member.banner:
                item = discord.ui.Button(style=discord.ButtonStyle.gray, emoji="🎨", label="Banner",
                                         url=fetched_member.banner.url, row=1)
                view.add_item(item=item)

            if discord.utils.find(lambda act: isinstance(act, discord.Spotify), member.activities):
                item = discord.ui.Button(style=discord.ButtonStyle.gray, emoji="<:spotify:899263771342700574>",
                                         label="Spotify",
                                         url=discord.utils.find(lambda act: isinstance(act, discord.Spotify),
                                                                member.activities).track_url, row=2)
                view.add_item(item=item)

            return await ctx.send(embed=embed, view=view)

        elif isinstance(member, discord.User):

            fetched_member = await self.bot.fetch_user(member.id)

            embed = discord.Embed(title=member.name if member.name else "No name",
                                  url=f"https://discord.com/users/{member.id}",
                                  description=f"*Less info cause this is a user not a member*\n<:greyTick:596576672900186113> ID: {member.id}")

            embed.add_field(name="__**General**__", value=f"""
:hash: Discriminator:  #{member.discriminator}
<:mention:908055690277433365> Mention: {member.mention}
:robot: Bot: {'Yes' if member.bot else 'No'} **|** :zzz: AFK {'Yes' if member.id in self.bot.afk_users else 'No'}
                """, inline=True)

            ack = await self.bot.db.fetchval("SELECT acknowledgment FROM acknowledgments WHERE user_id = $1",
                                                member.id)

            embed.add_field(name="__**Something**__", value=f"""
<:invite:895688440639799347> Created: {discord.utils.format_dt(member.created_at, style="F")} ({discord.utils.format_dt(member.created_at, style="R")})
:star: Acknowledgments: {ack if ack else 'No acknowledgments'}
                """, inline=False)

            embed.add_field(name="__**Assets**__", value=f"""
{helpers.get_member_avatar_urls(member, ctx, member.id)}
Banner: {helpers.get_member_banner_urls(fetched_member, ctx, member.id)}
:rainbow: Color: {helpers.get_member_color(member)}
:rainbow: Accent color: {helpers.get_member_accent_color(member)}
                """, inline=True)

            if member.avatar:
                embed.set_thumbnail(url=member.avatar.url)

            # embed.add_field(name="__**Join order**__", value=f"""
            # {helpers.get_join_order(member, ctx.guild)}
            # """, inline=False)

            return await ctx.send(embed=embed)

        else:
            raise errors.UnknownError

    @commands.command(
        help="Shows information about the specified server. If no server is specified it will default to the current server.",
        aliases=['si', 'guild', 'guildinfo'])
    async def serverinfo(self, ctx: CustomContext) -> discord.Message:
        await ctx.trigger_typing()
        guild = ctx.guild

        embed = discord.Embed(title=guild.name if guild.name else 'No name', description=f"""
<:greyTick:895688440690114560> ID: {guild.id}
<:info:888768239889424444> Description: {guild.description if guild.description else 'No description'}
        """)

        embed.add_field(name="<:text_channel:904473407524048916> __**Channels**__", value=f"""
<:text_channel:904473407524048916> Text: {len(guild.text_channels):,}
<:voice_channel:904474834526937120> Voice: {len(guild.voice_channels):,}
<:category:895688440220356669> Category: {len(guild.categories):,}
<:stage_channel:904474823927926785> Stages: {len(guild.stage_channels):,}
<:thread_channel:904474878390968412> Threads: {len(guild.threads):,}
(only threads
visible by me)
        """, inline=True)

        embed.add_field(name="<:emoji_ghost:895414463354785853> __**Emojis**__", value=f"""
Animated: {len([e for e in guild.emojis if not e.animated]):,}/{guild.emoji_limit:,}
Static: {len([e for e in guild.emojis if e.animated]):,}/{guild.emoji_limit:,}
<:stickers:906902448243892244> __**Stickers**__
Total: {len(guild.stickers):,}/{guild.sticker_limit:,}
        """, inline=True)

        embed.add_field(name="<:boost:858326699234164756> __**Boosts**__", value=f"""
{helpers.get_guild_boosts(guild)}
        """, inline=True)

        embed.add_field(name="<:members:858326990725709854> __**Members**__", value=f"""
:bust_in_silhouette: Humans: {len([m for m in guild.members if not m.bot]):,}
:robot: Bots: {len([m for m in guild.members if m.bot]):,}
:infinity: Total: {len(guild.members):,}
:file_folder: Limit: {guild.max_members:,}
:tools: Admins: {len([m for m in guild.members if m.guild_permissions.administrator]):,}
        """, inline=True)

        embed.add_field(name="<:status_offline:925709091328897074> __**Member statuses**__", value=f"""
<:status_online:925709091375026246> Online: {len([m for m in guild.members if m.status is discord.Status.online]):,}
<:status_idle:925709091312132126> Idle: {len([m for m in guild.members if m.status is discord.Status.idle]):,}
<:status_dnd:925709090997538867> Dnd: {len([m for m in guild.members if m.status is discord.Status.dnd]):,}
<:status_streaming:925709091396018186> Streaming: {len([m for m in guild.members if discord.utils.find(lambda a: isinstance(a, discord.Streaming), m.activities)]):,}
<:status_offline:925709091328897074> Offline: {len([m for m in guild.members if m.status is discord.Status.offline]):,}
        """, inline=True)

        embed.add_field(name="<:gear:899622456191483904> __**Other**__", value=f"""
<:role:895688440513974365> Roles: {len(guild.roles):,}
{helpers.get_server_region_emote(guild)} Region: {helpers.get_server_region(guild)}
:file_folder: Filesize limit: {humanize.naturalsize(guild.filesize_limit)}
<:voice_channel:904474834526937120> Voice bit-rate: {humanize.naturalsize(guild.bitrate_limit)}
{helpers.get_server_verification_level_emote(guild)} Verification level: {str(guild.verification_level).title()}
:calendar_spiral: Created: {discord.utils.format_dt(guild.created_at, style="f")} ({discord.utils.format_dt(guild.created_at, style="R")})
<:nsfw:906587263624945685> Explicit content filter: {helpers.get_server_explicit_content_filter(guild)}
        """, inline=False)

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        return await ctx.send(embed=embed)
    
    @commands.command(
        help="Shows basic information about the bot.",
        aliases=['bi', 'about', 'info'])
    async def botinfo(self, ctx: CustomContext):
        _commands = await self.bot.db.fetch("SELECT * FROM commands")

        shards_guilds = {i: {"guilds": 0, "users": 0} for i in range(len(self.bot.shards))}
        for guild in self.bot.guilds:
            shards_guilds[guild.shard_id]["guilds"] += 1
            shards_guilds[guild.shard_id]["users"] += guild.member_count

        p = pathlib.Path('../')
        cm = cr = fn = cl = ls = fc = 0
        for f in p.rglob('*.py'):
            if str(f).startswith("venv"):
                continue
            fc += 1
            with f.open() as of:
                for l in of.readlines():
                    l = l.strip()
                    if l.startswith('class'):
                        cl += 1
                    if l.startswith('def'):
                        fn += 1
                    if l.startswith('async def'):
                        cr += 1
                    if '#' in l:
                        cm += 1
                    ls += 1

        delta_uptime = discord.utils.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        total, used, free = shutil.disk_usage("/")

        embed = discord.Embed(title="Bot info", description=f"""
[Invite me](https://discord.com/api/oauth2/authorize?client_id=760179628122964008&permissions=8&scope=bot%20applications.commands) **|** [Support server](https://discord.gg/MrBcA6PZPw) **|** [Vote](https://top.gg/bot/760179628122964008) **|** [Website](https://stealthbot.xyz)

I'm a discord bot made by Ender2K89#9999.
I've been on discord since {discord.utils.format_dt(ctx.me.created_at)} ({discord.utils.format_dt(ctx.me.created_at, style='R')})
I have a lot of features such as moderation, fun, info and more!
I've been online for {ctx.time(days=days, hours=hours, minutes=minutes, seconds=seconds)}.
                              """)

        embed.add_field(name=f"__**Numbers**__", value=f"""
Guilds: `{len(self.bot.guilds):,}`
Users: `{len(self.bot.users):,}`
Commands: `{len(_commands):,}`
Commands used: `{self.bot.commands_used:,}`
Messages seen: `{self.bot.messages_count:,}`
                        """, inline=True)

        embed.add_field(name=f"__**System**__", value=f"""
PID: `{os.getpid()}`
CPU: `{round(psutil.cpu_percent())}%`/`100%`
RAM: `{int(get_ram_usage() / 1024 / 1024)}MB`/`{int(get_ram_total() / 1024 / 1024)}MB`
Disk: `{used // (2 ** 30)}GB`/`{total // (2 ** 30)}GB`
Python: `{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}`
                          """, inline=True)

        embed.add_field(name=f"__**Files**__", value=f"""
Files: `{fc:,}`
Lines: `{ls:,}`
Classes: `{cl:,}`
Functions: `{fn:,}`
Courtines: `{cr:,}`
                          """, inline=True)

        embed.add_field(name=f"__**Latest changes**__", value=ctx.get_last_commits(5), inline=False)

        for shard_id, shard in self.bot.shards.items():
            embed.add_field(name=f"__**Shard #{shard_id}**__", value=f"""
Latency: `{round(shard.latency * 1000)}`ms{' ' * (9 - len(str(round(shard.latency * 1000, 3))))}
Guilds: `{shards_guilds[shard_id]['guilds']:,}`
Users: `{shards_guilds[shard_id]['users']:,}`
            """, inline=True)

        await ctx.send(embed=embed)

    @commands.command(
        help="Shows information about the specified role. If no role is specified it will default to the author's top role.",
        aliases=['ri'],
        brief="roleinfo @Members\nroleinfo Admim\nroleinfo 799331025724375040")
    async def roleinfo(self, ctx: CustomContext, role: discord.Role = None):
        if role is None:
            role = ctx.author.top_role

        embed = discord.Embed(title=f"{role}", description=f"""
Mention: {role.mention}
ID: {role.id}

Color: {role.color}
Position: {role.position}
Members: {len(role.members)}
Creation date: {discord.utils.format_dt(role.created_at, style="f")} ({discord.utils.format_dt(role.created_at, style="R")})

Permissions: {helpers.get_member_permissions(role.permissions)}
        """)

        await ctx.send(embed=embed)