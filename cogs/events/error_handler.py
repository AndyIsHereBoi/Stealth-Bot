import io
import copy
import errors
import typing
import inspect
import difflib
import discord
import itertools
import traceback

from helpers import helpers
from ._base import EventsBase
from discord.ext import commands
from helpers.context import CustomContext
from helpers.paginator import PersistentExceptionView

def join_literals(annotation: inspect.Parameter.annotation, return_list: bool = False):
    if typing.get_origin(annotation) is typing.Literal:
        arguments = annotation.__args__

        if return_list is False:
            return '[' + '|'.join(arguments) + ']'

        else:
            return list(arguments)

    return None


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


class ErrorHandler(EventsBase):

    @commands.Cog.listener('on_command_error')
    async def error_handler(self, ctx: CustomContext, error):
        owners = [564890536947875868, 555818548291829792]

        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            if ctx.author.id in owners and self.bot.no_prefix:
                return

            ignored_cogs = ('jishaku', 'events') if ctx.author.id != self.bot.owner_id else ()
            command_names = []

            for command in [c for c in self.bot.commands if c.cog_name not in ignored_cogs]:
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
                    return await self.bot.process_commands(message)

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
            reason = await self.bot.db.fetchval("SELECT reason FROM blacklist WHERE user_id = $1", ctx.author.id)
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
            message = error or f"That argument was invalid."

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

            channel = self.bot.get_channel(914145662520659998)

            traceback_string = "".join(traceback.format_exception(etype=None, value=error, tb=error.__traceback__))

            embed = discord.Embed(
                description=f"An unexpected error occurred. The developers have been notified about this and will fix it ASAP.")
            embed.set_author(name="Unexpected error occurred", icon_url='https://i.imgur.com/9gQ6A5Y.png')

            await ctx.send(embed=embed)

            channel = self.bot.get_channel(914145662520659998)

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

    @commands.Cog.listener()
    async def on_command(self, ctx: CustomContext):
        if ctx.guild.id in self.bot.disable_commands_guilds:
            try:
                if self.bot.disable_commands_guilds[ctx.guild.id] is True:
                    return

            except KeyError:
                pass

        await self.bot.db.execute(
            "INSERT INTO commands (guild_id, user_id, command, timestamp) VALUES ($1, $2, $3, $4)",
            getattr(ctx.guild, 'id', None), ctx.author.id, ctx.command.qualified_name, ctx.message.created_at)