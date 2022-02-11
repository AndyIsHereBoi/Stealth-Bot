# Imports

import io
import os
import re
import ast
import time
import yaml
import topgg
import prsaw
import topgg
import typing
import pomice
import errors
import inspect
import mystbin
import asyncpg
import discord
import logging
import aiohttp
import asyncpraw
import traceback

from typing import Optional
from discord.ext import commands, ipc
from helpers.context import CustomContext
from asyncdagpi import Client, ImageFeatures
from helpers.helpers import LoggingEventsFlags
from collections import defaultdict, deque, namedtuple
from helpers.paginator import PersistentExceptionView, PersistentVerifyView

# Mobile status
def source(o):
    s = inspect.getsource(o).split("\n")
    indent = len(s[0]) - len(s[0].lstrip())
    return "\n".join(i[indent:] for i in s)

source_ = source(discord.gateway.DiscordWebSocket.identify)

patched = re.sub(
    r'([\'"]\$browser[\'"]:\s?[\'"]).+([\'"])',
    r"\1Discord Android\2",
    source_
)

loc = {}
exec(compile(ast.parse(patched), "<string>", "exec"), discord.gateway.__dict__, loc)
discord.gateway.DiscordWebSocket.identify = loc["identify"]

PRE: tuple = ("sb!",)

with open(r'/root/stealthbot/config.yaml') as file:
    full_yaml = yaml.load(file)
yaml_data = full_yaml

initial_extensions = (
    'jishaku',
)

extensions = ('cogs.events', 'cogs.fun', 'cogs.images', 'cogs.owner', 'cogs.utility')

target_type = typing.Union[discord.Member, discord.User, discord.PartialEmoji, discord.Guild, discord.Invite]

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"


async def create_db_pool():
    credentials = {"user": "postgres",
                   "password": "1211",
                   "database": "stealthdb",
                   "host": "localhost"}

    return await asyncpg.create_pool(**credentials)

class StealthBot(commands.AutoShardedBot):
    PRE: tuple = ("sb!",)

    def guild_only(self, ctx: commands.Context):
        if ctx.message.guild:
            return True

        else:
            raise commands.NoPrivateMessage("This command can't be used in DM channels.")

    def maintenance(self, ctx: commands.Context):
        if not self.maintenance or ctx.author.id == bot.owner_id:
            return True

        else:
            raise errors.BotMaintenance

    def blacklist_check(self, ctx: commands.Context):
        try:
            is_blacklisted = self.blacklist[ctx.author.id]

        except KeyError:
            is_blacklisted = False

        if ctx.author.id == self.owner_id:
            is_blacklisted = False

        if is_blacklisted is False:
            return True

        else:
            raise errors.AuthorBlacklisted

    def __init__(self):
        super().__init__(
            activity=discord.Game(name="sb!help"),
            intents=discord.Intents(
                guild_reactions=True,  # reaction add/remove/clear
                guild_messages=True,  # message create/update/delete
                guilds=True,  # guild/channel join/remove/update
                integrations=True,  # integrations update
                voice_states=True,  # voice state update
                dm_reactions=True,  # reaction add/remove/clear
                guild_typing=True,  # on typing
                dm_messages=True,  # message create/update/delete
                presences=True,  # member/user update for games/activities
                dm_typing=True,  # on typing
                webhooks=True,  # webhook update
                members=True,  # member join/remove/update
                invites=True,  # invite create/delete
                emojis=True,  # emoji update
                bans=True),  # member ban/unban
            case_insensitive=True,
            help_command=None,
            enable_debug_events=True,
            strip_after_prefix=True,
            shard_count=1,
            command_prefix=self.get_pre
        )

        # Important stuff
        self.allowed_mentions = discord.AllowedMentions.none()
        self._BotBase__cogs = commands.core._CaseInsensitiveDict()
        self.owner_ids = [564890536947875868, 555818548291829792, # Ender and vicente
                          349373972103561218, 675104167345258506, 855775178893426719]  # Leo and yoni and perez
        self.ipc = ipc.Server(self, secret_key=yaml_data['IPC_SECRET'])
        self.pomice = pomice.NodePool()
        self.db = self.loop.run_until_complete(create_db_pool())
        self.ipc = ipc.Server(self, secret_key=yaml_data['IPC_SECRET'])
        self.rs = prsaw.RandomStuff(api_key=yaml_data['PRSAW_KEY'], async_mode=True)
        self.add_check(self.guild_only)
        self.add_check(self.maintenance)
        self.add_check(self.blacklist_check)
        self.persistent_views_added = False

        # Tokens
        self.dagpi_cooldown = commands.CooldownMapping.from_cooldown(60, 60, commands.BucketType.default)
        self.dagpi = Client(yaml_data['DAGPI_TOKEN'])
        self.reddit = asyncpraw.Reddit(client_id=yaml_data['ASYNC_PRAW_CLIENT_ID'],
                                       client_secret=yaml_data['ASYNC_PRAW_CLIENT_SECRET'],
                                       user_agent=yaml_data['ASYNC_PRAW_USER_AGENT'],
                                       username=yaml_data['ASYNC_PRAW_USERNAME'],
                                       password=yaml_data['ASYNC_PRAW_PASSWORD'])
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.mystbin = mystbin.Client()
        self.topggpy = topgg.DBLClient(self, yaml_data['DBL_TOKEN'], autopost=True, post_shard_count=True)

        # Custom stuff
        self.chatbot_channels = [913851034416324658, 913851042079338586, 914643410357473310, 925801564701069322]
        self.no_prefix = False
        self.maintenance = False
        self.launch_time = discord.utils.utcnow()
        self.theme = "default"

        # Cache stuff
        self.afk_users = {}
        self.auto_un_afk = {}
        self.blacklist = {}
        self.prefixes = {}
        self.messages = {}
        self.edited_messages = {}
        self.dj_modes = {}
        self.dj_roles = {}
        self.disable_commands_guilds = {}
        self.dm_webhooks = defaultdict(str)
        log_wh = self.log_webhooks = namedtuple('log_wh',
                                                ['default', 'message', 'member', 'join_leave', 'voice', 'server'])
        self.log_channels: typing.Dict[int, log_wh] = {}
        self.log_cache = defaultdict(lambda: defaultdict(list))
        self.guild_loggings: typing.Dict[int, LoggingEventsFlags] = {}

        # Useless stuff
        self.brain_cells = 0
        self.user_id = 760179628122964008
        self.token = "haha no"
        self.loop.run_until_complete(self.load_cogs())
        self.loop.run_until_complete(self.populate_cache())


    def update_log(self, deliver_type: str, webhook_url: str, guild_id: int):
        guild_id = getattr(guild_id, 'id', guild_id)
        if deliver_type == 'default':
            self.log_channels[guild_id]._replace(default=webhook_url)
        elif deliver_type == 'message':
            self.log_channels[guild_id]._replace(message=webhook_url)
        elif deliver_type == 'member':
            self.log_channels[guild_id]._replace(member=webhook_url)
        elif deliver_type == 'join_leave':
            self.log_channels[guild_id]._replace(join_leave=webhook_url)
        elif deliver_type == 'voice':
            self.log_channels[guild_id]._replace(voice=webhook_url)
        elif deliver_type == 'server':
            self.log_channels[guild_id]._replace(server=webhook_url)


    def dj_only(self, guild: discord.Guild):
        try: dj_only = self.dj_modes[guild.id]
        except KeyError: dj_only = True
        if dj_only: return True
        else: return False
    def dj_role(self, guild: discord.Guild):
        try: dj_role_id = self.dj_roles[guild.id]
        except KeyError: dj_role_id = False
        if dj_role_id: return guild.get_role(dj_role_id)
        else:return False


    async def get_pre(self, bot, message: discord.Message, raw_prefix: Optional[bool] = False):
        if not message:
            return commands.when_mentioned_or(*self.PRE)(bot, message) if not raw_prefix else self.PRE

        if not message.guild:
            return commands.when_mentioned_or(*self.PRE)(bot, message) if not raw_prefix else self.PRE

        try:
            prefix = self.prefixes[message.guild.id]

        except KeyError:
            prefix = (await self.db.fetchval("SELECT prefix FROM guilds WHERE guild_id = $1",
                                             message.guild.id)) or self.PRE
            prefix = prefix if prefix[0] else self.PRE

            self.prefixes[message.guild.id] = prefix

        if await bot.is_owner(message.author) and bot.no_prefix is True:
            return commands.when_mentioned_or(*prefix, "")(bot, message) if not raw_prefix else prefix
        
        return commands.when_mentioned_or(*prefix)(bot, message) if not raw_prefix else prefix


    async def get_context(self, message, *, cls=CustomContext):
        return await super().get_context(message, cls=cls)


    async def on_autopost_success(self):
        channel = self.get_channel(927492170787749938)
        return await channel.send(f"Posted server count ({self.topggpy.guild_count}) and shard count {self.shard_count}")

    def _load_extension(self, ext):
        try:
            self.load_extension(ext)
            print(f"[EXT] {ext} has been loaded")

        except Exception as e:
            print(f"[EXT] {ext} failed to load.\n{type(e).__name__}: {e}")

    async def load_cogs(self) -> None:
        print("[EXT] loading cogs...")
        for ext in initial_extensions:
            self._load_extension(ext)

        for ext in extensions:
            self._load_extension(ext)

    async def populate_cache(self):
        print("[CACHE] populating cache...")
        # BLACKLIST
        values = await self.db.fetch("SELECT user_id, is_blacklisted FROM blacklist")

        for value in values:
            self.blacklist[value['user_id']] = (value['is_blacklisted'] or False)

        print("[CACHE] blacklist has been loaded")
        # BLACKLIST

        # PREFIXES
        values = await self.db.fetch("SELECT guild_id, prefix FROM guilds")

        for value in values:
            if value['prefix']:
                self.prefixes[value['guild_id']] = ((value['prefix'] if value['prefix'][0] else PRE) or PRE)

        for guild in self.guilds:
            try:
                self.prefixes[guild.id]

            except KeyError:
                self.prefixes[guild.id] = PRE

        print("[CACHE] prefixes have been loaded")
        # PREFIXES

        # AFK
        self.afk_users = dict(
            [(r['user_id'], True) for r in (await self.db.fetch('SELECT user_id, start_time FROM afk')) if
             r['start_time']])

        self.auto_un_afk = dict(
            [(r['user_id'], r['auto_un_afk']) for r in (await self.db.fetch('SELECT user_id, auto_un_afk FROM afk')) if
             r['auto_un_afk'] is not None])

        print("[CACHE] afk users have been loaded")
        # AFK

        # DISABLE COMMANDS GUILDS
        self.disable_commands_guilds = dict(
            [(r['guild_id'], True) for r in (await self.db.fetch('SELECT guild_id, disable_commands FROM guilds')) if
             r['disable_commands']])

        print("[CACHE] disable command guilds have been loaded")
        # DISABLE COMMANDS GUILDS

        # MUSIC STUFF
        values = await self.db.fetch("SELECT guild_id, dj_only FROM music")

        for value in values:
            self.dj_modes[value['guild_id']] = (value['dj_only'] or False)

        values = await self.db.fetch("SELECT guild_id, dj_role_id FROM music")

        for value in values:
            self.dj_roles[value['guild_id']] = (value['dj_role_id'] or False)

        print("[CACHE] music stuff has been loaded")
        # MUSIC STUFF

        # LOGGING STUFF
        for entry in await self.db.fetch('SELECT * FROM log_channels'):
            guild_id = entry['guild_id']
            await self.db.execute('INSERT INTO logging_events(guild_id) VALUES ($1) ON CONFLICT (guild_id) DO NOTHING',
                                  entry['guild_id'])

            self.log_channels[guild_id] = self.log_webhooks(default=entry['default_channel'],
                                                            message=entry['message_channel'],
                                                            join_leave=entry['join_leave_channel'],
                                                            member=entry['member_channel'],
                                                            voice=entry['voice_channel'],
                                                            server=entry['server_channel'])

            flags = dict(await self.db.fetchrow(
                'SELECT message_delete, message_purge, message_edit, member_join, member_leave, member_update, user_ban, user_unban, '
                'user_update, invite_create, invite_delete, voice_join, voice_leave, voice_move, voice_mod, emoji_create, emoji_delete, '
                'emoji_update, sticker_create, sticker_delete, sticker_update, server_update, stage_open, stage_close, channel_create, '
                'channel_delete, channel_edit, role_create, role_delete, role_edit FROM logging_events WHERE guild_id = $1',
                guild_id))
            self.guild_loggings[guild_id] = LoggingEventsFlags(**flags)

        print("[CACHE] logging guilds have been loaded")
        # LOGGING STUFF



    async def on_ready(self):
        print(f"-------------================----------------")
        print(f"bot name: {self.user.name}")
        print(f"bot ID: {self.user.id}")
        print(f"-------------================----------------")
        print(f"servers: {len(self.guilds)}")
        print(f"users: {len(self.users)}")
        print(f"-------------================----------------")

        await self.pomice.create_node(
            bot=self,
            host=yaml_data['NODE2_HOST'],
            port=yaml_data['NODE2_PORT'],
            password=yaml_data['NODE2_PASSWORD'],
            identifier=yaml_data['NODE2_IDENTIFIER'],
            spotify_client_id=yaml_data['SPOTIFY_CLIENT_ID'],
            spotify_client_secret=yaml_data['SPOTIFY_CLIENT_SECRET'],
        )

        # PERSISTENT VIEWS
        self.add_view(PersistentExceptionView(self))
        self.persistent_views_added = True


        if os.path.exists("data/restart_log.log"):
            file = open("data/restart_log.log", "r")
            channel_id = int(file.readline())
            file.close()
            
            delay = time.time() - os.path.getctime("data/restart_log.log")
    
            embed = discord.Embed(title="Successfully restarted", description=f"""
This restart took {delay} seconds.
                                      """, color=discord.Color.green())
            
            await self.get_channel(channel_id).send(embed=embed)


    async def on_message(self, message: discord.Message):
        # wait until bot is ready
        await self.wait_until_ready()

        # send a message if bot is pinged
        if self.user:
            # check if bot.mention is in message.content
            if re.fullmatch(rf"<@!?{bot.user.id}>", message.content):
                return await message.reply("fuck you", mention_author=False)

        # process commands
        await self.process_commands(message)

    async def dagpi_request(self, ctx, target: target_type = None, *, feature: ImageFeatures, **kwargs):
        bucket = self.dagpi_cooldown.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(commands.Cooldown(60, 60), retry_after, commands.BucketType.default)
        if isinstance(target, discord.Emoji):
            url = target.url
            
        elif isinstance(target, discord.PartialEmoji):
            url = target.url
        
        else:
            target = target or ctx.author
            url = getattr(target, "display_avatar", None) or getattr(target, "icon", None) or getattr(target, "guild",
                                                                                                    None) or target
            url = getattr(getattr(url, "icon", url), "url", url)
            
        request = await self.dagpi.image_process(feature, url, **kwargs)
        return discord.File(fp=request.image, filename=f"{str(feature)}.{request.format}")

    async def on_error(self, event_method: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        traceback_string = traceback.format_exc()
        for line in traceback_string.split('\n'):
            logging.info(line)

        await self.wait_until_ready()
        channel = self.get_channel(914145662520659998)
        send = f"""
```py
Event {event_method} raised the following error:
{traceback_string}
```"""

        if len(send) < 2000:
            try:
                await channel.send(send)

            except (discord.Forbidden, discord.HTTPException):
                await channel.send(f"""
```py
Event {event_method} raised the following error:
```
                """, file=discord.File(io.StringIO(traceback_string), filename="traceback.py"))

        else:
            await channel.send(f"""
```py
Event {event_method} raised the following error:
```
                """, file=discord.File(io.StringIO(traceback_string), filename="traceback.py"))


if __name__ == '__main__':
    bot = StealthBot()
    bot.ipc.start()

    try:
        webhook = discord.SyncWebhook.from_url(yaml_data['UPTIME_WEBHOOK'])
        webhook.send(content=":white_check_mark: Stealth Bot is starting up...")
        bot.run(yaml_data['TOKEN'], reconnect=True)
        
    finally:
        webhook = discord.SyncWebhook.from_url(yaml_data['UPTIME_WEBHOOK'])
        webhook.send(content=":x: Stealth Bot is shutting down...")
