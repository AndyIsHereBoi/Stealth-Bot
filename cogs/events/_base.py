import io
import re
import discord
import traceback

from discord.ext import commands
from helpers.paginator import PersistentExceptionView

class EventsBase(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.moderation_guilds = [799330949686231050, 879050715660697622, 925067864241754132]

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


        data = f"""Author: {ctx.author} ({ctx.author.id})
                Channel: {ctx.channel} ({ctx.channel.id})
                Guild: {ctx.guild} ({ctx.guild.id})
                Owner: {ctx.guild.owner} ({ctx.guild.owner.id})
                
                Bot admin?: {ctx.me.guild_permissions.administrator}
                Role position: {ctx.me.top_role.position}
                
                Message: {ctx.message.content}"""

        send = f"```yaml\n{data}\n```\n```py\nCommand {ctx.command} raised the following error:\n{traceback_string}\n```"

        try:
            if len(send) < 2000:
                await channel.send(send, view=PersistentExceptionView(ctx.bot))

            else:
                await channel.send(f"```yaml\n{data}\n```\n```py\nCommand {ctx.command} raised the following error:\n```", file=discord.File(io.StringIO(traceback_string), filename="traceback.py"), view=PersistentExceptionView(ctx.bot))

        finally:
            print(f"{ctx.command} raised an unexpected error")