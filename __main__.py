# Imports

import discord
import logging
import os
import aiohttp
import random
import errors
import yaml
import time
import random
import traceback
import re
import prsaw
import topgg
from discord.ext import commands, ipc
import asyncpg
import typing
import asyncpraw
from discord import Interaction
from typing import Optional
from asyncdagpi import Client, ImageFeatures
import pomice

PRE: tuple = ("sb!",)

with open(r'/root/stealthbot/config.yaml') as file:
    full_yaml = yaml.load(file)
yaml_data = full_yaml

target_type = typing.Union[discord.Member, discord.User, discord.PartialEmoji, discord.Guild, discord.Invite]

class ConfirmButton(discord.ui.Button):
    def __init__(self, label: str, emoji: str, button_style: discord.ButtonStyle):
        super().__init__(style=button_style, label=label, emoji=emoji, )

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: Confirm = self.view
        view.value = True
        view.stop()


class CancelButton(discord.ui.Button):
    def __init__(self, label: str, emoji: str, button_style: discord.ButtonStyle):
        super().__init__(style=button_style, label=label, emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: Confirm = self.view
        view.value = False
        view.stop()


class Confirm(discord.ui.View):
    def __init__(self, buttons: typing.Tuple[typing.Tuple[str]], timeout: int = 30):
        super().__init__(timeout=timeout)
        self.message = None
        self.value = None
        self.ctx: CustomContext = None
        self.add_item(ConfirmButton(emoji=buttons[0][0],
                                    label=buttons[0][1],
                                    button_style=(
                                            buttons[0][2] or discord.ButtonStyle.green
                                    )))
        self.add_item(CancelButton(emoji=buttons[1][0],
                                   label=buttons[1][1],
                                   button_style=(
                                           buttons[1][2] or discord.ButtonStyle.red
                                   )))

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user and interaction.user.id in (self.ctx.bot.owner_id, self.ctx.author.id):
            return True
        messages = [
            "Oh no you can't do that! This belongs to **{user}**",
            'This is **{user}**\'s confirmation, sorry! 💖',
            '😒 Does this look yours? **No**. This is **{user}**\'s confirmation button',
            '<a:stopit:891139227327295519>',
            'HEYYYY!!!!! this is **{user}**\'s menu.',
            'Sorry but you can\'t mess with **{user}**\' menu QnQ',
            'No. just no. This is **{user}**\'s menu.',
            '<:blobstop:749111017778184302>' * 3,
            'You don\'t look like {user} do you...',
            '🤨 Thats not yours! Thats **{user}**\'s',
            '🧐 Whomst! you\'re not **{user}**',
            '_out!_ 👋'
        ]
        await interaction.response.send_message(random.choice(messages).format(user=self.ctx.author.display_name),
                                                ephemeral=True)

        return False


class CustomContext(commands.Context):

    @staticmethod
    def tick(option: bool):
        ticks = {
            True: '<:greenTick:895688440690147370>',
            False: '<:redTick:895688440568508518>',
            None: '<:greyTick:895688440690114560>'}

        emoji = ticks.get(option, "<:redTick:596576672149667840>")
        return emoji

    @staticmethod
    def toggle(option: bool):
        ticks = {
            True: '<:toggle_on:896743740285263892>',
            False: '<:toggle_off:896743704323309588>',
            None: '<:toggle_off:896743704323309588>'}

        emoji = ticks.get(option, "<:toggle_off:896743704323309588>")
        return emoji

    @staticmethod
    def time(days: int, hours: int, minutes: int, seconds: int):
        def remove_s(string):
            if re.match(r"\d+", string).group() == "1":
                return string[:-1]
            return string

        days = remove_s(f"{days} days")
        hours = remove_s(f"{hours} hours")
        minutes = remove_s(f"{minutes} minutes")
        seconds = remove_s(f"{seconds} seconds")

        return " and ".join(", ".join(filter(lambda i: int(i[0]), (days, hours, minutes, seconds))).rsplit(", ", 1))

    @staticmethod
    def short_time(days: int, hours: int, minutes: int, seconds: int):
        def remove_s(string):
            if re.match(r"\d+", string).group() == "1":
                return string[:-1]
            return string

        days = remove_s(f"{days}d")
        hours = remove_s(f"{hours}h")
        minutes = remove_s(f"{minutes}m")
        seconds = remove_s(f"{seconds}s")

        return " and ".join(", ".join(filter(lambda i: int(i[0]), (days, hours, minutes, seconds))).rsplit(", ", 1))
    
    @staticmethod
    def members(bot):
        return len(bot.users)
    
    @staticmethod
    def users(bot):
        return len(bot.users)
    
    @staticmethod
    def guilds(bot):
        return len(bot.guilds)
    
    @staticmethod
    def servers(bot):
        return len(bot.guilds)

    async def send(self, content: str = None, embed: discord.Embed = None, reminders: bool = True,
                   reply: bool = True, footer: bool = True, timestamp: bool = True, color: bool = True,
                   reference: typing.Union[discord.Message, discord.MessageReference] = None, **kwargs):

        reference = (reference or self.message.reference or self.message) if reply is True else reference
        
        if self.bot.theme == "default":
            colors = [0x910023, 0xA523FF]
            emotes = []
            unicode_emotes = []
            star_emoji = ":star:"
            
        elif self.bot.theme == "halloween":
            colors = [0xFF9A00, 0x000000, 0x09FF00, 0xC900FF, 0xFBFAF4]
            emotes = [':ghost:', ':jack_o_lantern:']
            unicode_emotes = ['👻', '🎃']
            star_emoji = random.choice(emotes)
            
        elif self.bot.theme == "christmas":
            colors = [0xB3000C, 0xE40010, 0xD8D8D8, 0x1FD537, 0x1FD537]
            emotes = [':santa:', ':christmas_tree:', ':deer:', ':gift:']
            unicode_emotes = ['🎅', '🎄', '🦌', '🎁']
            star_emoji = ":star2:"
            
        else:
            colors = [0x910023, 0xA523FF]
            emotes = []
            unicode_emotes = []
            star_emoji = ":star:"

        if embed:

            if footer:
                embed.set_footer(text=f"{f'{random.choice(unicode_emotes)} ' if unicode_emotes else ''}Requested by {self.author}", icon_url=self.author.display_avatar.url)
                
            if not footer and embed.footer:
                embed.set_footer(text=f"{f'{random.choice(unicode_emotes)} ' if unicode_emotes else ''}{embed.footer.text}", icon_url=embed.footer.icon_url if embed.footer.icon_url else discord.Embed.Empty)

            if timestamp:
                embed.timestamp = discord.utils.utcnow()

            if color:
                color = random.choice(colors)
                embed.color = color

        if reminders:
            answer = f"{star_emoji} Help **Stealth Bot** grow by voting on top.gg: **<https://top.gg/bot/760179628122964008>**"
            number = random.randint(1, 5)

            content = content

            if number == 1:
                content = f"{answer}\n\n{str(content) if content else ''}"

        try:
            return await super().send(content=content, embed=embed, reference=reference, **kwargs)
        
        except discord.HTTPException:
            return await super().send(content=content, embed=embed, reference=None, **kwargs)

    async def confirm(self, message: str = "Do you want to confirm?", embed: discord.Embed = None,
                      # added embed so it's possible to use ctx.confirm with an embed instead of a lame class normal message - P3ter
                      buttons: typing.Tuple[typing.Union[discord.PartialEmoji, str],
                                            str, discord.ButtonStyle] = None, timeout: int = 30,
                      delete_after_confirm: bool = False, delete_after_timeout: bool = False,
                      delete_after_cancel: bool = None):
        delete_after_cancel = delete_after_cancel if delete_after_cancel is not None else delete_after_confirm
        view = Confirm(buttons=buttons or (
            (None, 'Confirm', discord.ButtonStyle.green),
            (None, 'Cancel', discord.ButtonStyle.red)
        ), timeout=timeout)
        view.ctx = self
        if embed and message:  # checks if there was BOTH embed and message and if there wasnt:
            message = await self.send(message, view=view, embed=embed)
        elif embed:  # checks if there was an embed and if there wasnt:
            message = await self.send(view=view, embed=embed)
        else:  # sends the message alone and if it was None it sends the default one "Do you want to confirm?"
            message = await self.send(message, view=view)
        await view.wait()

        if view.value is None:
            try:
                (await message.edit(view=None)) if \
                    delete_after_timeout is False else (await message.delete())
            except (discord.Forbidden, discord.HTTPException):
                pass
            return False

        elif view.value:
            try:
                (await message.edit(view=None)) if \
                    delete_after_confirm is False else (await message.delete())
            except (discord.Forbidden, discord.HTTPException):
                pass
            return True

        else:
            try:
                (await message.edit(view=None)) if \
                    delete_after_cancel is False else (await message.delete())
            except (discord.Forbidden, discord.HTTPException):
                pass
            return False

    async def trigger_typing(self) -> None:
        try:
            await super().trigger_typing()

        except (discord.Forbidden, discord.HTTPException):
            pass

    async def dagpi(self, target: target_type = None, *, feature: ImageFeatures, **kwargs) -> discord.File:
        await self.trigger_typing()
        target = target or self.reference
        return await self.bot.dagpi_request(self, target, feature=feature, **kwargs)

    async def waifu(self, feature: str, **kwargs) -> discord.File:
        await self.trigger_typing()
        return await self.bot.waifu_request(self, feature=feature, **kwargs)

    @property
    def reference(self) -> typing.Optional[discord.Message]:
        return getattr(self.message.reference, 'resolved', None)

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"


async def create_db_pool():
    credentials = {"user": "postgres",
                   "password": "1211",
                   "database": "stealthdb",
                   "host": "localhost"}

    return await asyncpg.create_pool(**credentials)


class StealthBot(commands.Bot): # commands.AutoShardedBot
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

    def blacklist(self, ctx: commands.Context):
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
            activity=discord.Streaming(name="sb!help", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
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
            # shard_count=1,
            command_prefix=self.get_pre
        )

        # Important stuff
        self.allowed_mentions = discord.AllowedMentions.none()
        self._BotBase__cogs = commands.core._CaseInsensitiveDict()
        self.owner_id = 564890536947875868
        self.owner_ids = [564890536947875868, 555818548291829792,
                          349373972103561218]  # 349373972103561218 (LeoCx1000) # 555818548291829792 (Vicente0670)
        self.ipc = ipc.Server(self, secret_key=yaml_data['IPC_SECRET'])
        self.pomice = pomice.NodePool()
        self.db = self.loop.run_until_complete(create_db_pool())
        self.ipc = ipc.Server(self, secret_key=yaml_data['IPC_SECRET'])
        self._topgg = topgg.DBLClient(self, yaml_data['DBL_TOKEN'], autopost=True) # , post_shard_count=True
        self._topgg_webhook = topgg.WebhookManager(self).dbl_webhook('/topgg', yaml_data['DBL_PASSWORD'])
        self.rs = prsaw.RandomStuff(api_key=yaml_data['PRSAW_KEY'], async_mode=True)
        self.add_check(self.guild_only)
        self.add_check(self.maintenance)
        self.add_check(self.blacklist)

        # Tokens
        self.dagpi_cooldown = commands.CooldownMapping.from_cooldown(60, 60, commands.BucketType.default)
        self.dagpi = Client(yaml_data['DAGPI_TOKEN'])
        self.reddit = asyncpraw.Reddit(client_id=yaml_data['ASYNC_PRAW_CLIENT_ID'],
                                       client_secret=yaml_data['ASYNC_PRAW_CLIENT_SECRET'],
                                       user_agent=yaml_data['ASYNC_PRAW_USER_AGENT'],
                                       username=yaml_data['ASYNC_PRAW_USERNAME'],
                                       password=yaml_data['ASYNC_PRAW_PASSWORD'])
        self.session = aiohttp.ClientSession(loop=self.loop)

        # Custom stuff
        self.chatbot_channels = [913851034416324658, 913851042079338586, 914643410357473310]
        self.no_prefix = False
        self.maintenance = False
        self.launch_time = discord.utils.utcnow()
        self.theme = "christmas"

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

        # Useless stuff
        self.brain_cells = 0
        self.user_id = 760179628122964008
        self.token = "haha no"

    def _load_extension(self, name: str):
        try:
            self.load_extension(name)

        except (commands.ExtensionNotFound, commands.ExtensionAlreadyLoaded, commands.NoEntryPointError, commands.ExtensionFailed):
            traceback.print_exc()
            print()

    def _dynamic_cogs(self):
        for filename in os.listdir(f"./cogs"):
            if filename.endswith(".py"):
                cog = filename[:-3]
                logging.info(f"trying to load cog: {cog}")
                self._load_extension(f'cogs.{cog}')

    def dj_only(self, guild: discord.Guild):
        try:
            dj_only = self.dj_modes[guild.id]

        except KeyError:
            dj_only = True

        if dj_only:
            return True

        else:
            return False

    def dj_role(self, guild: discord.Guild):
        try:
            dj_role_id = self.dj_roles[guild.id]
        except KeyError:
            dj_role_id = False

        if dj_role_id:
            role = guild.get_role(dj_role_id)
            return role
        else:
            return False

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

    async def on_ready(self):
        print(f"-------------================----------------")
        print(f"bot name: {self.user.name}")
        print(f"bot ID: {self.user.id}")
        print(f"-------------================----------------")
        print(f"servers: {len(self.guilds)}")
        print(f"users: {len(self.users)}")
        print(f"-------------================----------------")

        # try:
        #     await self.pomice.create_node(
        #         bot=self,
        #         host=yaml_data['NODE1_HOST'],
        #         port=yaml_data['NODE1_PORT'],
        #         password=yaml_data['NODE1_PASSWORD'],S
        #         identifier=yaml_data['NODE1_IDENTIFIER'],
        #         spotify_client_id=yaml_data['SPOTIFY_CLIENT_ID'],
        #         spotify_client_secret=yaml_data['SPOTIFY_CLIENT_SECRET'],
        #     )
        #     print("node1 has successfully been loaded")
            
        # except:
        #     print("an unexpected error occurred while loading node1")

        try:
            await self.pomice.create_node(
                bot=self,
                host=yaml_data['NODE2_HOST'],
                port=yaml_data['NODE2_PORT'],
                password=yaml_data['NODE2_PASSWORD'],
                identifier=yaml_data['NODE2_IDENTIFIER'],
                spotify_client_id=yaml_data['SPOTIFY_CLIENT_ID'],
                spotify_client_secret=yaml_data['SPOTIFY_CLIENT_SECRET'],
            )
            print("node2 has successfully been loaded")
            
        except:
            print("an unexpected error occurred while loading node2")

        try:
            await self.pomice.create_node(
                bot=self,
                host=yaml_data['NODE3_HOST'],
                port=yaml_data['NODE3_PORT'],
                password=yaml_data['NODE3_PASSWORD'],
                identifier=yaml_data['NODE3_IDENTIFIER'],
                spotify_client_id=yaml_data['SPOTIFY_CLIENT_ID'],
                spotify_client_secret=yaml_data['SPOTIFY_CLIENT_SECRET'],
            )
            print("node3 has successfully been loaded")
            
        except:
            print("an unexpected error occurred while loading node3")
        
        channel = self.get_channel(895683561737297934)

        values = await self.db.fetch("SELECT user_id, is_blacklisted FROM blacklist")

        for value in values:
            self.blacklist[value['user_id']] = (value['is_blacklisted'] or False)

        print("blacklist system has been loaded")

        values = await self.db.fetch("SELECT guild_id, prefix FROM guilds")

        for value in values:
            if value['prefix']:
                self.prefixes[value['guild_id']] = ((value['prefix'] if value['prefix'][0] else PRE) or PRE)

        for guild in self.guilds:
            try:
                self.prefixes[guild.id]

            except KeyError:
                self.prefixes[guild.id] = PRE

        self.afk_users = dict(
            [(r['user_id'], True) for r in (await self.db.fetch('SELECT user_id, start_time FROM afk')) if
             r['start_time']])

        self.auto_un_afk = dict(
            [(r['user_id'], r['auto_un_afk']) for r in (await self.db.fetch('SELECT user_id, auto_un_afk FROM afk')) if
             r['auto_un_afk'] is not None])

        self.disable_commands_guilds = dict(
            [(r['guild_id'], True) for r in (await self.db.fetch('SELECT guild_id, disable_commands FROM guilds')) if
             r['disable_commands']])

        values = await self.db.fetch("SELECT guild_id, dj_only FROM music")

        for value in values:
            self.dj_modes[value['guild_id']] = (value['dj_only'] or False)

        values = await self.db.fetch("SELECT guild_id, dj_role_id FROM music")

        for value in values:
            self.dj_roles[value['guild_id']] = (value['dj_role_id'] or False)

        self._dynamic_cogs()
        self.load_extension("jishaku")

        print(f"-------------================----------------")
        print("all cogs have successfully been loaded")
        print(f"-------------================----------------")
        
        if os.path.exists("data/restart_log.log"):
            file = open("data/restart_log.log", "r")
            channel_id = int(file.readline())
            file.close()
            
            delay = time.time() - os.path.getctime("data/restart_log.log")
    
            embed = discord.Embed(title="Successfully restarted", description=f"""
This restart took {round(delay, 2)} seconds.
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
        
        
    async def on_dbl_vote(self, data):
        if data["type"] == "test":
            return self.dispatch("dbl_test", data)

        channel = self.get_channel(896775088249122889)
        embed = discord.Embed(title="Received a vote", description=f"""
```
{data}
```
                              """)
        await channel.send(embed=embed)

    async def on_dbl_test(self, data):
        channel = self.get_channel(896775088249122889)
        embed = discord.Embed(title="Received a test vote", description=f"""
```
{data}
```
                              """)
        await channel.send(embed=embed)

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


if __name__ == '__main__':
    bot = StealthBot()
    try:
        bot.ipc.start()
        
    except:
        pass
    
    
    try:
        webhook = discord.SyncWebhook.from_url(yaml_data['UPTIME_WEBHOOK'])
        webhook.send(content=":white_check_mark: Stealth Bot is starting up...")
        bot.run(yaml_data['TOKEN'], reconnect=True)
        
    finally:
        webhook = discord.SyncWebhook.from_url(yaml_data['UPTIME_WEBHOOK'])
        webhook.send(content=":x: Stealth Bot is shutting down...")
