from helpers.context import CustomContext

from jishaku.cog import STANDARD_FEATURES, OPTIONAL_FEATURES
from jishaku.features.baseclass import Feature


def setup(bot):
    bot.add_cog(CustomJishaku(bot=bot))


class CustomJishaku(*OPTIONAL_FEATURES, *STANDARD_FEATURES):

    @Feature.Command(name="jishaku", aliases=["jsk"], invoke_without_command=True, ignore_extra=False)
    async def jsk(self, ctx: CustomContext):
        await ctx.send("Hello World!")