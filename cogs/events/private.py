import re
import discord

from ._base import EventsBase
from discord.ext import commands

class Private(EventsBase):

    @commands.Cog.listener('on_message')
    async def on_owner_forgor(self, message: discord.Message):
        """ Event to detect if the bot owner said 'forgor' in a message and react with 💀 to it. """

        if message.author.id == 564890536947875868 and "forgor" in message.content.lower():
            return await message.add_reaction("💀")

    @commands.Cog.listener('on_message')
    async def send_emote(self, message: discord.Message):
        """ Event to use nitro emotes for free cause some of my friends don't have nitro. """

        if not message.guild:
            return

        if message.author.id != 555818548291829792:
            return

        character = "\u200b"
        content = message.content
        emojis = re.findall(r';(?P<name>[a-zA-Z0-9]{1,32}?);', message.content)

        for em_name in emojis:
            emoji = discord.utils.find(lambda em: em.name.lower() == em_name.lower(), self.bot.emojis)

            if not emoji or not emoji.is_usable():
                emoji = None

            content = content.replace(f';{em_name};', f'{str(emoji or f";{character}{em_name}{character};")}', 1)

        if content.replace(character, '') != message.content:
            await message.channel.send(content)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """ Ghost ping detector for my servers. """

        if not message.guild or message.author.bot:
            return

        if message.guild.id in self.moderation_guilds:
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

    @commands.Cog.listener('on_message')
    async def on_mention_spam(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return

        if message.guild.id == 799330949686231050 and len(message.mentions) > 3:
            await message.delete()
            await message.channel.send(
                f"Hey {message.author.mention}, don't spam mentions!")