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

    async def level_up(self, user):
        level = user['level']
        xp = user['xp']

        if xp >= round((4 * (level ** 3)) / 5):
            await self.client.db.execute("UPDATE users SET level = $1 WHERE user_id = $2 AND guild_id = $3", level + 1, user['user_id'], user['guild_id'])
            return True

        else:
            return False

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return

        if message.author.bot:
            return

        if message.channel.id == 923959775794978826:
            user = await self.client.db.fetch("SELECT * FROM users WHERE user_id = $1 AND guild_id = $2", message.author.id, message.guild.id)

            if not user:
                await self.client.db.execute("INSERT INTO users (user_id, guild_id, level, xp) VALUES ($1, $2, $3, $4)", message.author.id, message.guild.id, 1, 0)

            user = await self.client.db.fetchrow("SELECT * FROM users WHERE user_id = $1 AND guild_id = $2", message.author.id, message.guild.id)
            await self.client.db.execute("UPDATE users SET xp = $1 WHERE user_id = $2 AND guild_id = $3", user['xp'] + 1, message.author.id, message.guild.id)

            if await self.level_up(user):
                try:
                    await message.reply(f"You've levelled up! You are now level **{user['level'] + 1}**")

                except:
                    await message.channel.send(f"{message.author.mention} has levelled up! They are now level **{user['level'] + 1}**")

        else:
            return

    @commands.command()
    async def level(self, ctx: CustomContext) -> discord.Message:
        user = await self.client.db.fetch("SELECT * FROM users WHERE user_id = $1 AND guild_id = $2",
                                          ctx.author.id, ctx.guild.id)

        if not user:
            return await ctx.send("You don't have a level!")

        level = user['level']
        xp = user['xp']

        embed = discord.Embed(description=f"""
Level: {level}
XP: {xp}/{round((4 * (level ** 3)) / 5)}
        """)

        return await ctx.send(embed=embed)