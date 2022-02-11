import discord

from ._base import EventsBase
from discord.ext import commands

class Bot(EventsBase):

    @commands.Cog.listener('on_message')
    async def update_messages_seen_count(self, message: discord.Message):
        self.bot.messages_count =+ 1