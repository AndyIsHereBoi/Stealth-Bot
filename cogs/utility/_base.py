from discord.ext import commands

class UtilityBase(commands.Cog):
    def __init__(self, bot):
        self.bot = bot