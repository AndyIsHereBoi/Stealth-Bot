from .signalpvp import SignalPvP
from .owner import Owner as _Owner

class Owner(_Owner, SignalPvP):
    pass


def setup(bot):
    bot.add_cog(Owner(bot))