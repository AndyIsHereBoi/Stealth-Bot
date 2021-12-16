import discord

from discord.ext import commands
from helpers.context import CustomContext


def setup(client):
    client.add_cog(Levels(client))


class Levels(commands.Cog):
    """Levelling system."""

    def __init__(self, client):
        self.client = client
        self.hidden = True
        self.select_emoji = "<:lightningbolt:903706434791956561>"
        self.select_brief = "Levelling system."
