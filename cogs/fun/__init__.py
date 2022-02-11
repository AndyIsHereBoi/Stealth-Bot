from .anime import Anime
from .api import API
from .other import Other
from .rate import Rate
from .reddit import Reddit
from .text import Text

class Fun(Anime, API, Other, Rate, Reddit, Text):
    """Fun commands like meme, hug and more!"""

    select_emoji = "<:soccer:899621880120639509>"
    select_brief = "Fun commands like meme, hug and more!"

    pass


def setup(bot):
    bot.add_cog(Fun(bot))