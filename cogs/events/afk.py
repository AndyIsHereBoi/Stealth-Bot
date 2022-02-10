import random
import discord

from helpers import helpers
from ._base import EventsBase
from discord.ext import commands

class Afk(EventsBase):
    
    @commands.Cog.listener('on_message')
    async def on_afk_user_message(self, message: discord.Message):
        if message.author.bot:
            return

        if not message.guild:
            return

        if message.author.id in self.bot.afk_users:
            try:
                if self.bot.auto_un_afk[message.author.id] is False:
                    return
            except KeyError:
                pass

            self.bot.afk_users.pop(message.author.id)

            info = await self.bot.db.fetchrow("SELECT * FROM afk WHERE user_id = $1", message.author.id)
            await self.bot.db.execute("INSERT INTO afk (user_id, start_time, reason) VALUES ($1, null, null) "
                                      "ON CONFLICT (user_id) DO UPDATE SET start_time = null, reason = null",
                                      message.author.id)

            colors = [0x910023, 0xA523FF]
            color = random.choice(colors)

            time = info["start_time"]

            delta_uptime = message.created_at - time
            hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            days, hours = divmod(hours, 24)

            embed = discord.Embed(title=f"👋 Welcome back {message.author.name}!", description=f"""
You've been AFK for {self.time(days=days, hours=hours, minutes=minutes, seconds=seconds)}
With the reason being: {info['reason']}
                                    """, timestamp=discord.utils.utcnow(), color=color)

            await message.channel.send(embed=embed, delete_after=35)

            await message.add_reaction("👋")

    @commands.Cog.listener('on_message')
    async def on_afk_user_mention(self, message: discord.Message):
        if not message.guild:
            return

        if message.author == self.bot.user:
            return

        if message.mentions:
            pinged_afk_user_ids = list(set([u.id for u in message.mentions]).intersection(self.bot.afk_users))
            afkUsers = []
            for user_id in pinged_afk_user_ids:
                member = message.guild.get_member(user_id)
                if member and member.id != message.author.id:
                    info = await self.bot.db.fetchrow("SELECT * FROM afk WHERE user_id = $1", user_id)

                    time = info["start_time"]

                    delta_uptime = message.created_at - time
                    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    days, hours = divmod(hours, 24)

                    afkUsers.append(
                        f"Hey {message.author.mention}, it looks like {member.mention} has been AFK for {helpers.human_timedelta(info['start_time'])}.\nWith the reason being: {info['reason']}\n")

            if afkUsers:
                afkUsers = "\n".join(afkUsers)
                await message.reply(f"{afkUsers}", delete_after=35)

            else:
                return