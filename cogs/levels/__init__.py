from .commands import Commands
from .levelling import Levelling

class Levels(Levelling, Commands):
    """Commands for the levelling system."""

    select_emoji = "<:lightningbolt:903706434791956561>"
    select_brief = "Commands for the levelling system."

    pass


def setup(bot):
    bot.add_cog(Levels(bot))