import asyncio
import discord

from discord.ext import commands
from disrank.generator import Generator
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

    @commands.command(
        help="")
    async def level(self, ctx: CustomContext) -> discord.Message:
        await ctx.trigger_typing()
        await asyncio.sleep(2)

        user = await self.client.db.fetchrow("SELECT * FROM users WHERE user_id = $1 AND guild_id = $2",
                                          ctx.author.id, ctx.guild.id)

        if not user:
            return await ctx.send("You don't have a level!")

        args = {
            'bg_image': 'https://media.discordapp.net/attachments/820049182860509206/923974515623604224/Untitled48_20211224102440.png?width=1193&height=671',  # Background image link
            'profile_image': str(ctx.author.avatar.replace(format='png', size=2048).url),  # User profile picture link
            'level': user['level'],  # User current level
            'current_xp': 0,  # Current level minimum xp
            'user_xp': user['xp'],  # User current xp
            'next_xp': round((4 * (user['level'] ** 3)) / 5),  # xp required for next level
            'user_position': 1,  # User position in leaderboard
            'user_name': str(ctx.author),  # username with descriminator
            'user_status': ctx.author.status.name,  # User status eg. online, offline, idle, streaming, dnd
        }

        image = Generator().generate_profile(**args)

        return await ctx.send(file=discord.File(fp=image, filename="rank.png"))