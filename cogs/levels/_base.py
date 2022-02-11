from discord.ext import commands

class LevelsBase(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cd_mapping = commands.CooldownMapping.from_cooldown(1, 45, commands.BucketType.member)