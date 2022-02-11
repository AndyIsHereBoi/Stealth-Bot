import typing
import asyncio
import discord
import functools

from ._base import LevelsBase
from discord.ext import commands
from disrank.generator import Generator
from helpers.context import CustomContext

class Commands(LevelsBase):

    def get_rank_card(self, args):
        image = Generator().generate_profile(**args)
        return image

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

        user = await self.bot.db.fetchrow("SELECT * FROM users WHERE user_id = $1 AND guild_id = $2",
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
            'user_name': str(member), # username with discriminator
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
        records = await self.bot.db.fetch("SELECT * FROM users WHERE guild_id = $1 ORDER BY level DESC LIMIT 10",
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
