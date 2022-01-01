import random
import typing
import asyncio
import discord
import functools

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

        self.cd_mapping = commands.CooldownMapping.from_cooldown(1, 45, commands.BucketType.member)

    async def level_up(self, user):
        level = user['level']
        xp = user['xp']

        # if xp >= round((4 * (level ** 3)) / 5):
        if xp >= (level - 1) * 300:
            await self.client.db.execute("UPDATE users SET level = $1, xp = $2 WHERE user_id = $3 AND guild_id = $4", level + 1, 0, user['user_id'], user['guild_id'])
            return True

        else:
            return False

    def get_rank_card(self, args):
        image = Generator().generate_profile(**args)
        return image

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return

        if message.author.bot:
            return

        if message.guild.id == 799330949686231050 and message.channel.id != 829418754408317029:
            return

        bucket = self.cd_mapping.get_bucket(message)
        retry_after = bucket.update_rate_limit()

        if retry_after:
            return

        user = await self.client.db.fetch("SELECT * FROM users WHERE user_id = $1 AND guild_id = $2", message.author.id, message.guild.id)

        if not user:
            await self.client.db.execute("INSERT INTO users (user_id, guild_id, level, xp) VALUES ($1, $2, $3, $4)", message.author.id, message.guild.id, 1, 0)

        user = await self.client.db.fetchrow("SELECT * FROM users WHERE user_id = $1 AND guild_id = $2", message.author.id, message.guild.id)
        await self.client.db.execute("UPDATE users SET xp = $1 WHERE user_id = $2 AND guild_id = $3", user['xp'] + random.randint(10, 30), message.author.id, message.guild.id)

        if await self.level_up(user):
            if message.guild.id == 799330949686231050:
                level: int = user['level'] + 1

                await message.reply(f"You've levelled up! You are now level **{user['level'] + 1}**")

    @commands.command(
        help="Shows the specified member's rank card.",
        aliases=['lvl', 'rank'])
    async def level(self, ctx: CustomContext, member: typing.Optional[discord.Member] = None) -> discord.Message:
        await ctx.trigger_typing()

        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        user = await self.client.db.fetchrow("SELECT * FROM users WHERE user_id = $1 AND guild_id = $2",
                                          member.id, ctx.guild.id)

        if not user:
            return await ctx.send(f"{'You' if member.id == ctx.author.id else f'{member.display_name}'} doesn't have a level")

        args = {
            'bg_image': 'https://media.discordapp.net/attachments/820049182860509206/923974515623604224/Untitled48_20211224102440.png?width=1193&height=671',  # Background image link
            'profile_image': str(member.avatar.replace(format='png', size=2048).url),  # User profile picture link
            'level': user['level'],  # User current level
            'current_xp': 0,  # Current level minimum xp
            'user_xp': user['xp'],  # User current xp
            'next_xp': 300 * user['level'],  # xp required for next level
            'user_position': 0,  # User position in leaderboard
            'user_name': str(member),  # username with descriminator
            'user_status': member.status.name,  # User status eg. online, offline, idle, streaming, dnd
        }

        image = await asyncio.get_event_loop().run_in_executor(None, functools.partial(self.get_rank_card, args))

        embed = discord.Embed(title=f"{'Your' if member.id == ctx.author.id else f'{member.display_name}s'} rank card")
        embed.set_image(url=f"attachment://rank.png")

        return await ctx.send(embed=embed, file=discord.File(fp=image, filename="rank.png"))

    @commands.command(
        help="Shows the level leaderboard for the server.",
        aliases=['lb'])
    async def leaderboard(self, ctx: CustomContext) -> discord.Message:
        records = await self.client.db.fetch("SELECT * FROM users WHERE guild_id = $1 ORDER BY level DESC LIMIT 10",
                                            ctx.guild.id)

        users = []
        levels = []
        nl = "\n"

        for record in records:
            user = ctx.guild.get_member(record['user_id'])
            users.append(f"{user.mention}")
            levels.append(f"{record['level']} ({record['xp']} XP)")

        embed = discord.Embed(title=f"{ctx.guild.name}'s level leaderboard")
        embed.add_field(name=f"User", value=f"{nl.join(users)}", inline=True)
        embed.add_field(name=f"Level", value=f"{nl.join(levels)}", inline=True)
        return await ctx.send(embed=embed)
