import random
import discord

from ._base import UtilityBase
from discord.ext import commands, menus
from helpers.context import CustomContext
from discord.ext.menus.views import ViewMenuPages

class ServerEmotesEmbedPage(menus.ListPageSource):
    def __init__(self, data, guild):
        self.data = data
        self.guild = guild
        super().__init__(data, per_page=10)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        colors = [0x910023, 0xA523FF]
        color = random.choice(colors)

        embed = discord.Embed(title=f"{self.guild}'s emotes ({len(self.guild.emojis):,})",
                              description="\n".join(f'{i + 1}. {v}' for i, v in enumerate(entries, start=offset)),
                              timestamp=discord.utils.utcnow(), color=color)
        return embed


class ServerMembersEmbedPage(menus.ListPageSource):
    def __init__(self, data, guild):
        self.data = data
        self.guild = guild
        super().__init__(data, per_page=20)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        colors = [0x910023, 0xA523FF]
        color = random.choice(colors)
        embed = discord.Embed(title=f"{self.guild}'s members ({self.guild.member_count:,})",
                              description="\n".join(f'{i + 1}. {v}' for i, v in enumerate(entries, start=offset)),
                              timestamp=discord.utils.utcnow(), color=color)
        return embed

class _List(UtilityBase):

    @commands.command(
        help="Shows you a list of emotes from the specified server. If no server is specified it will default to the current one.",
        aliases=['emojilist', 'emote_list', 'emoji_list', 'emotes', 'emojis'],
        brief="emotelist\nemotelist 799330949686231050")
    async def emotelist(self, ctx: CustomContext, guildID: int = None):
        if guildID:
            guild = self.bot.get_guild(guildID)
            if not guild:
                return await ctx.send("I couldn't find that server. Make sure the ID you entered was correct.")
        else:
            guild = ctx.guild

        guildEmotes = guild.emojis
        emotes = []

        for emoji in guildEmotes:

            if emoji.animated:
                emotes.append(f"<a:{emoji.name}:{emoji.id}> **|** {emoji.name} **|** [`<a:{emoji.name}:{emoji.id}>`]({emoji.url})")

            if not emoji.animated:
                emotes.append(f"<:{emoji.name}:{emoji.id}> **|** {emoji.name} **|** [`<:{emoji.name}:{emoji.id}>`]({emoji.url})")

        paginator = ViewMenuPages(source=ServerEmotesEmbedPage(emotes, guild), clear_reactions_after=True)
        page = await paginator._source.get_page(0)
        kwargs = await paginator._get_kwargs_from_page(page)

        if paginator.build_view():
            paginator.message = await ctx.send(embed=kwargs['embed'], view=paginator.build_view())

        else:
            paginator.message = await ctx.send(embed=kwargs['embed'])

        await paginator.start(ctx)

    @commands.command(
        help="Shows you a list of members from the specified server. If no server is specified it will default to the current one.",
        aliases=['member_list', 'memlist', 'mem_list', 'members'],
        brief="memberlist\nmemberlist 799330949686231050")
    async def memberlist(self, ctx: CustomContext, guildID: int = None):
        if guildID:
            guild = self.bot.get_guild(guildID)
            if not guild:
                return await ctx.send("I couldn't find that server. Make sure the ID you entered was correct.")
        else:
            guild = ctx.guild

        guildMembers = guild.members
        members = []

        for member in guildMembers:
            members.append(f"{member.name} **|** {member.mention} **|** `{member.id}`")

        paginator = ViewMenuPages(source=ServerMembersEmbedPage(members, guild), clear_reactions_after=True)
        page = await paginator._source.get_page(0)
        kwargs = await paginator._get_kwargs_from_page(page)
        if paginator.build_view():
            paginator.message = await ctx.send(embed=kwargs['embed'], view=paginator.build_view())
        else:
            paginator.message = await ctx.send(embed=kwargs['embed'])
        await paginator.start(ctx)