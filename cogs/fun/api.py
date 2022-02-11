import urllib
import discord

from ._base import FunBase
from discord.ext import commands
from helpers.context import CustomContext
from discord.ext.commands import BucketType

class API(FunBase):

    @commands.command(
        help="<:minecraft:895688440614649919> Let's you customize a minecraft achievement!",
        aliases=['minecraft_achievement', 'mc_achievement'])
    @commands.cooldown(1, 5, BucketType.user)
    async def achievement(self, ctx: CustomContext, *, text):
        text = urllib.parse.quote(text)

        async with self.bot.session.get(f"https://api.cool-img-api.ml/achievement?text={text}",
                                           allow_redirects=True) as request:
            embed = discord.Embed()
            embed.set_image(url=request.url)

            await ctx.send(embed=embed)

    @commands.command(
        help="Sends a random shower thought!",
        aliases=['shower_thought', 'shower', 'shower-thought'])
    @commands.cooldown(1, 5, BucketType.user)
    async def showerthought(self, ctx: CustomContext):
        request = await self.bot.session.get("https://api.popcat.xyz/showerthoughts")
        json = await request.json()

        try:
            embed = discord.Embed(title=f"{json['author']}:", description=json['result'])
            embed.set_footer(text=f"{json['upvotes']} upvotes • Requested by {ctx.author.display_name}")

            return await ctx.send(embed=embed, footer=False)

        except:
            return await ctx.send("Rate limited!")

    @commands.command(
        help="Sends a random roast")
    @commands.cooldown(1, 5, BucketType.user)
    async def roast(self, ctx: CustomContext, member: discord.Member = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        await ctx.send(f"{member.mention}, {await self.bot.dagpi.roast()}")

    @commands.command(
        help="Sends a random joke")
    async def joke(self, ctx: CustomContext):
        await ctx.send(await self.bot.dagpi.joke())

    @commands.command(
        help="Sends a random yo mama joke",
        aliases=['yomom', 'yo_mama', 'yo-mama', 'yo-mom', 'yo_mom'])
    async def yomama(self, ctx: CustomContext):
        await ctx.send(await self.bot.dagpi.yomama())