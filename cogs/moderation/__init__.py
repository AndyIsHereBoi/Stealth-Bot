from .announce import Announce
from .basic import Basic
from .mute import Mute
from .other import Other
from .remove import Remove
from .role import Role
from .voice import Voice

class Moderation(Announce, Basic, Mute, Other, Remove, Role, Voice):
    """Commands useful for staff members of the server."""

    select_emoji = "<:staff:858326975869485077>"
    select_brief = "Commands useful for staff members of the server."

    pass


def setup(bot):
    bot.add_cog(Moderation(bot))