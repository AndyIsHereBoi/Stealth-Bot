import discord

from ._base import EventsBase
from discord.ext import commands

class JoinLeave(EventsBase):

    @commands.Cog.listener("on_guild_join")
    async def thank_for_adding_bot(self, guild: discord.Guild):
        channel = discord.utils.get(guild.text_channels, name='general')

        if not channel:
            channels = [channel for channel in guild.text_channels if channel.permissions_for(guild.me).send_messages]
            channel = channels[0]

        if len([m for m in guild.members if m.bot]) > len([m for m in guild.members if not m.bot]):
            fuckoffEmbed = discord.Embed(title="Fuck off!", description=f"""
I have detected that this server has a bot count higher than the human count.
So I will kindly have to say, fuck off and leave.
            """)

        welcomeEmbed = discord.Embed(title="Thank you for adding `Stealth Bot` to your server", description="""
We really appreciate you adding `Stealth Bot` to your server.
You can do `sb!help` to view a list of commands.
To add a prefix simply do `sb!prefix add <prefix>`.
                            """, timestamp=discord.utils.utcnow(), color=0x2F3136)
        welcomeEmbed.set_thumbnail(url=self.bot.user.avatar.url)

        await channel.send(embed=welcomeEmbed)

    @commands.Cog.listener("on_guild_join")
    async def private_log_on_guild_join(self, guild: discord.Guild):
        await self.bot.db.execute("DELETE FROM guilds WHERE guild_id = $1", guild.id)

        embed = discord.Embed(title="New guild!", description=f"""
**Guild name:** {guild.name}
**Guild owner:** {guild.owner}
**Guild ID:** {guild.id}

{len(guild.members):,} members ({len([m for m in guild.members if m.bot]):,} bots {len([m for m in guild.members if not m.bot]):,} humans)
{len(guild.text_channels):,} text channels
{len(guild.voice_channels):,} voice channels
                                """, color=discord.Color.green())
        embed.set_footer(text=f"I am now in {len(self.bot.guilds)} guilds", icon_url=self.bot.user.avatar.url)

        if guild.icon:
            embed.set_thumbnail(url=f"{guild.icon}")

        channel = self.bot.get_channel(914145032406196245)
        await channel.send(embed=embed)

    @commands.Cog.listener("on_guild_remove")
    async def private_log_on_guild_remove(self, guild: discord.Guild):
        await self.bot.db.execute("DELETE FROM guilds WHERE guild_id = $1", guild.id)

        embed = discord.Embed(title="Left guild!", description=f"""
**Guild name:** {guild.name}
**Guild owner:** {guild.owner}
**Guild ID:** {guild.id}

{len(guild.members):,} members ({len([m for m in guild.members if m.bot]):,} bots {len([m for m in guild.members if not m.bot]):,} humans)
{len(guild.text_channels):,} text channels
{len(guild.voice_channels):,} voice channels
                                """, color=discord.Color.red())
        embed.set_footer(text=f"I am now in {len(self.bot.guilds)} guilds", icon_url=self.bot.user.avatar.url)

        if guild.icon:
            embed.set_thumbnail(url=f"{guild.icon}")

        channel = self.bot.get_channel(914145032406196245)
        await channel.send(embed=embed)