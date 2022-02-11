from discord.ext import commands

class ModerationBase(commands.Cog):
    def __init__(self, bot):
        self.bot = bot