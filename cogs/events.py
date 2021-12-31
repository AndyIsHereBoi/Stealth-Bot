import io
import re
import copy
import yaml
import typing
import random
import errors
import difflib
import aiohttp
import discord
import inspect
import itertools
import traceback

from discord import Webhook
from helpers import helpers as helpers
from discord.ext import commands, menus
from helpers.context import CustomContext
from helpers.paginator import PersistentExceptionView


with open(r'/root/stealthbot/config.yaml') as file:
    full_yaml = yaml.load(file)
yaml_data = full_yaml


def conv_n(tuple_acc):
    returning = ""
    op_list_v = []
    op_list_n = list(tuple_acc)

    for i in range(len(op_list_n)):
        op_list_v.append(op_list_n[i].__name__.replace("Converter", ""))

    for i in range(len(op_list_v)):
        if i + 3 <= len(op_list_v):
            returning += f"{op_list_v[i].lower()}, "

        elif i + 2 <= len(op_list_v):
            returning += f"{op_list_v[i].lower()} or "

        else:
            returning += f"{op_list_v[i].lower()}"

    return returning


def join_literals(annotation: inspect.Parameter.annotation, return_list: bool = False):
    if typing.get_origin(annotation) is typing.Literal:
        arguments = annotation.__args__

        if return_list is False:
            return '[' + '|'.join(arguments) + ']'

        else:
            return list(arguments)

    return None


class AFKUsersEmbedPage(menus.ListPageSource):
    def __init__(self, data):
        self.data = data
        super().__init__(data, per_page=20)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        colors = [0x910023, 0xA523FF]
        color = random.choice(colors)
        embed = discord.Embed(title=f"It looks like some of the users, that you just mentioned, are AFK",
                              description="\n".join(f'{i + 1}. {v}' for i, v in enumerate(entries, start=offset)),
                              timestamp=discord.utils.utcnow(), color=color)
        return embed


def setup(client):
    client.add_cog(Events(client))

class ColorRoles:
    roles = {
        "<a:dark_red_flame:926390853415624735>": 925071980275859476, # Dark Red
        "<a:red_flame:926390860470448138>": 925072299940544552, # Red
        "🟥": 925072340453302374, # Light Red

        "<a:yellow_flame:926391276532793394>": 925072506413531206, # Yellow
        "<:gold_ingot:926391443726143549>": 925072609719246858, # Gold
        "🧡": 925072900522917888, # Orange
        "🟧": 925072937025949716, # Light Orange

        "💙": 925072395902005318, # Dark Blue
        "🟦": 925072439652778025, # Blue
        "🔵": 925072473651814440, # Light Blue

        "🍏": 925073028025581639, # Dark Green
        "<:green_sparkle:919660572310667294>": 925073079183503410, # Green
        "🟩": 925073105586647080, # Light Green

        "🟪": 925073254979350528, # Dark Purple
        "🟣": 925073130190417960, # Purple
        "❤️": 925073303348056096, # Pink
        "<:pink_sparkle:919660699674902528>": 925073341314891886, # Light Pink

        "🤎": 925073380804292618, # Brown
        "<a:black_flame:926393087989780480>": 925073459304861716, # Black
        "🕶️": 925073518754922617, # Dark Gray
        "<:cat_paw:926393214313852928>": 925073553999663196, # Gray
        "🔳": 925073584748109854, # Light Gray
        "🤍": 925073620416479303, # White
    }

class Events(commands.Cog):
    """Just some events.. but how did you find this cog?..."""

    def __init__(self, client):
        self.hidden = True
        self.client = client
        self.colours = {}
        
        self.select_emoji = "<:hypesquad:895688440610422900>"
        self.select_brief = "Just some events.. but how did you find this cog?..."
        
        if not hasattr(self.client, 'commands_used'):
            self.client.commands_used = 0
            
        if not hasattr(self.client, 'messages_count'):
            self.client.messages_count = 0
            
        if not hasattr(self.client, 'edited_messages_count'):
            self.client.edited_messages_count = 0

    @commands.Cog.listener('on_raw_reaction_add')
    async def reaction_roles(self, payload: discord.RawReactionActionEvent):
        print("event called")
        roles = {
            ":dark_red_flame:": 925071980275859476,  # Dark Red
            ":red_flame:": 925072299940544552,  # Red
            ":red_square:": 925072340453302374,  # Light Red

            ":yellow_flame:": 925072506413531206,  # Yellow
            ":gold_ingot:": 925072609719246858,  # Gold
            ":orange_heart:": 925072900522917888,  # Orange
            ":orange_square:": 925072937025949716,  # Light Orange

            ":blue_heart:": 925072395902005318,  # Dark Blue
            ":blue_square:": 925072439652778025,  # Blue
            ":blue_circle:": 925072473651814440,  # Light Blue

            ":green_apple:": 925073028025581639,  # Dark Green
            ":green_sparkle:": 925073079183503410,  # Green
            ":green_square:": 925073105586647080,  # Light Green

            ":purple_square:": 925073254979350528,  # Dark Purple
            ":purple_circle:": 925073130190417960,  # Purple
            ":heart:": 925073303348056096,  # Pink
            ":pink_sparkle:": 925073341314891886,  # Light Pink

            ":brown_heart:": 925073380804292618,  # Brown
            ":black_flame:": 925073459304861716,  # Black
            ":dark_sunglasses:": 925073518754922617,  # Dark Gray
            ":cat_paw:": 925073553999663196,  # Gray
            ":white_square_button:": 925073584748109854,  # Light Gray
            ":white_heart:": 925073620416479303,  # White
        }

        if payload.member.bot or payload.channel_id != 926390126827937872 or not payload.member.guild:
            print("member was a bot or the channel was incorrect or it wasnt a guild")
            return

        if role := roles.get(str(payload.emoji)):
            print("first if statement")
            if role := payload.member.guild.get_role(role):
                print("second if statement, giving role.")
                await payload.member.add_roles(role)

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
    async def send_unexpected_error(ctx, error, **kwargs):
        channel = ctx.bot.get_channel(914145662520659998)
        traceback_string = "".join(traceback.format_exception(etype=None, value=error, tb=error.__traceback__))


        data = f"""
Author: {ctx.author} ({ctx.author.id})
Channel: {ctx.channel} ({ctx.channel.id})
Guild: {ctx.guild} ({ctx.guild.id})
Owner: {ctx.guild.owner} ({ctx.guild.owner.id})

Bot admin?: {ctx.me.guild_permissions.administrator}
Role position: {ctx.me.top_role.position}

Message: {ctx.message}"""

        send = f"""
```yaml
{data}
```
```py
Command {ctx.command} raised the following error:
{traceback_string}
```"""

        try:
            if len(send) < 2000:
                await channel.send(send, view=PersistentExceptionView(ctx.bot))

            else:
                await channel.send(f"""
```yaml
{data}
```
```py
Command {ctx.command} raised the following error:
```
                """, file=discord.File(io.StringIO(traceback_string), filename="traceback.py"), view=PersistentExceptionView(ctx.bot))

        finally:
            print(f"{ctx.command} raised an unexpected error")


    @commands.Cog.listener()
    async def on_autopost_success(self):
        channel = self.client.get_channel(896775088249122889)
        
        embed = discord.Embed(title="Successfully posted to top.gg!")
        await channel.send(embed=embed)

#     @commands.Cog.listener('on_dbl_vote')
#     async def on_vote(self, data):
#         channel = self.client.get_channel(913532734528446484)
#         user = await self.client.fetch_user(data["user"])

#         if data["isWeekend"]:
#             amount = 350
            
#         else:
#             amount = 600

#         embed = discord.Embed(title=f"{user.name} has voted!", description=f"""
# {user.mention if user in channel.guild.members else user.name} has just voted for **Stealth Bot** on top.gg!
# {amount}$ has been added to their balance.
#                               """ ,color=discord.Color.green())
        
#         if user.avatar:
#             embed.set_thumbnail(url=user.avatar)
            
#         if isinstance(user, discord.Member):
#             await user.send(f"""
# Thank you for voting on top.gg
# {amount}$ has been added to your balance.
# """)
            
#         await channel.send(embed=embed)

        
#         # await self.client.db.execute("INSERT INTO economy(user_id, amount) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET amount= $2", int(data["user"]), balance + amount)

    @commands.Cog.listener('on_command_error')
    async def error_handler(self, ctx: CustomContext, error):
        owners = [564890536947875868, 555818548291829792]

        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            if ctx.author.id in owners and self.client.no_prefix:
                return

            ignored_cogs = ('jishaku', 'events') if ctx.author.id != self.client.owner_id else ()
            command_names = []

            for command in [c for c in self.client.commands if c.cog_name not in ignored_cogs]:
                try:
                    if await command.can_run(ctx):
                        command_names.append([command.name] + command.aliases)

                except:
                    continue

            command_names = list(itertools.chain.from_iterable(command_names))

            matches = difflib.get_close_matches(ctx.invoked_with, command_names)

            if matches:
                confirm = await ctx.confirm(
                    message=f"I couldn't find a command called `{ctx.invoked_with}`.\nDid you mean `{f'{matches[0]}' if matches else ''}`?",
                    delete_after_confirm=True, delete_after_timeout=True, delete_after_cancel=True,
                    buttons=(('<:greenTick:895688440690147370>', f'', discord.ButtonStyle.gray),
                             ('🗑', None, discord.ButtonStyle.red)), timeout=15)

                if confirm is True:
                    message = copy.copy(ctx.message)
                    message._edited_timestamp = discord.utils.utcnow()
                    message.content = message.content.replace(ctx.invoked_with, matches[0])
                    return await self.client.process_commands(message)

                else:
                    return

            else:
                return await ctx.send(
                    f"I couldn't find a command called `{ctx.invoked_with}`.\nDo `help` to view a list of available "
                    f"commands.")
                
        ##### MUSIC ERRORS ####
        
        elif isinstance(error, errors.NoPlayer):
            name = "Music error"
            icon_url = None
            message = f"There isn't an activate player in this server."
            
        elif isinstance(error, errors.FullVoiceChannel):
            name = "Music error"
            icon_url = None
            message = f"I can't join your VC because it's full."
            
        elif isinstance(error, errors.NotAuthorized):
            name = "Music error"
            icon_url = None
            message = f"You cannot perform this action."

        elif isinstance(error, errors.UnknownError):
            name = "Unexpected error"
            icon_url = None
            message = f"An unexpected error occurred."
            
        elif isinstance(error, errors.IncorrectChannelError):
            player = ctx.voice_client
            name = "Music error"
            icon_url = None
            message = f"You must be in {player.channel.mention} for this session."

        elif isinstance(error, errors.IncorrectTextChannelError):
            player = ctx.voice_client
            name = "Music error"
            icon_url = None
            message = f"You can only use commands in {player.text_channel.mention} for this session."

        elif isinstance(error, errors.AlreadyConnectedToChannel):
            player = ctx.voice_client
            name = "Music error"
            icon_url = None
            message = f"I'm already connected to {player.channel.mention}."
            
        elif isinstance(error, errors.NoVoiceChannel):
            name = "Music error"
            icon_url = None
            message = f"I'm not connected to any VC."

        elif isinstance(error, errors.QueueIsEmpty):
            name = "Music error"
            icon_url = None
            message = f"There are no songs in the queue."

        elif isinstance(error, errors.NoCurrentTrack):
            name = "Music error"
            icon_url = None
            message = f"There is no song currently playing."

        elif isinstance(error, errors.PlayerIsAlreadyPaused):
            name = "Music error"
            icon_url = None
            message = f"The current song is already paused."
            
        elif isinstance(error, errors.PlayerIsNotPaused):
            name = "Music error"
            icon_url = None
            message = f"The current song isn't paused"

        elif isinstance(error, errors.NoMoreTracks):
            name = "Music error"
            icon_url = None
            message = f"There are no more songs in the queue."

        elif isinstance(error, errors.InvalidTimeString):
            name = "Music error"
            icon_url = None
            message = f"The time string given is invalid."

        elif isinstance(error, errors.NoPerms):
            name = "Music error"
            icon_url = None
            message = f"I missing permissions to speak/connect to that voice channel."

        elif isinstance(error, errors.NoConnection):
            name = "Music error"
            icon_url = None
            message = f"You must be connected to a VC to use music commands."

        elif isinstance(error, errors.AfkChannel):
            name = "Music error"
            icon_url = None
            message = f"I can't play music in a AFK channel."

        elif isinstance(error, errors.InvalidTrack):
            name = "Music error"
            icon_url = None
            message = f"I can't perform actions on a song that is not in the queue."

        elif isinstance(error, errors.InvalidPosition):
            name = "Music error"
            icon_url = None
            message = f"I can't perform actions on a invalid position in the queue."

        elif isinstance(error, errors.InvalidVolume):
            name = "Music error"
            icon_url = None
            message = f"Please enter a volume between 1 and 125."

        elif isinstance(error, errors.InvalidSeek):
            name = "Music error"
            icon_url = None
            message = f"You can't seek with timestamps that are shorter/longer than the current song."

        elif isinstance(error, errors.InvalidPosition):
            name = "Music error"
            icon_url = None
            message = f"I can't perform actions on a invalid position in the queue."

        elif isinstance(error, errors.AlreadyVoted):
            name = "Music error"
            icon_url = None
            message = f"You can't vote twice!"

        elif isinstance(error, errors.NothingToShuffle):
            name = "Music error"
            icon_url = None
            message = f"There's nothing to shuffle."

        elif isinstance(error, errors.NoLyrics):
            name = "Music error"
            icon_url = None
            message = f"I couldn't find lyrics on that song."

        elif isinstance(error, errors.ActiveVote):
            name = "Music error"
            icon_url = None
            message = f"There is already an active vote."

        elif isinstance(error, errors.LoadFailed):
            name = "Music error"
            icon_url = None
            message = f"An unexpected error occurred while loading your song."

        elif isinstance(error, errors.NoMatches):
            name = "Music error"
            icon_url = None
            message = f"I couldn't find a song called that, please try again."

        elif isinstance(error, errors.InvalidInput):
            name = "Music error"
            icon_url = None
            message = f"Invalid input has been detected!"

        elif isinstance(error, errors.LoopDisabled):
            name = "Music error"
            icon_url = None
            message = f"The loop mode is already disabled."

        elif isinstance(error, errors.TrackFailed):
            name = "Music error"
            icon_url = None
            message = f"There was an error playing that song, skipping to next song."

        #### MUTE ROLE ERRORS ###

        elif isinstance(error, errors.MuteRoleNotFound):
            name = "Mute role error"
            icon_url = None
            message = f"This server doesn't have a mute-role.\nTo change that, use `{ctx.prefix}mute-role <role>`."

        elif isinstance(error, errors.MuteRoleAlreadyExists):
            name = "Mute role error"
            icon_url = None
            message = f"This server already has a mute-role.\nTo remove it, use `{ctx.prefix}mute-role remove`."

        #### NORMAL ERRORS ####

        elif isinstance(error, errors.Forbidden):
            name = "Forbidden"
            icon_url = None
            message = f"""
I don't have the permissions to do that.
This might be due to me missing permissions in the current channel or server.
This might also be a issue with role hierarchy, try moving my role to the top of the role list.
            """

        elif isinstance(error, errors.InvalidThread):
            name = "Invalid thread"
            icon_url = None
            message = f"I couldn't find that thread."

        elif isinstance(error, errors.AuthorBlacklisted):
            name = "Skill Issue"
            icon_url = None
            reason = await self.client.db.fetchval("SELECT reason FROM blacklist WHERE user_id = $1", ctx.author.id)
            message = f"It appears that you're blacklisted from this bot with the reason being: {reason}\n*If you think this is a mistake, contact Ender2K89* "

        elif isinstance(error, errors.BotMaintenance):
            name = "Maintenance"
            icon_url = None
            message = f"The bot is in maintenance mode meaning no commands work."

        elif isinstance(error, errors.NoBannedMembers):
            name = "No banned users"
            icon_url = None
            message = f"There's no banned users in this server."

        elif isinstance(error, helpers.NotSH):
            name = "Wrong server"
            icon_url = None
            message = f"You can only use this command in `Stealth Hangout`!\ndiscord.gg/ktkXwmD2kF"

        elif isinstance(error, helpers.NotSPvP):
            name = "Wrong server"
            icon_url = None
            message = f"You can only use this command in `SignalPvP`!\nhttps://discord.gg/afBDa2Kqc9"

        elif isinstance(error, errors.TooLongPrefix):
            name = "Prefix error"
            icon_url = None
            message = f"Prefixes can only be up to 50 characters!"

        elif isinstance(error, errors.TooManyPrefixes):
            name = "Prefix error"
            icon_url = None
            message = f"You can only have 20 prefixes!"

        elif isinstance(error, errors.EmptyTodoList):
            name = "Empty todo list"
            icon_url = None
            message = f"Your todo list is empty!"

        elif isinstance(error, errors.NoSpotifyStatus):
            name = "Spotify error"
            icon_url = None
            message = f"That member doesn't have a spotify status!"

        elif isinstance(error, errors.PrefixAlreadyExists):
            name = "Prefix error"
            icon_url = None
            message = f"That's already one of my prefixes!"

        elif isinstance(error, errors.PrefixDoesntExist):
            name = "Prefix error"
            icon_url = None
            message = f"That's not one of my prefixes!"

        elif isinstance(error, errors.KillYourself):
            name = "Go kys"
            icon_url = None
            message = f"I couldn't find that command. Did you mean...\nkill {ctx.author.mention}"

        elif isinstance(error, errors.CommandDoesntExist):
            name = "Unknown command"
            icon_url = None
            message = f"I couldn't find that category/command."

        elif isinstance(error, helpers.Blacklisted):
            name = "Skill issue"
            icon_url = None
            message = f"It appears that you're blacklisted from this bot.\nContact Ender2K89#9999 if you think this is a mistake."

        elif isinstance(error, errors.NotStartedEconomy):
            name = "Economy error"
            icon_url = None
            message = error

        elif isinstance(error, commands.CommandOnCooldown):
            name = "Cooldown"
            icon_url = None
            message = f"This command is on cooldown. Please try again after {round(error.retry_after, 1)} seconds."

        elif isinstance(error, discord.Forbidden):
            name = "Forbidden"
            icon_url = None
            message = f"""
I don't have the permissions to do that.
This might be due to me missing permissions in the current channel or server.
This might also be a issue with role hierarchy, try moving my role to the top of the role list.
            """

        elif isinstance(error, discord.HTTPException):
            name = "HTTP Exception"
            icon_url = None
            message = "An unexpected HTTP error occurred.\nPlease notify Ender2K89#9999 about this issue with a " \
                      "screenshot of what you're trying to do. "

        elif isinstance(error, commands.MissingPermissions):
            permissions1 = [(e.replace('_', ' ').replace('guild', 'server')).title() for e in
                            error.missing_permissions]
            permissions = ", ".join(permissions1[:-2] + [" and ".join(permissions1[-2:])])

            name = "Missing permissions"
            icon_url = None
            message = f"You're missing {permissions} permissions."

        elif isinstance(error, commands.BotMissingPermissions):
            permissions1 = [(e.replace('_', ' ').replace('guild', 'server')).title() for e in
                            error.missing_permissions]
            permissions = ", ".join(permissions1[:-2] + [" and ".join(permissions1[-2:])])

            name = "Missing permissions"
            icon_url = None
            message = f"I'm missing {permissions} permissions."

        elif isinstance(error, commands.NotOwner):
            name = "Not owner"
            icon_url = None
            message = "Only the owner of this bot can run this command."

        elif isinstance(error, commands.DisabledCommand):
            name = "Disabled command"
            icon_url = None
            message = "That command has been temporarily disabled by the owner."
            
        elif isinstance(error, commands.CheckAnyFailure):
            name = "Check failure"
            icon_url = None
            message = error

        elif isinstance(error, commands.TooManyArguments):
            name = "Too many arguments"
            icon_url = None
            message = "It appears that you've provided too many arguments, please try again with fewer arguments."

        elif isinstance(error, commands.BadLiteralArgument):
            literals = join_literals(error.param.annotation, return_list=True)
            literals = '"' + '", "'.join(literals[:-2] + ['" or "'.join(literals[-2:])]) + '"'

            name = "Bad literal argument"
            icon_url = None
            message = f"Sorry but the argument `{error.param.name}` isn't one of the following: {literals}"

        elif isinstance(error, commands.BadArgument):
            name = "Bad argument"
            icon_url = None
            message = f"The argument you provided was invalid."

        elif isinstance(error, commands.BadUnionArgument):
            name = "Bad union argument"
            icon_url = None
            message = f"You didn't provide a valid {conv_n(error.converters)}."

        elif isinstance(error, commands.MemberNotFound):
            name = "Unknown member"
            icon_url = None
            message = "I couldn't find that member."

        elif isinstance(error, commands.MessageNotFound):
            name = "Unknown message"
            icon_url = None
            message = "I couldn't find that message."

        elif isinstance(error, commands.GuildNotFound):
            name = "Unknown guild"
            icon_url = None
            message = "I couldn't find that guild."

        elif isinstance(error, commands.ChannelNotFound):
            name = "Unknown channel"
            icon_url = None
            message = "I couldn't find that channel."

        elif isinstance(error, commands.UserNotFound):
            name = "Unknown user"
            icon_url = None
            message = "I couldn't find that user."

        elif isinstance(error, commands.EmojiNotFound):
            name = "Unknown emoji"
            icon_url = None
            message = "I couldn't find that emoji.\nThis might be cause I'm not in the server that emoji is from."

        elif isinstance(error, commands.ChannelNotReadable):
            name = "Unreadable channel"
            icon_url = None
            message = "I cannot read that channel."

        elif isinstance(error, commands.NSFWChannelRequired):
            name = "Invalid channel"
            icon_url = None
            message = "This command can only be used in a NSFW channel."

            embed = discord.Embed(title=message, color=0x2F3136)
            embed.set_image(url='https://i.imgur.com/oe4iK5i.gif')

            return await ctx.send(embed=embed)

        elif isinstance(error, discord.ext.commands.MissingRequiredArgument):
            missing = f"{error.param.name}"
            command = f"{ctx.clean_prefix}{ctx.command} {ctx.command.signature}"
            separator = (' ' * (len([item[::-1] for item in command[::-1].split(missing[::-1], 1)][::-1][0]) - 1))
            indicator = ('^' * (len(missing) + 2))
            name = "Command error"
            icon_url = None
            message = f"```\n{command}\n{separator}{indicator}\n{missing} is a required argument that is missing.\n```"

        elif isinstance(error, commands.RoleNotFound):
            name = "Unknown role"
            icon_url = None
            message = "I couldn't find that role."

        elif isinstance(error, commands.MissingRole):
            name = "Missing role"
            icon_url = None
            message = "You're missing a role that's required to run this command."

        elif isinstance(error, commands.ExtensionFailed):
            name = "Extension error"
            icon_url = None
            message = "That extension failed."

        elif isinstance(error, commands.ExtensionAlreadyLoaded):
            name = "Extension error"
            icon_url = None
            message = "That extension is already loaded."

        elif isinstance(error, commands.ExtensionNotFound):
            name = "Extension error"
            icon_url = None
            message = "I couldn't find that extension."

        elif isinstance(error, IndexError):
            name = "Python error"
            icon_url = None
            message = error

        elif isinstance(error, KeyError):
            name = "Python error"
            icon_url = None
            message = error

        else:
            name = None
            icon_url = None
            message = None

            channel = self.client.get_channel(914145662520659998)

            traceback_string = "".join(traceback.format_exception(etype=None, value=error, tb=error.__traceback__))

            embed = discord.Embed(description=f"An unexpected error occurred. The developers have been notified about this and will fix it ASAP.")
            embed.set_author(name="Unexpected error occurred", icon_url='https://i.imgur.com/9gQ6A5Y.png')

            await ctx.send(embed=embed)

            channel = self.client.get_channel(914145662520659998)

            data = f"""
Author: {ctx.author} ({ctx.author.id})
Channel: {ctx.channel} ({ctx.channel.id})
Guild: {ctx.guild} ({ctx.guild.id})
Owner: {ctx.guild.owner} ({ctx.guild.owner.id})

Bot admin?: {ctx.me.guild_permissions.administrator}
Role position: {ctx.me.top_role.position}

Message: {ctx.message}"""

            send = f"""
```yaml
{data}
```
```py
Command {ctx.command} raised the following error:
{traceback_string}
```"""

            try:
                if len(send) < 2000:
                    await channel.send(send, view=PersistentExceptionView(ctx.bot))

                else:
                    await channel.send(f"""
```yaml
{data}
```
```py
Command {ctx.command} raised the following error:
```
                            """, file=discord.File(io.StringIO(traceback_string), filename="traceback.py"),
                                view=PersistentExceptionView(ctx.bot))

            finally:
                print(f"{ctx.command} raised an unexpected error")

            return

        embed = discord.Embed(description=message)
        icon_urlL = icon_url or 'https://i.imgur.com/9gQ6A5Y.png'
        nameL = name or 'Error occurred'
        embed.set_author(name=nameL, icon_url=icon_urlL)

        await ctx.send(embed=embed)
        
    @commands.Cog.listener('on_message')
    async def chatbot(self, message: discord.Message):
        if message.author.bot:
            return
        
        if not message.guild:
            return
        
        if message.channel.id in self.client.chatbot_channels:
            response = await self.client.rs.get_ai_response(discord.utils.remove_markdown(message.content))
            
            await message.reply(response[0]['message'] or 'No response...')
            
    @commands.Cog.listener()
    async def on_command(self, ctx: CustomContext):
        if ctx.guild.id in self.client.disable_commands_guilds:
            try:
                if self.client.disable_commands_guilds[ctx.guild.id] is True:
                    return
                
            except KeyError:
                pass
        
        await self.client.db.execute("INSERT INTO commands (guild_id, user_id, command, timestamp) VALUES ($1, $2, $3, $4)",
                                  getattr(ctx.guild, 'id', None), ctx.author.id, ctx.command.qualified_name, ctx.message.created_at)

        colors = [0x910023, 0xA523FF]
        color = random.choice(colors)

        embed = discord.Embed(title=f"{ctx.command} has been used",
                              description=f"""
__**Guild info**__

Name: `{ctx.guild}`
ID: `{ctx.guild.id}`

Channel Name: `{ctx.channel}`
Channel ID: `{ctx.channel.id}`
Channel Mention: {ctx.channel.mention}

Owner Name: `{ctx.guild.owner}`
Owner ID: `{ctx.guild.owner.id}`
Owner Mention: {ctx.guild.owner.mention}
Owner Tag: `#{ctx.guild.owner.discriminator}`

__**Author info**__

Name: `{ctx.author}`
ID: `{ctx.author.id}`
Mention: {ctx.author.mention}
Tag: `#{ctx.author.discriminator}`

__**Message info**__
URL: [Click here]({ctx.message.jump_url}/ 'Jump URL')
Content:
`{ctx.message.content}`
                              """,
                              timestamp=discord.utils.utcnow(),
                              color=color)

        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(yaml_data['ON_COMMAND_WEBHOOK_URL'], session=session)
            await webhook.send(embed=embed)

    @commands.Cog.listener('on_message')
    async def update_messages_seen_count(self, message: discord.Message):
        self.client.messages_count = self.client.messages_count + 1

    @commands.Cog.listener('on_message')
    async def on_owner_forgor(self, message: discord.Message):
        if not message.guild:
            return

        if message.author.bot:
            return

        if message.author.id == 564890536947875868 and "forgor" in message.content.lower():
            return await message.add_reaction("💀")

    @commands.Cog.listener('on_message')
    async def on_mention_spam(self, message: discord.Message):
        if not message.guild:
            return

        if message.author.bot:
            return

        if message.guild.id == 799330949686231050 and len(message.mentions) > 3:
            await message.delete()
            await message.channel.send(
                f"Hey {message.author.mention}, don't spam mentions! Next time this will result in a ban.")
            
    @commands.Cog.listener('on_message')
    async def on_suggestion(self, message: discord.Message):
        if message.author.bot:
            return
        
        if not message.guild:
            return
        
        if message.channel.id == 910948507681165405 or message.channel.id == 916654281489256459:
            await message.add_reaction("<:upvote:893588750242832424>")
            return await message.add_reaction("<:downvote:895688440543342624>")

    @commands.Cog.listener('on_message')
    async def send_emote(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return

        if message.author.id == 555818548291829792:
            character = "\u200b"
            content = message.content
            emojis = re.findall(r';(?P<name>[a-zA-Z0-9]{1,32}?);', message.content)

            for em_name in emojis:
                emoji = discord.utils.find(lambda em: em.name.lower() == em_name.lower(), self.client.emojis)

                if not emoji or not emoji.is_usable():
                    emoji = None

                content = content.replace(f';{em_name};', f'{str(emoji or f";{character}{em_name}{character};")}', 1)

            if content.replace(character, '') != message.content:
                await message.channel.send(content)

        else:
            return

    @commands.Cog.listener('on_message')
    async def on_afk_user_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        if not message.guild:
            return

        if message.author.id in self.client.afk_users:
            try:
                if self.client.auto_un_afk[message.author.id] is False:
                    return
            except KeyError:
                pass

            self.client.afk_users.pop(message.author.id)

            info = await self.client.db.fetchrow("SELECT * FROM afk WHERE user_id = $1", message.author.id)
            await self.client.db.execute("INSERT INTO afk (user_id, start_time, reason) VALUES ($1, null, null) "
                                         "ON CONFLICT (user_id) DO UPDATE SET start_time = null, reason = null",
                                         message.author.id)

            colors = [0x910023, 0xA523FF]
            color = random.choice(colors)

            time = info["start_time"]

            delta_uptime = message.created_at - time
            hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            days, hours = divmod(hours, 24)

            embed = discord.Embed(title=f"👋 Welcome back {message.author.name}!", description=f"""
You've been AFK for {self.time(days=days, hours=hours, minutes=minutes, seconds=seconds)}
With the reason being: {info['reason']}
                                """, timestamp=discord.utils.utcnow(), color=color)

            await message.channel.send(embed=embed, delete_after=35)

            await message.add_reaction("👋")

    @commands.Cog.listener('on_message')
    async def on_afk_user_mention(self, message: discord.Message):
        if not message.guild:
            return

        if message.author == self.client.user:
            return

        if message.mentions:
            pinged_afk_user_ids = list(set([u.id for u in message.mentions]).intersection(self.client.afk_users))
            afkUsers = []
            for user_id in pinged_afk_user_ids:
                member = message.guild.get_member(user_id)
                if member and member.id != message.author.id:
                    info = await self.client.db.fetchrow("SELECT * FROM afk WHERE user_id = $1", user_id)

                    time = info["start_time"]

                    delta_uptime = message.created_at - time
                    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    days, hours = divmod(hours, 24)

                    afkUsers.append(
                        f"Hey {message.author.mention}, it looks like {member.mention} has been AFK for {helpers.human_timedelta(info['start_time'])}.\nWith the reason being: {info['reason']}\n")

            if afkUsers:
                afkUsers = "\n".join(afkUsers)
                await message.reply(f"{afkUsers}", delete_after=35)

            else:
                return

    # @commands.Cog.listener('on_member_join')
    # async def add_previously_muted_members(self, member: discord.Member):
    #     if not await self.client.db.fetchval("SELECT user_id FROM muted WHERE user_id = $1 AND guild_id = $2", member.id, member.guild.id):
    #         return
    #
    #     await self.client.db.execute("DELETE FROM muted WHERE user_id = $1 AND guild_id = $2", member.id, member.guild.id)
    #
    #     if not (role := await self.client.db.fetchval("SELECT muted_role_id FROM guilds WHERE guild_id = $1", member.guild.id)):
    #         return
    #
    #     if not (role := member.guild.get_role(role)):
    #         return
    #
    #     if role >= member.guild.me.top_role:
    #         return
    #
    #     await member.add_roles(role, reason="Member was previous muted.")
    #
    # @commands.Cog.listener('on_member_remove')
    # async def remove_previously_muted_members(self, member: discord.Member):
    #     if not (role := await self.client.db.fetchval("SELECT muted_role_id FROM guilds WHERE guild_id = $1", member.guild.id)):
    #         return
    #
    #     if not (role := member.guild.get_role(role)):
    #         return
    #
    #     if role in member.roles:
    #         await self.client.db.execute("INSERT INTO muted (user_id, guild_id) VALUES ($1, $2) ON CONFLICT (user_id, guild_id) DO NOTHING", member.id, member.guild.id)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        self.client.edited_messages_count = self.client.edited_messages_count + 1

        if self.client.edited_messages.get(before.guild.id) is None:
            self.client.edited_messages[before.guild.id] = {}

        self.client.edited_messages[before.guild.id]["before"] = before
        self.client.edited_messages[before.guild.id]["before_content"] = before.content
        self.client.edited_messages[before.guild.id]["before_author"] = before.author

        self.client.edited_messages[before.guild.id]["after"] = after
        self.client.edited_messages[before.guild.id]["after_content"] = after.content
        self.client.edited_messages[before.guild.id]["after_author"] = after.author

        await self.client.process_commands(after)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.guild:
            return

        if message.guild.id == 799330949686231050 and message.channel.category_id in [799406595838312498, 799640351996510229, 800030353527799848]:
            if not message.author.bot:
                if message.mentions:
                    users = []
                    for user in message.mentions:
                        if user.id == message.author.id:
                            continue

                        user = message.guild.get_member(user.id)
                        users.append(user.mention)

                    if users:
                        embed = discord.Embed(title="<a:alert:854743318033072158> Ghost ping detector <a:alert:854743318033072158>", description=f"""
{message.author.mention} just deleted a message that pinged {', '.join(users)}!
                                """, color=discord.Color.red())

                        return await message.channel.send(message.author.mention, embed=embed, allowed_mentions=discord.AllowedMentions(users=True))

            else:
                return

        if self.client.messages.get(message.guild.id) is None:
            self.client.messages[message.guild.id] = {}

        self.client.messages[message.guild.id]["message"] = message
        self.client.messages[message.guild.id]["content"] = message.content
        self.client.messages[message.guild.id]["author"] = message.author
        self.client.messages[message.guild.id]["time_deleted"] = message.created_at

        if message.embeds:
            self.client.messages[message.guild.id]["embed"] = message.embeds[0]

        elif not message.embeds:
            self.client.messages[message.guild.id]["embed"] = ""

    @commands.Cog.listener("on_guild_join")
    async def thank_for_adding_bot(self, guild: discord.Guild):
        channel = discord.utils.get(guild.text_channels, name='general')

        if not channel:
            channels = [channel for channel in guild.text_channels if channel.permissions_for(guild.me).send_messages]
            channel = channels[0]

        welcomeEmbed = discord.Embed(title="Thank you for adding `Stealth Bot` to your server", description="""
We really appreciate you adding `Stealth Bot` to your server.
You can do `sb!help` to view a list of commands.
To add a prefix simply do `sb!prefix add <prefix>`.
                        """, timestamp=discord.utils.utcnow(), color=0x2F3136)
        welcomeEmbed.set_thumbnail(url=self.client.user.avatar.url)

        await channel.send(embed=welcomeEmbed)

    @commands.Cog.listener("on_guild_join")
    async def private_log_on_guild_join(self, guild: discord.Guild):
        await self.client.db.execute("DELETE FROM guilds WHERE guild_id = $1", guild.id)

        embed = discord.Embed(title="New guild!", description=f"""
**Guild name:** {guild.name}
**Guild owner:** {guild.owner}
**Guild ID:** {guild.id}

{len(guild.members):,} members ({len([m for m in guild.members if m.bot]):,} bots {len([m for m in guild.members if not m.bot]):,} humans)
{len(guild.text_channels):,} text channels
{len(guild.voice_channels):,} voice channels
                            """, color=discord.Color.green())
        embed.set_footer(text=f"I am now in {len(self.client.guilds)} guilds", icon_url=self.client.user.avatar.url)

        if guild.icon:
            embed.set_thumbnail(url=f"{guild.icon}")

        channel = self.client.get_channel(914145032406196245)
        await channel.send(embed=embed)
        
        
        if len([m for m in guild.members if m.bot]) > 48:
            embed = discord.Embed(title="Possible bot farm!", description=f"""
{guild.name} ({guild.id}) could be a bot farm!

{len(guild.members):,} members
{len([m for m in guild.members if m.bot]):,} bots
{len([m for m in guild.members if not m.bot]):,} humans
                                """, color=discord.Color.red())
            
            if guild.icon:
                embed.set_thumbnail(url=f"{guild.icon}")

            await channel.send(embed=embed)

    @commands.Cog.listener("on_guild_remove")
    async def private_log_on_guild_remove(self, guild: discord.Guild):
        await self.client.db.execute("DELETE FROM guilds WHERE guild_id = $1", guild.id)

        embed = discord.Embed(title="Left guild!", description=f"""
**Guild name:** {guild.name}
**Guild owner:** {guild.owner}
**Guild ID:** {guild.id}

{len(guild.members):,} members ({len([m for m in guild.members if m.bot]):,} bots {len([m for m in guild.members if not m.bot]):,} humans)
{len(guild.text_channels):,} text channels
{len(guild.voice_channels):,} voice channels
                            """, color=discord.Color.red())
        embed.set_footer(text=f"I am now in {len(self.client.guilds)} guilds", icon_url=self.client.user.avatar.url)

        if guild.icon:
            embed.set_thumbnail(url=f"{guild.icon}")

        channel = self.client.get_channel(914145032406196245)
        await channel.send(embed=embed)