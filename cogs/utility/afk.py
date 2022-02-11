import discord

from ._base import UtilityBase
from discord.ext import commands
from helpers.context import CustomContext

class AFK(UtilityBase):

    @commands.command(
        help="Makes you go AFK. If someone pings you the bot will tell them that you're AFK.")
    async def afk(self, ctx: CustomContext, *, reason="No reason provided"):
        if ctx.author.id in self.bot.afk_users and ctx.author.id in self.bot.auto_un_afk and \
                self.bot.auto_un_afk[ctx.author.id] is True:
            return

        if ctx.author.id not in self.bot.afk_users:
            await self.bot.db.execute(
                "INSERT INTO afk (user_id, start_time, reason) VALUES ($1, $2, $3) ON CONFLICT (user_id) DO UPDATE SET start_time = $2, reason = $3",
                ctx.author.id, ctx.message.created_at, reason[0:1800])
            self.bot.afk_users[ctx.author.id] = True

            embed = discord.Embed(title=f"<:idle:872784075591675904>{ctx.author.name} is now AFK",
                                  description=f"With the reason being: {reason}")

            await ctx.send(embed=embed)

        else:
            self.bot.afk_users.pop(ctx.author.id)

            info = await self.bot.db.fetchrow("SELECT * FROM afk WHERE user_id = $1", ctx.author.id)
            await self.bot.db.execute(
                "INSERT INTO afk (user_id, start_time, reason) VALUES ($1, null, null) ON CONFLICT (user_id) DO UPDATE SET start_time = null, reason = null",
                ctx.author.id)

            start_time = info["start_time"]

            delta_uptime = ctx.message.created_at - start_time
            hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            days, hours = divmod(hours, 24)

            embed = discord.Embed(title=f"👋 Welcome back {ctx.author.name}!", description=f"""
    You've been AFK for {ctx.time(days=int(days), hours=int(hours), minutes=int(minutes), seconds=int(seconds))}.
    With the reason being: {info['reason']}""")

            await ctx.send(embed=embed)

            await ctx.message.add_reaction("👋")

    @commands.command(
        help="Toggles if the bot should remove your AFK status after you send a message or not",
        aliases=['auto_un_afk', 'aafk', 'auto-afk-remove'])
    async def autoafk(self, ctx: CustomContext, mode: bool = None):
        mode = mode or (False if (ctx.author.id in self.bot.auto_un_afk and self.bot.auto_un_afk[
            ctx.author.id] is True) or ctx.author.id not in self.bot.auto_un_afk else True)
        self.bot.auto_un_afk[ctx.author.id] = mode

        await self.bot.db.execute("INSERT INTO afk (user_id, auto_un_afk) VALUES ($1, $2) "
                                     "ON CONFLICT (user_id) DO UPDATE SET auto_un_afk = $2", ctx.author.id, mode)

        text = f'{"Enabled" if mode is True else "Disabled"}'

        embed = discord.Embed(title=f"{ctx.toggle(mode)} {text} automatic AFK removal",
                              description="To remove your AFK status do `afk` again.")

        return await ctx.send(embed=embed)