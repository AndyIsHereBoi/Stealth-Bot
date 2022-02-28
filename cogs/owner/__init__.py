from .signalpvp import SignalPvP
from .owner import Owner as _Owner

class Owner(_Owner, SignalPvP):
    """Commands only the owner of this bot can use."""

    select_emoji = "<:owner_crown:934156242388144219>"
    select_brief = "Commands only the owner of this bot can use."

    pass


def setup(bot):
    bot.add_cog(Owner(bot))