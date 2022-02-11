import time
import discord

from ._base import FunBase
from discord.ext import commands
from helpers.context import CustomContext

class Reddit(FunBase):
    
    async def reddit(self, ctx: CustomContext, reddit: str, hot: bool):
        start = time.perf_counter()
        request = await self.bot.session.get(f"https://meme-api.herokuapp.com/gimme/{reddit}?hot={hot}")
        json = await request.json()

        try:
            if json['code']:
                return await ctx.send("Invalid sub-reddit!")

        except:
            if ctx.channel.is_nsfw() is False and json['nsfw'] is True:
                return await ctx.send("NSFW sub-reddit! Please use this command again is a NSFW channel.")

            end = time.perf_counter()
            ms = (end - start) * 1000

            embed = discord.Embed(title=json['title'])
            embed.set_image(url=json['url'] or discord.Embed.Empty)
            embed.set_footer(text=f"Requested by {ctx.author} • {reddit} • {round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

            return await ctx.send(embed=embed, footer=False)

    @commands.command(
        help=":frog: Sends a random meme from Reddit.")
    async def meme(self, ctx: CustomContext):
        await self.reddit(ctx, "dankmemes", True)

    @commands.command(
        help=":frog: Sends a random programmer meme from Reddit.",
        aliases=['programmer_meme', 'programmerhumor', 'programmer_humor', 'programmerhumour', 'programmer_humour',
                 'pm'])
    async def programmermeme(self, ctx: CustomContext):
        await self.reddit(ctx, "programmerhumor", True)

    @commands.command(
        help=":frog: Sends a random bad discord bot from Reddit.",
        aliases=['bdb', 'bad_discord_bots', 'baddiscordbot', 'bad_discord_bot'])
    async def baddiscrodbots(self, ctx: CustomContext):
        await self.reddit(ctx, "baddiscordbots", True)

    @commands.command(
        name="reddit",
        help=":frog: Sends a random post from the specified subreddit.")
    async def _reddit(self, ctx: CustomContext, reddit: str):
        await self.reddit(ctx, reddit, True)