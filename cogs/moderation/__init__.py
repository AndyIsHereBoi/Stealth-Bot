class Moderation():
    """Commands useful for staff members of the server."""

    select_emoji = "<:staff:858326975869485077>"
    select_brief = "Commands useful for staff members of the server."

    pass


def setup(bot):
    bot.add_cog(Moderation(bot))