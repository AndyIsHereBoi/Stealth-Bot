import random

from ._base import LevelsBase
from discord.ext import commands

class Levelling(LevelsBase):
    
    async def level_up(self, user):
        level = user['level']
        xp = user['xp']

        if xp >= (level - 1) * 300:
            await self.bot.db.execute("UPDATE users SET level = $1, xp = $2 WHERE user_id = $3 AND guild_id = $4", level + 1, 0, user['user_id'], user['guild_id'])
            return True

        else:
            return False

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

        user = await self.bot.db.fetch("SELECT * FROM users WHERE user_id = $1 AND guild_id = $2", message.author.id, message.guild.id)

        if not user:
            await self.bot.db.execute("INSERT INTO users (user_id, guild_id, level, xp) VALUES ($1, $2, $3, $4)", message.author.id, message.guild.id, 1, 0)

        user = await self.bot.db.fetchrow("SELECT * FROM users WHERE user_id = $1 AND guild_id = $2", message.author.id, message.guild.id)

        amount = random.randint(10, 30)

        if len(message.content) >= 55:
            amount += random.randint(10, 15)

        await self.bot.db.execute("UPDATE users SET xp = $1 WHERE user_id = $2 AND guild_id = $3", user['xp'] + amount, message.author.id, message.guild.id)

        if await self.level_up(user):
            if message.guild.id == 799330949686231050:
                level: int = user['level'] + 1

                await message.reply(f"You've levelled up! You are now level **{user['level'] + 1}**")