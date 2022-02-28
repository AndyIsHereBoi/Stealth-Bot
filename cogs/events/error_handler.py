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

class Buttons(discord.ui.View):
    def __init__(self, traceback_, timeout=180):
        self.traceback = traceback_
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Traceback", emoji=None, style=discord.ButtonStyle.blurple)
    async def view_traceback(self, button: discord.ui.Button, interaction: discord.Interaction):
        return await interaction.response.send_message(f"Read the last line for proper info.\n```py\n{self.traceback}\n```", ephemeral=True)

    @discord.ui.button(label="Delete", emoji=None, style=discord.ButtonStyle.blurple)
    async def delete_message(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.message.delete()
        return await interaction.response.send_message("Message deleted.", ephemeral=True)


class ErrorHandler(EventsBase):

    @commands.Cog.listener('on_command_error')
    async def error_handler(self, ctx: CustomContext, error):
        owners = [564890536947875868, 555818548291829792]

        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            pass

        elif isinstance(error, errors.MuteRoleNotFound):
            pass

        elif isinstance(error, errors.MuteRoleAlreadyExists):
            pass

        elif isinstance(error, errors.Forbidden):
            pass

        elif isinstance(error, errors.InvalidThread):
            pass

        elif isinstance(error, errors.AuthorBlacklisted):
            pass

        elif isinstance(error, errors.BotMaintenance):
            pass

        elif isinstance(error, errors.NoBannedMembers):
            pass

        elif isinstance(error, helpers.NotSH):
            pass

        elif isinstance(error, helpers.NotSPvP):
            pass

        elif isinstance(error, errors.TooLongPrefix):
            pass

        elif isinstance(error, errors.TooManyPrefixes):
            pass

        elif isinstance(error, errors.EmptyTodoList):
            pass

        elif isinstance(error, errors.NoSpotifyStatus):
            pass

        elif isinstance(error, errors.PrefixAlreadyExists):
            pass

        elif isinstance(error, errors.PrefixDoesntExist):
            pass

        elif isinstance(error, errors.CommandDoesntExist):
            pass

        elif isinstance(error, commands.CommandOnCooldown):
            pass

        elif isinstance(error, discord.Forbidden):
            pass

        elif isinstance(error, discord.HTTPException):
            pass

        elif isinstance(error, commands.MissingPermissions):
            pass

        elif isinstance(error, commands.BotMissingPermissions):
            pass

        elif isinstance(error, commands.NotOwner):
            pass

        elif isinstance(error, commands.DisabledCommand):
            pass

        elif isinstance(error, commands.CheckAnyFailure):
            pass

        elif isinstance(error, commands.TooManyArguments):
            pass

        elif isinstance(error, commands.BadLiteralArgument):
            pass

        elif isinstance(error, commands.BadArgument):
            pass

        elif isinstance(error, commands.BadUnionArgument):
            pass

        elif isinstance(error, commands.MemberNotFound):
            pass

        elif isinstance(error, commands.MessageNotFound):
            pass

        elif isinstance(error, commands.GuildNotFound):
            pass

        elif isinstance(error, commands.ChannelNotFound):
            pass

        elif isinstance(error, commands.UserNotFound):
            pass

        elif isinstance(error, commands.EmojiNotFound):
            pass

        elif isinstance(error, commands.ChannelNotReadable):
            pass

        elif isinstance(error, commands.NSFWChannelRequired):
            pass

        elif isinstance(error, discord.ext.commands.MissingRequiredArgument):
            pass

        elif isinstance(error, commands.RoleNotFound):
            pass

        elif isinstance(error, commands.MissingRole):
            pass

        elif isinstance(error, commands.ExtensionFailed):
            pass

        elif isinstance(error, commands.ExtensionAlreadyLoaded):
            pass

        elif isinstance(error, commands.ExtensionNotFound):
            pass

        elif isinstance(error, IndexError):
            pass

        elif isinstance(error, KeyError):
            pass

        else:
            # unknown error
            embed = discord.Embed(title=f"<:error:888779034408927242> Command {ctx.command.name} raised an **unknown** error")
            embed = discord.Embed( description=f"An unexpected error occurred.\nThe developers have been notified about this and will fix it ASAP.")

            await ctx.send(embed=embed, footer=False, view=Buttons("".join(traceback.format_exception(etype=None, value=error, tb=error.__traceback__)), 180))
            return await self.send_unexpected_error(ctx, error)


        # known error
        embed = discord.Embed(title=f"<:error:888779034408927242> {f'Command {ctx.command.name} raised an error' if ctx.command else 'Error'} ", description=f"""
```prolog
{error}
```
        """)

        return await ctx.send(embed=embed, footer=False, view=Buttons("".join(traceback.format_exception(etype=None, value=error, tb=error.__traceback__)), 180))

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