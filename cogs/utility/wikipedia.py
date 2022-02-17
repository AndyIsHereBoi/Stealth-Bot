import wikipedia

from ._base import UtilityBase
from discord.ext import commands
from helpers.context import CustomContext

class Wikipedia(UtilityBase):

    @commands.command()
    async def wikipedia(self, ctx: CustomContext, *, query: str):
        try:
            return await ctx.send(wikipedia.summary(query, sentences=3, chars=1000))
        except Exception as e:
            return await ctx.send(e)