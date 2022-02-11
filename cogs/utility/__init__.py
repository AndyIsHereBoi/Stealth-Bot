from .afk import AFK
from .bot import Bot
from .info import Info
from .list import _List
from .misc import Misc
from .rtfm import RTFM
from .todo import Todo


class Utility(AFK, Bot, Info, _List, Misc, RTFM, Todo):
    pass


def setup(bot):
    bot.add_cog(Utility(bot))