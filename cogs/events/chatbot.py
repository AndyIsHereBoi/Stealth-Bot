import urllib
import discord
import unidecode

from ._base import EventsBase
from discord.ext import commands

class Chatbot(EventsBase):

    @commands.Cog.listener('on_message')
    async def chatbot(self, message: discord.Message):
        if message.author.bot:
            return

        if not message.guild:
            return

        if message.channel.id in self.bot.chatbot_channels:
            text = unidecode.unidecode(discord.utils.remove_markdown(urllib.parse.quote(message.content)))
            request = await self.bot.session.get(
                f"https://api.popcat.xyz/chatbot?msg={text}&owner=Ender2K89&botname=Stealth+Bot")
            json = await request.json()

            try:
                await message.reply(json['response'])

            except:
                await message.add_reaction('❌')
                await message.reply(json['error']['message'])