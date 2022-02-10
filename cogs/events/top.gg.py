import discord

from ._base import EventsBase
from discord.ext import commands

class Topgg(EventsBase):

    @commands.Cog.listener()
    async def on_autopost_success(self):
        channel = self.bot.get_channel(896775088249122889)

        embed = discord.Embed(title="Successfully posted to top.gg!")
        await channel.send(embed=embed)