from .images import Images
from .jeyy import Jeyy

class Images(Images, Jeyy):
    """Commands that manipulate/send images."""

    select_emoji = "<:frame_photo:899621559520595968>"
    select_brief = "Commands that manipulate/send images."

    pass


def setup(bot):
    bot.add_cog(Images(bot))