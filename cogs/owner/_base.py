from discord.ext import commands

class OwnerBase(commands.Cog):
    def __init__(self, bot):
        self.bot = bot